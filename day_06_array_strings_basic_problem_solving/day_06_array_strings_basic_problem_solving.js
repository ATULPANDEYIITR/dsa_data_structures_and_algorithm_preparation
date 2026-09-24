/*
Day 6 — Arrays, Strings and Basic Problem Solving

A self-contained JavaScript study program covering:
- Array creation, indexing, traversal, mutation and slicing
- String indexing, traversal and manipulation
- Linear searching
- Counting occurrences and frequencies
- Maximum, minimum and sum
- Reversal
- Palindromes
- Duplicate detection
- Character counting
- Second-largest value
- Even/odd counting
- Additional beginner problem-solving patterns
- Edge cases
- Complexity considerations
- 15 mixed practice problems
- Assertions for validation

Run with:
    node day6_arrays_strings.js
*/

// -----------------------------------------------------------------------------
// 1. ARRAY CREATION
// -----------------------------------------------------------------------------

function demonstrateArrayCreation() {
    const emptyArray = [];
    const numbers = [10, 20, 30, 40, 50];
    const repeatedValues = new Array(5).fill(0);
    const mixedValues = [10, "JavaScript", 3.14, true];

    console.log("\n=== ARRAY CREATION ===");
    console.log("Empty array:", emptyArray);
    console.log("Numbers:", numbers);
    console.log("Repeated values:", repeatedValues);
    console.log("Mixed values:", mixedValues);
}

// -----------------------------------------------------------------------------
// 2. ARRAY INDEXING
// -----------------------------------------------------------------------------

function demonstrateArrayIndexing() {
    const numbers = [10, 20, 30, 40, 50];

    console.log("\n=== ARRAY INDEXING ===");
    console.log("Array:", numbers);
    console.log("Index 0:", numbers[0]);
    console.log("Index 2:", numbers[2]);
    console.log("Last element:", numbers[numbers.length - 1]);

    // JavaScript returns undefined for an out-of-range array index instead
    // of throwing an IndexError like Python.
    console.log("Out-of-range index:", numbers[10]);
}

// -----------------------------------------------------------------------------
// 3. ARRAY TRAVERSAL
// -----------------------------------------------------------------------------

function demonstrateArrayTraversal() {
    const numbers = [12, 7, 25, 9, 18];

    console.log("\n=== ARRAY TRAVERSAL ===");

    console.log("Traditional for loop:");
    for (let index = 0; index < numbers.length; index++) {
        console.log(`index=${index}, value=${numbers[index]}`);
    }

    console.log("for...of:");
    for (const number of numbers) {
        process.stdout.write(`${number} `);
    }
    console.log();

    console.log("forEach:");
    numbers.forEach((number, index) => {
        console.log(`index=${index}, value=${number}`);
    });
}

// -----------------------------------------------------------------------------
// 4. ARRAY MUTATION AND SLICING
// -----------------------------------------------------------------------------

function demonstrateArrayMutation() {
    const numbers = [10, 20, 30, 40, 50];

    console.log("\n=== ARRAY MUTATION AND SLICING ===");

    numbers[2] = 35;
    console.log("After replacing index 2:", numbers);

    console.log("First three:", numbers.slice(0, 3));
    console.log("Middle section:", numbers.slice(1, 4));
    console.log("Last two:", numbers.slice(-2));
    console.log("Copy:", numbers.slice());
}

// -----------------------------------------------------------------------------
// 5. BASIC STRING OPERATIONS
// -----------------------------------------------------------------------------

function demonstrateStringBasics() {
    const text = "Algorithm";

    console.log("\n=== STRING BASICS ===");
    console.log("String:", text);
    console.log("First character:", text[0]);
    console.log("Last character:", text[text.length - 1]);
    console.log("Length:", text.length);

    console.log("Characters:");
    for (const character of text) {
        process.stdout.write(`${character} `);
    }
    console.log();

    console.log("First four characters:", text.slice(0, 4));
    console.log("Reversed:", reverseString(text));
    console.log("Uppercase:", text.toUpperCase());
    console.log("Lowercase:", text.toLowerCase());
    console.log("Contains 'g':", text.includes("g"));
}

// -----------------------------------------------------------------------------
// 6. BASIC SEARCHING
// -----------------------------------------------------------------------------

function linearSearch(numbers, target) {
    /*
    Check every element from left to right.

    Time: O(n)
    Extra space: O(1)
    */
    for (let index = 0; index < numbers.length; index++) {
        if (numbers[index] === target) {
            return index;
        }
    }

    return -1;
}

function findAllPositions(numbers, target) {
    const positions = [];

    for (let index = 0; index < numbers.length; index++) {
        if (numbers[index] === target) {
            positions.push(index);
        }
    }

    return positions;
}

// -----------------------------------------------------------------------------
// 7. BASIC COUNTING
// -----------------------------------------------------------------------------

function countOccurrences(numbers, target) {
    let count = 0;

    for (const number of numbers) {
        if (number === target) {
            count++;
        }
    }

    return count;
}

function countCharacters(text) {
    const frequency = new Map();

    for (const character of text) {
        frequency.set(character, (frequency.get(character) ?? 0) + 1);
    }

    return Object.fromEntries(frequency);
}

// -----------------------------------------------------------------------------
// 8. MAXIMUM, MINIMUM AND SUM
// -----------------------------------------------------------------------------

function findMaximum(numbers) {
    if (numbers.length === 0) {
        throw new Error("Cannot find maximum of an empty array.");
    }

    let maximum = numbers[0];

    for (let index = 1; index < numbers.length; index++) {
        if (numbers[index] > maximum) {
            maximum = numbers[index];
        }
    }

    return maximum;
}

function findMinimum(numbers) {
    if (numbers.length === 0) {
        throw new Error("Cannot find minimum of an empty array.");
    }

    let minimum = numbers[0];

    for (let index = 1; index < numbers.length; index++) {
        if (numbers[index] < minimum) {
            minimum = numbers[index];
        }
    }

    return minimum;
}

function calculateSum(numbers) {
    let total = 0;

    for (const number of numbers) {
        total += number;
    }

    return total;
}

function calculateAverage(numbers) {
    if (numbers.length === 0) {
        throw new Error("Cannot calculate average of an empty array.");
    }

    return calculateSum(numbers) / numbers.length;
}

// -----------------------------------------------------------------------------
// 9. REVERSING
// -----------------------------------------------------------------------------

function reverseArrayInPlace(numbers) {
    /*
    Two-pointer technique:
    - left begins at index 0.
    - right begins at the final index.
    - swap and move inward.

    Time: O(n)
    Extra space: O(1)
    */
    let left = 0;
    let right = numbers.length - 1;

    while (left < right) {
        [numbers[left], numbers[right]] = [numbers[right], numbers[left]];
        left++;
        right--;
    }

    return numbers;
}

function reverseString(text) {
    // Strings are immutable, so a new string is constructed.
    const characters = [];

    for (let index = text.length - 1; index >= 0; index--) {
        characters.push(text[index]);
    }

    return characters.join("");
}

// -----------------------------------------------------------------------------
// 10. PALINDROMES
// -----------------------------------------------------------------------------

function isPalindrome(text) {
    /*
    Normalize by keeping only letters and digits.
    Then compare symmetrical positions using two pointers.
    */
    const normalized = text
        .toLowerCase()
        .split("")
        .filter(character => /[a-z0-9]/.test(character));

    let left = 0;
    let right = normalized.length - 1;

    while (left < right) {
        if (normalized[left] !== normalized[right]) {
            return false;
        }

        left++;
        right--;
    }

    return true;
}

// -----------------------------------------------------------------------------
// 11. DUPLICATES
// -----------------------------------------------------------------------------

function findDuplicateValues(numbers) {
    const seen = new Set();
    const duplicates = new Set();

    for (const number of numbers) {
        if (seen.has(number)) {
            duplicates.add(number);
        } else {
            seen.add(number);
        }
    }

    return [...duplicates].sort((a, b) => a - b);
}

function findFirstDuplicate(numbers) {
    const seen = new Set();

    for (const number of numbers) {
        if (seen.has(number)) {
            return number;
        }

        seen.add(number);
    }

    return null;
}

// -----------------------------------------------------------------------------
// 12. SECOND-LARGEST VALUE
// -----------------------------------------------------------------------------

function findSecondLargest(numbers) {
    if (numbers.length < 2) {
        throw new Error("At least two values are required.");
    }

    let largest = null;
    let secondLargest = null;

    for (const number of numbers) {
        if (largest === null || number > largest) {
            secondLargest = largest;
            largest = number;
        } else if (
            number !== largest &&
            (secondLargest === null || number > secondLargest)
        ) {
            secondLargest = number;
        }
    }

    if (secondLargest === null) {
        throw new Error("At least two distinct values are required.");
    }

    return secondLargest;
}

// -----------------------------------------------------------------------------
// 13. EVEN AND ODD COUNTING
// -----------------------------------------------------------------------------

function countEvenAndOdd(numbers) {
    let evenCount = 0;
    let oddCount = 0;

    for (const number of numbers) {
        if (number % 2 === 0) {
            evenCount++;
        } else {
            oddCount++;
        }
    }

    return { evenCount, oddCount };
}

// -----------------------------------------------------------------------------
// 14. ADDITIONAL ARRAY PROBLEMS
// -----------------------------------------------------------------------------

function countPositiveNegativeZero(numbers) {
    let positive = 0;
    let negative = 0;
    let zero = 0;

    for (const number of numbers) {
        if (number > 0) {
            positive++;
        } else if (number < 0) {
            negative++;
        } else {
            zero++;
        }
    }

    return { positive, negative, zero };
}

function removeDuplicatesPreservingOrder(numbers) {
    const seen = new Set();
    const result = [];

    for (const number of numbers) {
        if (!seen.has(number)) {
            seen.add(number);
            result.push(number);
        }
    }

    return result;
}

function findCommonValues(first, second) {
    const secondSet = new Set(second);
    const common = new Set();

    for (const value of first) {
        if (secondSet.has(value)) {
            common.add(value);
        }
    }

    return [...common].sort((a, b) => a - b);
}

function moveZerosToEnd(numbers) {
    /*
    Rewrite non-zero values at the front.
    Fill the remaining positions with zero.

    This avoids repeated splice operations that could lead to
    unnecessary element shifting.
    */
    let writePosition = 0;

    for (const value of numbers) {
        if (value !== 0) {
            numbers[writePosition] = value;
            writePosition++;
        }
    }

    while (writePosition < numbers.length) {
        numbers[writePosition] = 0;
        writePosition++;
    }

    return numbers;
}

function isSortedAscending(numbers) {
    for (let index = 1; index < numbers.length; index++) {
        if (numbers[index] < numbers[index - 1]) {
            return false;
        }
    }

    return true;
}

function findMissingValue(numbers, maximumValue) {
    const expected = maximumValue * (maximumValue + 1) / 2;
    const actual = calculateSum(numbers);

    return expected - actual;
}

// -----------------------------------------------------------------------------
// 15. ADDITIONAL STRING PROBLEMS
// -----------------------------------------------------------------------------

function countVowelsAndConsonants(text) {
    const vowels = new Set(["a", "e", "i", "o", "u"]);
    let vowelCount = 0;
    let consonantCount = 0;

    for (const character of text.toLowerCase()) {
        if (/[a-z]/.test(character)) {
            if (vowels.has(character)) {
                vowelCount++;
            } else {
                consonantCount++;
            }
        }
    }

    return { vowelCount, consonantCount };
}

function firstNonRepeatingCharacter(text) {
    const frequency = new Map();

    for (const character of text) {
        frequency.set(character, (frequency.get(character) ?? 0) + 1);
    }

    for (const character of text) {
        if (frequency.get(character) === 1) {
            return character;
        }
    }

    return null;
}

function areAnagrams(first, second) {
    const normalize = text =>
        text.toLowerCase().replace(/\s/g, "");

    const firstFrequency = countCharacters(normalize(first));
    const secondFrequency = countCharacters(normalize(second));

    return JSON.stringify(
        Object.entries(firstFrequency).sort()
    ) === JSON.stringify(
        Object.entries(secondFrequency).sort()
    );
}

function reverseWords(sentence) {
    return sentence.trim().split(/\s+/).reverse().join(" ");
}

function findLongestWord(sentence) {
    const words = sentence.trim().split(/\s+/);

    if (words.length === 1 && words[0] === "") {
        return "";
    }

    let longest = words[0];

    for (const word of words.slice(1)) {
        if (word.length > longest.length) {
            longest = word;
        }
    }

    return longest;
}

// -----------------------------------------------------------------------------
// 16. 15 MIXED PRACTICE PROBLEMS
// -----------------------------------------------------------------------------

function problem01Sum(numbers) {
    return calculateSum(numbers);
}

function problem02Maximum(numbers) {
    return findMaximum(numbers);
}

function problem03Minimum(numbers) {
    return findMinimum(numbers);
}

function problem04CountTarget(numbers, target) {
    return countOccurrences(numbers, target);
}

function problem05ReverseArray(numbers) {
    return reverseArrayInPlace([...numbers]);
}

function problem06ReverseString(text) {
    return reverseString(text);
}

function problem07Palindrome(text) {
    return isPalindrome(text);
}

function problem08Duplicates(numbers) {
    return findDuplicateValues(numbers);
}

function problem09CharacterCount(text) {
    return countCharacters(text);
}

function problem10SecondLargest(numbers) {
    return findSecondLargest(numbers);
}

function problem11EvenOdd(numbers) {
    return countEvenAndOdd(numbers);
}

function problem12FirstNonRepeating(text) {
    return firstNonRepeatingCharacter(text);
}

function problem13Anagram(first, second) {
    return areAnagrams(first, second);
}

function problem14MoveZeros(numbers) {
    return moveZerosToEnd([...numbers]);
}

function problem15MissingValue(numbers, maximumValue) {
    return findMissingValue(numbers, maximumValue);
}

function runMixedPractice() {
    console.log("\n=== 15 MIXED BEGINNER PROBLEMS ===");

    const sampleNumbers = [8, 3, 5, 3, 10, 2, 8, 6];
    const sampleText = "programming";

    const results = [
        ["1. Array sum", problem01Sum(sampleNumbers)],
        ["2. Maximum", problem02Maximum(sampleNumbers)],
        ["3. Minimum", problem03Minimum(sampleNumbers)],
        ["4. Count 3", problem04CountTarget(sampleNumbers, 3)],
        ["5. Reverse array", problem05ReverseArray(sampleNumbers)],
        ["6. Reverse string", problem06ReverseString(sampleText)],
        ["7. Palindrome", problem07Palindrome("Never odd or even")],
        ["8. Duplicates", problem08Duplicates(sampleNumbers)],
        ["9. Character count", problem09CharacterCount("banana")],
        ["10. Second largest", problem10SecondLargest(sampleNumbers)],
        ["11. Even and odd", problem11EvenOdd(sampleNumbers)],
        ["12. First non-repeating", problem12FirstNonRepeating("swiss")],
        ["13. Anagram", problem13Anagram("listen", "silent")],
        ["14. Move zeros", problem14MoveZeros([0, 1, 0, 3, 12])],
        ["15. Missing value", problem15MissingValue([0, 1, 2, 4, 5], 5)]
    ];

    for (const [name, result] of results) {
        console.log(`${name}:`, result);
    }
}

// -----------------------------------------------------------------------------
// 17. EDGE CASES
// -----------------------------------------------------------------------------

function demonstrateEdgeCases() {
    console.log("\n=== EDGE CASES ===");

    const cases = [
        ["empty array", []],
        ["one element", [42]],
        ["negative values", [-10, -5, -20]],
        ["all equal", [7, 7, 7]],
        ["zeros", [0, 0, 0]],
        ["empty string", ""],
        ["one character", "a"],
        ["spaces", "   "]
    ];

    for (const [description, value] of cases) {
        console.log(`${description}:`, value);
    }

    try {
        findMaximum([]);
    } catch (error) {
        console.log("Empty maximum handled:", error.message);
    }

    try {
        findSecondLargest([5, 5, 5]);
    } catch (error) {
        console.log("No distinct second largest handled:", error.message);
    }

    console.log("Empty string palindrome:", isPalindrome(""));
    console.log("One-character palindrome:", isPalindrome("x"));
}

// -----------------------------------------------------------------------------
// 18. COMPLEXITY REFERENCE
// -----------------------------------------------------------------------------

function printComplexityReference() {
    console.log("\n=== COMPLEXITY REFERENCE ===");

    const notes = [
        ["Array traversal", "O(n)", "O(1)"],
        ["Linear search", "O(n)", "O(1)"],
        ["Count occurrences", "O(n)", "O(1)"],
        ["Maximum/minimum", "O(n)", "O(1)"],
        ["Two-pointer reversal", "O(n)", "O(1)"],
        ["Character frequency", "O(n)", "O(k)"],
        ["Duplicate detection with Set", "O(n) average", "O(n)"],
        ["Naive duplicate search", "O(n²)", "O(1)"],
        ["Palindrome normalization", "O(n)", "O(n)"]
    ];

    for (const [operation, time, space] of notes) {
        console.log(
            `${operation.padEnd(34)} Time: ${time.padEnd(12)} Space: ${space}`
        );
    }
}

// -----------------------------------------------------------------------------
// 19. TEST SUITE
// -----------------------------------------------------------------------------

function assertEqual(actual, expected, message) {
    if (JSON.stringify(actual) !== JSON.stringify(expected)) {
        throw new Error(
            `${message}\nExpected: ${JSON.stringify(expected)}\nActual: ${JSON.stringify(actual)}`
        );
    }
}

function runTests() {
    console.log("\n=== TEST SUITE ===");

    const numbers = [4, 2, 9, 2, 7];

    assertEqual(findMaximum(numbers), 9, "Maximum failed");
    assertEqual(findMinimum(numbers), 2, "Minimum failed");
    assertEqual(calculateSum(numbers), 24, "Sum failed");
    assertEqual(calculateAverage(numbers), 4.8, "Average failed");
    assertEqual(linearSearch(numbers, 9), 2, "Search failed");
    assertEqual(linearSearch(numbers, 100), -1, "Missing search failed");
    assertEqual(countOccurrences(numbers, 2), 2, "Count failed");
    assertEqual(findAllPositions(numbers, 2), [1, 3], "Positions failed");

    assertEqual(
        reverseArrayInPlace([...numbers]),
        [7, 2, 9, 2, 4],
        "Array reversal failed"
    );

    assertEqual(reverseString("hello"), "olleh", "String reversal failed");
    assertEqual(isPalindrome("racecar"), true, "Palindrome failed");
    assertEqual(isPalindrome("python"), false, "Non-palindrome failed");

    assertEqual(findDuplicateValues(numbers), [2], "Duplicates failed");
    assertEqual(findFirstDuplicate(numbers), 2, "First duplicate failed");
    assertEqual(
        findSecondLargest(numbers),
        7,
        "Second largest failed"
    );

    assertEqual(
        countEvenAndOdd([1, 2, 3, 4, 6]),
        { evenCount: 3, oddCount: 2 },
        "Even/odd count failed"
    );

    assertEqual(
        countCharacters("aabbc"),
        { a: 2, b: 2, c: 1 },
        "Character count failed"
    );

    assertEqual(
        firstNonRepeatingCharacter("swiss"),
        "w",
        "First non-repeating failed"
    );

    assertEqual(areAnagrams("listen", "silent"), true, "Anagram failed");
    assertEqual(
        reverseWords("one two three"),
        "three two one",
        "Word reversal failed"
    );

    assertEqual(
        removeDuplicatesPreservingOrder([3, 1, 3, 2, 1]),
        [3, 1, 2],
        "Duplicate removal failed"
    );

    assertEqual(
        findCommonValues([1, 2, 3, 4], [3, 4, 5]),
        [3, 4],
        "Common values failed"
    );

    assertEqual(
        moveZerosToEnd([0, 1, 0, 3, 12]),
        [1, 3, 12, 0, 0],
        "Zero movement failed"
    );

    assertEqual(
        isSortedAscending([1, 2, 2, 5]),
        true,
        "Sorted check failed"
    );

    assertEqual(
        findMissingValue([0, 1, 2, 4], 4),
        3,
        "Missing value failed"
    );

    console.log("All tests passed.");
}

// -----------------------------------------------------------------------------
// 20. MAIN
// -----------------------------------------------------------------------------

function main() {
    console.log("=".repeat(72));
    console.log("DAY 6 — ARRAYS, STRINGS AND BASIC PROBLEM SOLVING");
    console.log("=".repeat(72));

    demonstrateArrayCreation();
    demonstrateArrayIndexing();
    demonstrateArrayTraversal();
    demonstrateArrayMutation();

    demonstrateStringBasics();

    console.log("\n=== BASIC SEARCHING ===");
    const searchNumbers = [5, 9, 2, 9, 7, 9];
    console.log("Array:", searchNumbers);
    console.log("Search for 7:", linearSearch(searchNumbers, 7));
    console.log("Search for 100:", linearSearch(searchNumbers, 100));
    console.log("Positions of 9:", findAllPositions(searchNumbers, 9));

    console.log("\n=== BASIC COUNTING ===");
    console.log("Occurrences of 9:", countOccurrences(searchNumbers, 9));
    console.log("Character frequencies:", countCharacters("data structures"));

    console.log("\n=== MAXIMUM, MINIMUM, SUM AND AVERAGE ===");
    const statisticsNumbers = [12, 4, 18, 7, 25, 3];
    console.log("Array:", statisticsNumbers);
    console.log("Maximum:", findMaximum(statisticsNumbers));
    console.log("Minimum:", findMinimum(statisticsNumbers));
    console.log("Sum:", calculateSum(statisticsNumbers));
    console.log("Average:", calculateAverage(statisticsNumbers));

    console.log("\n=== REVERSAL ===");
    const reverseNumbers = [1, 2, 3, 4, 5];
    console.log("Original:", reverseNumbers);
    console.log("Reversed:", reverseArrayInPlace(reverseNumbers));
    console.log("Reversed string:", reverseString("algorithm"));

    console.log("\n=== PALINDROMES ===");
    console.log("'racecar':", isPalindrome("racecar"));
    console.log("'hello':", isPalindrome("hello"));
    console.log(
        "'A man, a plan, a canal: Panama':",
        isPalindrome("A man, a plan, a canal: Panama")
    );

    console.log("\n=== DUPLICATES ===");
    const duplicateNumbers = [4, 7, 4, 2, 7, 7, 9];
    console.log("Array:", duplicateNumbers);
    console.log("Duplicates:", findDuplicateValues(duplicateNumbers));
    console.log("First duplicate:", findFirstDuplicate(duplicateNumbers));

    console.log("\n=== SECOND LARGEST ===");
    console.log(
        "Second distinct-largest:",
        findSecondLargest([10, 20, 20, 5, 15])
    );

    console.log("\n=== EVEN AND ODD ===");
    console.log(
        countEvenAndOdd([1, 2, 3, 4, 5, 6])
    );

    console.log("\n=== ADDITIONAL PROBLEM SOLVING ===");
    console.log(
        "Positive/negative/zero:",
        countPositiveNegativeZero([-2, 0, 5, -1, 0, 8])
    );
    console.log(
        "Remove duplicates:",
        removeDuplicatesPreservingOrder([4, 2, 4, 1, 2, 3])
    );
    console.log(
        "Common values:",
        findCommonValues([1, 2, 3, 4], [3, 4, 5, 6])
    );
    console.log(
        "Move zeros:",
        moveZerosToEnd([0, 4, 0, 5, 2, 0, 8])
    );
    console.log(
        "Sorted:",
        isSortedAscending([1, 2, 2, 4])
    );
    console.log(
        "Missing value:",
        findMissingValue([0, 1, 2, 4], 4)
    );

    console.log("\n=== STRING PROBLEM SOLVING ===");
    console.log(
        "Vowels/consonants:",
        countVowelsAndConsonants("Data Structures")
    );
    console.log(
        "First non-repeating:",
        firstNonRepeatingCharacter("swiss")
    );
    console.log(
        "Anagram:",
        areAnagrams("Dormitory", "Dirty room")
    );
    console.log(
        "Reverse words:",
        reverseWords("arrays strings problem solving")
    );
    console.log(
        "Longest word:",
        findLongestWord("arrays make data processing practical")
    );

    demonstrateEdgeCases();
    printComplexityReference();
    runMixedPractice();
    runTests();

    console.log("\nStudy program completed.");
}

main();
