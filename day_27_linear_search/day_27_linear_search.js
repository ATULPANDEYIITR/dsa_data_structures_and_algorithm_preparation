/*
 * Day 27 — Linear Search
 * =======================
 *
 * A standalone JavaScript study and executable demonstration of linear search.
 *
 * Topics:
 * - Sequential search
 * - Search conditions
 * - First occurrence
 * - Last occurrence
 * - Duplicate values
 * - Edge cases
 * - Predicate-based searching
 * - Searching objects
 * - Generators and lazy iteration
 * - Sorted-data early exit
 * - Complexity analysis
 * - Performance considerations
 * - Practical case study
 *
 * Run with:
 *   node day27_linear_search.js
 *
 * No external packages are required.
 */

"use strict";

// ============================================================================
// 1. BASIC LINEAR SEARCH
// ============================================================================

function linearSearch(items, target) {
    /*
     * Sequentially inspect each element.
     *
     * The function returns the first matching index.
     * It returns -1 when the target does not exist.
     */
    for (let index = 0; index < items.length; index += 1) {
        if (items[index] === target) {
            return index;
        }
    }

    return -1;
}

function demonstrateBasicSearch() {
    console.log("\n" + "=".repeat(72));
    console.log("1. BASIC LINEAR SEARCH");
    console.log("=".repeat(72));

    const numbers = [17, 4, 9, 23, 11, 8];

    console.log("Data:", numbers);
    console.log("Search for 23:", linearSearch(numbers, 23));
    console.log("Search for 99:", linearSearch(numbers, 99));
}


// ============================================================================
// 2. TRACE EACH COMPARISON
// ============================================================================

function linearSearchWithTrace(items, target) {
    for (let index = 0; index < items.length; index += 1) {
        console.log(
            `  Compare index ${index}:`,
            items[index],
            "===",
            target,
            "?"
        );

        if (items[index] === target) {
            console.log(`  Match found at index ${index}.`);
            return index;
        }
    }

    console.log("  Target was not found.");
    return -1;
}

function demonstrateSequentialProcess() {
    console.log("\n" + "=".repeat(72));
    console.log("2. SEQUENTIAL SEARCH PROCESS");
    console.log("=".repeat(72));

    const values = [31, 12, 44, 7, 25];

    console.log("Searching for 44:");
    linearSearchWithTrace(values, 44);

    console.log("\nSearching for 100:");
    linearSearchWithTrace(values, 100);
}


// ============================================================================
// 3. FIRST OCCURRENCE
// ============================================================================

function firstOccurrence(items, target) {
    for (let index = 0; index < items.length; index += 1) {
        if (items[index] === target) {
            return index;
        }
    }

    return -1;
}

function demonstrateFirstOccurrence() {
    console.log("\n" + "=".repeat(72));
    console.log("3. FIRST OCCURRENCE");
    console.log("=".repeat(72));

    const values = [5, 8, 5, 2, 5, 9, 5];

    console.log("Data:", values);
    console.log("First occurrence of 5:", firstOccurrence(values, 5));
    console.log("First occurrence of 9:", firstOccurrence(values, 9));
    console.log("First occurrence of 100:", firstOccurrence(values, 100));
}


// ============================================================================
// 4. LAST OCCURRENCE
// ============================================================================

function lastOccurrence(items, target) {
    let lastIndex = -1;

    for (let index = 0; index < items.length; index += 1) {
        if (items[index] === target) {
            lastIndex = index;
        }
    }

    return lastIndex;
}

function lastOccurrenceReverse(items, target) {
    /*
     * When random access is available, scanning from the end finds the last
     * occurrence without inspecting elements before that occurrence.
     */
    for (let index = items.length - 1; index >= 0; index -= 1) {
        if (items[index] === target) {
            return index;
        }
    }

    return -1;
}

function demonstrateLastOccurrence() {
    console.log("\n" + "=".repeat(72));
    console.log("4. LAST OCCURRENCE");
    console.log("=".repeat(72));

    const values = [5, 8, 5, 2, 5, 9, 5];

    console.log("Data:", values);
    console.log("Last occurrence using forward scan:", lastOccurrence(values, 5));
    console.log("Last occurrence using reverse scan:", lastOccurrenceReverse(values, 5));
}


// ============================================================================
// 5. ALL OCCURRENCES
// ============================================================================

function allOccurrences(items, target) {
    const positions = [];

    for (let index = 0; index < items.length; index += 1) {
        if (items[index] === target) {
            positions.push(index);
        }
    }

    return positions;
}

function demonstrateAllOccurrences() {
    console.log("\n" + "=".repeat(72));
    console.log("5. ALL OCCURRENCES");
    console.log("=".repeat(72));

    const values = [2, 7, 2, 9, 2, 4, 2];

    console.log("All occurrences of 2:", allOccurrences(values, 2));
    console.log("All occurrences of 10:", allOccurrences(values, 10));
}


// ============================================================================
// 6. SEARCH CONDITIONS
// ============================================================================

function firstIndexWhere(items, condition) {
    for (let index = 0; index < items.length; index += 1) {
        if (condition(items[index], index)) {
            return index;
        }
    }

    return -1;
}

function lastIndexWhere(items, condition) {
    let result = -1;

    for (let index = 0; index < items.length; index += 1) {
        if (condition(items[index], index)) {
            result = index;
        }
    }

    return result;
}

function firstValueWhere(items, condition) {
    const index = firstIndexWhere(items, condition);
    return index === -1 ? undefined : items[index];
}

function demonstrateSearchConditions() {
    console.log("\n" + "=".repeat(72));
    console.log("6. SEARCH CONDITIONS");
    console.log("=".repeat(72));

    const values = [4, 7, 12, 15, 22, 31];

    console.log(
        "First even:",
        firstValueWhere(values, value => value % 2 === 0)
    );

    console.log(
        "First value > 20:",
        firstValueWhere(values, value => value > 20)
    );

    console.log(
        "Last index divisible by 3:",
        lastIndexWhere(values, value => value % 3 === 0)
    );
}


// ============================================================================
// 7. EXISTENCE CHECK
// ============================================================================

function exists(items, target) {
    /*
     * A boolean query does not need an index.
     * The search can stop as soon as the condition succeeds.
     */
    for (const item of items) {
        if (item === target) {
            return true;
        }
    }

    return false;
}

function demonstrateEarlyExit() {
    console.log("\n" + "=".repeat(72));
    console.log("7. EXISTENCE AND EARLY EXIT");
    console.log("=".repeat(72));

    const values = [99, 12, 45, 72, 18, 30];

    console.log("Does 99 exist?", exists(values, 99));
    console.log("Does 30 exist?", exists(values, 30));
    console.log("Does 100 exist?", exists(values, 100));
}


// ============================================================================
// 8. COUNTING MATCHES
// ============================================================================

function countOccurrences(items, target) {
    let count = 0;

    for (const item of items) {
        if (item === target) {
            count += 1;
        }
    }

    return count;
}

function demonstrateCounting() {
    console.log("\n" + "=".repeat(72));
    console.log("8. COUNTING MATCHES");
    console.log("=".repeat(72));

    const values = [4, 4, 1, 9, 4, 7, 4];

    console.log("Count of 4:", countOccurrences(values, 4));
}


// ============================================================================
// 9. SORTED-DATA EARLY EXIT
// ============================================================================

function linearSearchSorted(items, target) {
    /*
     * Sorting enables an early "target cannot occur later" decision.
     *
     * It does NOT change the worst-case complexity from O(n) to O(log n).
     */
    for (let index = 0; index < items.length; index += 1) {
        if (items[index] === target) {
            return index;
        }

        if (items[index] > target) {
            return -1;
        }
    }

    return -1;
}

function demonstrateSortedSearch() {
    console.log("\n" + "=".repeat(72));
    console.log("9. SORTED-DATA LINEAR SEARCH");
    console.log("=".repeat(72));

    const values = [4, 8, 13, 21, 29, 35];

    console.log("Search for 21:", linearSearchSorted(values, 21));
    console.log("Search for 20:", linearSearchSorted(values, 20));
    console.log("Search for 40:", linearSearchSorted(values, 40));
}


// ============================================================================
// 10. BINARY SEARCH FOR COMPARISON
// ============================================================================

function binarySearch(items, target) {
    let left = 0;
    let right = items.length - 1;

    while (left <= right) {
        const middle = left + Math.floor((right - left) / 2);

        if (items[middle] === target) {
            return middle;
        }

        if (items[middle] < target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return -1;
}

function demonstrateComparison() {
    console.log("\n" + "=".repeat(72));
    console.log("10. LINEAR SEARCH VS BINARY SEARCH");
    console.log("=".repeat(72));

    const sortedValues = [3, 8, 12, 17, 24, 31, 45, 51];

    console.log("Linear search:", linearSearch(sortedValues, 24));
    console.log("Binary search:", binarySearch(sortedValues, 24));

    console.log(
        "Binary search requires suitable sorted data; linear search does not."
    );
}


// ============================================================================
// 11. OBJECT SEARCH
// ============================================================================

class Student {
    constructor(studentId, name, score) {
        this.studentId = studentId;
        this.name = name;
        this.score = score;
    }
}

function findStudentById(students, studentId) {
    for (const student of students) {
        if (student.studentId === studentId) {
            return student;
        }
    }

    return undefined;
}

function findFirstStudentAboveScore(students, minimumScore) {
    for (const student of students) {
        if (student.score >= minimumScore) {
            return student;
        }
    }

    return undefined;
}

function demonstrateObjectSearch() {
    console.log("\n" + "=".repeat(72));
    console.log("11. SEARCHING OBJECTS");
    console.log("=".repeat(72));

    const students = [
        new Student(101, "Asha", 84.5),
        new Student(102, "Rahul", 91),
        new Student(103, "Meera", 76.5),
        new Student(104, "Vikram", 88)
    ];

    console.log("Student 103:", findStudentById(students, 103));
    console.log(
        "First student with score >= 90:",
        findFirstStudentAboveScore(students, 90)
    );
}


// ============================================================================
// 12. KEY-BASED SEARCH
// ============================================================================

function findFirstByKey(items, targetKey, keyFunction) {
    for (const item of items) {
        if (keyFunction(item) === targetKey) {
            return item;
        }
    }

    return undefined;
}

function demonstrateKeySearch() {
    console.log("\n" + "=".repeat(72));
    console.log("12. KEY-BASED SEARCH");
    console.log("=".repeat(72));

    const students = [
        new Student(201, "Asha", 89),
        new Student(202, "Rahul", 92),
        new Student(203, "Meera", 86)
    ];

    const result = findFirstByKey(
        students,
        "rahul",
        student => student.name.toLowerCase()
    );

    console.log("Found:", result);
}


// ============================================================================
// 13. GENERATOR SEARCH
// ============================================================================

function* generateNumbers(limit) {
    for (let number = 1; number <= limit; number += 1) {
        yield number;
    }
}

function findFirstInIterable(iterable, condition) {
    for (const item of iterable) {
        if (condition(item)) {
            return item;
        }
    }

    return undefined;
}

function demonstrateGeneratorSearch() {
    console.log("\n" + "=".repeat(72));
    console.log("13. LAZY ITERABLE SEARCH");
    console.log("=".repeat(72));

    const result = findFirstInIterable(
        generateNumbers(100),
        number => number === 73
    );

    console.log("First generated value equal to 73:", result);
}


// ============================================================================
// 14. STRING NORMALIZATION
// ============================================================================

function findEmail(emails, targetEmail) {
    const normalizedTarget = targetEmail.trim().toLowerCase();

    for (const email of emails) {
        if (email.trim().toLowerCase() === normalizedTarget) {
            return email;
        }
    }

    return undefined;
}

function demonstrateStringSearch() {
    console.log("\n" + "=".repeat(72));
    console.log("14. NORMALIZED STRING SEARCH");
    console.log("=".repeat(72));

    const emails = [
        "admin@example.com",
        " Alice@example.com ",
        "support@example.com"
    ];

    console.log(
        findEmail(emails, " alice@EXAMPLE.com ")
    );
}


// ============================================================================
// 15. SEARCH RESULT WITH STATISTICS
// ============================================================================

function searchWithStatistics(items, target) {
    let comparisons = 0;

    for (let index = 0; index < items.length; index += 1) {
        comparisons += 1;

        if (items[index] === target) {
            return {
                found: true,
                index,
                comparisons
            };
        }
    }

    return {
        found: false,
        index: -1,
        comparisons
    };
}

function demonstrateStatistics() {
    console.log("\n" + "=".repeat(72));
    console.log("15. COMPARISON STATISTICS");
    console.log("=".repeat(72));

    const values = [11, 22, 33, 44, 55];

    for (const target of [11, 33, 55, 99]) {
        console.log(target, "->", searchWithStatistics(values, target));
    }
}


// ============================================================================
// 16. SEARCHING A REALISTIC PRODUCT CATALOG
// ============================================================================

class Product {
    constructor(code, name, price, stock) {
        this.code = code;
        this.name = name;
        this.price = price;
        this.stock = stock;
    }
}

function findProductByCode(products, code) {
    for (const product of products) {
        if (product.code === code) {
            return product;
        }
    }

    return undefined;
}

function findFirstInStockProduct(products) {
    for (const product of products) {
        if (product.stock > 0) {
            return product;
        }
    }

    return undefined;
}

function demonstrateProductSearch() {
    console.log("\n" + "=".repeat(72));
    console.log("16. PRODUCT CATALOG CASE");
    console.log("=".repeat(72));

    const products = [
        new Product("P100", "Keyboard", 2499, 0),
        new Product("P101", "Mouse", 899, 12),
        new Product("P102", "Monitor", 14999, 4),
        new Product("P103", "Webcam", 3999, 0)
    ];

    console.log("P102:", findProductByCode(products, "P102"));
    console.log("First in-stock product:", findFirstInStockProduct(products));
}


// ============================================================================
// 17. FILTERING VERSUS FIRST-MATCH SEARCH
// ============================================================================

function firstMatch(items, condition) {
    for (const item of items) {
        if (condition(item)) {
            return item;
        }
    }

    return undefined;
}

function filterMatches(items, condition) {
    const matches = [];

    for (const item of items) {
        if (condition(item)) {
            matches.push(item);
        }
    }

    return matches;
}

function demonstrateFirstVsAll() {
    console.log("\n" + "=".repeat(72));
    console.log("17. FIRST MATCH VS ALL MATCHES");
    console.log("=".repeat(72));

    const scores = [72, 91, 95, 68, 93];

    console.log(
        "First score >= 90:",
        firstMatch(scores, score => score >= 90)
    );

    console.log(
        "All scores >= 90:",
        filterMatches(scores, score => score >= 90)
    );
}


// ============================================================================
// 18. EDGE CASES
// ============================================================================

function demonstrateEdgeCases() {
    console.log("\n" + "=".repeat(72));
    console.log("18. EDGE CASES");
    console.log("=".repeat(72));

    const cases = [
        ["empty", [], 10],
        ["singleton match", [10], 10],
        ["singleton miss", [10], 20],
        ["first position", [10, 20, 30], 10],
        ["middle position", [10, 20, 30], 20],
        ["last position", [10, 20, 30], 30],
        ["duplicates", [7, 7, 7, 7], 7],
        ["negative values", [-5, -3, -1, 2], -3]
    ];

    for (const [description, values, target] of cases) {
        console.log(
            description.padEnd(20),
            "first=",
            firstOccurrence(values, target),
            "last=",
            lastOccurrence(values, target)
        );
    }
}


// ============================================================================
// 19. VALIDATION
// ============================================================================

function validateArray(items) {
    if (!Array.isArray(items)) {
        throw new TypeError("items must be an array");
    }
}

function safeLinearSearch(items, target) {
    validateArray(items);
    return linearSearch(items, target);
}

function demonstrateValidation() {
    console.log("\n" + "=".repeat(72));
    console.log("19. INPUT VALIDATION");
    console.log("=".repeat(72));

    console.log("Valid search:", safeLinearSearch([1, 2, 3], 2));

    try {
        safeLinearSearch("123", 2);
    } catch (error) {
        console.log("Expected validation error:", error.message);
    }
}


// ============================================================================
// 20. JAVASCRIPT EQUALITY EDGE CASES
// ============================================================================

function demonstrateEqualityBehavior() {
    console.log("\n" + "=".repeat(72));
    console.log("20. JAVASCRIPT EQUALITY BEHAVIOR");
    console.log("=".repeat(72));

    /*
     * === avoids coercion.
     *
     * Example:
     *   5 === "5" is false
     *   5 == "5" is true
     *
     * Linear search should use the equality semantics appropriate for the
     * application's data contract.
     */
    console.log("5 === '5':", 5 === "5");
    console.log("5 == '5':", 5 == "5"); // Deliberately shown for comparison.

    console.log(
        "NaN === NaN:",
        NaN === NaN
    );

    /*
     * Object identity matters:
     * two separately created objects with identical fields are not strictly
     * equal because they occupy different object identities.
     */
    console.log(
        "{value: 1} === {value: 1}:",
        { value: 1 } === { value: 1 }
    );
}


// ============================================================================
// 21. OBJECT PROPERTY SEARCH
// ============================================================================

function findUserByUsername(users, username) {
    const normalizedTarget = username.trim().toLowerCase();

    for (const user of users) {
        if (user.username.trim().toLowerCase() === normalizedTarget) {
            return user;
        }
    }

    return undefined;
}

function demonstrateUserSearch() {
    console.log("\n" + "=".repeat(72));
    console.log("21. USER RECORD SEARCH");
    console.log("=".repeat(72));

    const users = [
        { id: 1, username: "admin", role: "administrator" },
        { id: 2, username: "Atul", role: "analyst" },
        { id: 3, username: "guest", role: "viewer" }
    ];

    console.log(
        "User search:",
        findUserByUsername(users, " atul ")
    );
}


// ============================================================================
// 22. PERFORMANCE MEASUREMENT
// ============================================================================

function benchmarkSearch(size, targetIndex) {
    if (!Number.isInteger(size) || size <= 0) {
        throw new RangeError("size must be a positive integer");
    }

    if (!Number.isInteger(targetIndex) ||
        targetIndex < 0 ||
        targetIndex >= size) {
        throw new RangeError("targetIndex must be within the array");
    }

    const values = Array.from({ length: size }, (_, index) => index);
    const target = values[targetIndex];

    const start = process.hrtime.bigint();
    const result = searchWithStatistics(values, target);
    const end = process.hrtime.bigint();

    return {
        result,
        elapsedMilliseconds: Number(end - start) / 1_000_000
    };
}

function demonstratePerformance() {
    console.log("\n" + "=".repeat(72));
    console.log("22. PERFORMANCE MEASUREMENT");
    console.log("=".repeat(72));

    for (const size of [100, 10_000, 100_000]) {
        const measurement = benchmarkSearch(size, size - 1);

        console.log(
            `n=${size.toString().padStart(7)} `,
            `comparisons=${measurement.result.comparisons
                .toString()
                .padStart(7)} `,
            `time=${measurement.elapsedMilliseconds.toFixed(6)} ms`
        );
    }

    console.log(
        "Timing varies by hardware and runtime; comparison count is the"
        + " algorithmically meaningful measure."
    );
}


// ============================================================================
// 23. PRACTICAL EVENT STREAM
// ============================================================================

function findFirstCriticalEvent(events) {
    for (const event of events) {
        if (event.severity.toLowerCase() === "critical") {
            return event;
        }
    }

    return undefined;
}

function demonstrateEventSearch() {
    console.log("\n" + "=".repeat(72));
    console.log("23. EVENT STREAM SEARCH");
    console.log("=".repeat(72));

    const events = [
        { id: 1, type: "LOGIN", severity: "INFO" },
        { id: 2, type: "READ", severity: "LOW" },
        { id: 3, type: "FAILED_LOGIN", severity: "HIGH" },
        { id: 4, type: "DATABASE", severity: "CRITICAL" },
        { id: 5, type: "LOGOUT", severity: "INFO" }
    ];

    console.log(
        "First critical event:",
        findFirstCriticalEvent(events)
    );
}


// ============================================================================
// 24. COMPLEXITY INFORMATION
// ============================================================================

function demonstrateComplexity() {
    console.log("\n" + "=".repeat(72));
    console.log("24. COMPLEXITY");
    console.log("=".repeat(72));

    console.log(`
Let n be the number of elements.

First occurrence:
  Best case:  O(1)
  Worst case: O(n)
  Auxiliary space: O(1)

Last occurrence:
  Forward scan worst case: O(n)
  Reverse scan worst case: O(n)
  Auxiliary space: O(1)

All occurrences:
  Time: O(n)
  Additional output storage: O(k), where k is the number of matches.

Why is the average successful search often about (n + 1) / 2 comparisons?
If every position is equally likely to contain the target, the possible
comparison counts are 1, 2, ..., n. Their arithmetic mean is (n + 1) / 2.

Binary search has O(log n) search time but requires suitable sorted data.
`);
}


// ============================================================================
// 25. SECURITY CONSIDERATIONS
// ============================================================================

function demonstrateSecurityConsiderations() {
    console.log("\n" + "=".repeat(72));
    console.log("25. SECURITY CONSIDERATIONS");
    console.log("=".repeat(72));

    console.log(`
Linear search does not provide authorization or security by itself.

For application code:
- Validate and normalize input where the domain requires it.
- Avoid exposing sensitive record existence through unnecessary responses.
- Avoid logging confidential search values.
- Consider worst-case input sizes when users can trigger searches repeatedly.
- Use database indexes for persistent high-volume query workloads.
- Apply authorization checks before returning sensitive records.
- Do not use a simple linear password lookup as an authentication design.
`);
}


// ============================================================================
// 26. TESTS
// ============================================================================

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function runTests() {
    assert(linearSearch([], 1) === -1, "empty search");
    assert(linearSearch([10], 10) === 0, "singleton match");
    assert(linearSearch([10], 20) === -1, "singleton miss");

    assert(
        firstOccurrence([1, 2, 1, 3, 1], 1) === 0,
        "first occurrence"
    );

    assert(
        lastOccurrence([1, 2, 1, 3, 1], 1) === 4,
        "last occurrence"
    );

    assert(
        JSON.stringify(allOccurrences([1, 2, 1, 3, 1], 1))
        === JSON.stringify([0, 2, 4]),
        "all occurrences"
    );

    assert(
        firstIndexWhere([1, 3, 4, 7], value => value % 2 === 0) === 2,
        "predicate search"
    );

    assert(
        countOccurrences([1, 1, 2, 1], 1) === 3,
        "count occurrences"
    );

    assert(exists([1, 2, 3], 3), "exists");
    assert(!exists([1, 2, 3], 4), "does not exist");

    assert(
        linearSearchSorted([1, 4, 7, 9], 7) === 2,
        "sorted search"
    );

    assert(
        linearSearchSorted([1, 4, 7, 9], 6) === -1,
        "sorted miss"
    );

    assert(
        lastOccurrenceReverse([2, 5, 2, 8], 2) === 2,
        "reverse search"
    );

    assert(
        binarySearch([1, 4, 7, 9, 12], 9) === 3,
        "binary search"
    );

    const statistics = searchWithStatistics([10, 20, 30], 30);
    assert(statistics.found === true, "statistics found");
    assert(statistics.index === 2, "statistics index");
    assert(statistics.comparisons === 3, "statistics comparisons");

    console.log("\nAll JavaScript tests passed.");
}


// ============================================================================
// 27. MAIN
// ============================================================================

function main() {
    console.log("=".repeat(72));
    console.log("DAY 27 — LINEAR SEARCH");
    console.log("=".repeat(72));

    demonstrateBasicSearch();
    demonstrateSequentialProcess();
    demonstrateFirstOccurrence();
    demonstrateLastOccurrence();
    demonstrateAllOccurrences();
    demonstrateSearchConditions();
    demonstrateEarlyExit();
    demonstrateCounting();
    demonstrateSortedSearch();
    demonstrateComparison();
    demonstrateObjectSearch();
    demonstrateKeySearch();
    demonstrateGeneratorSearch();
    demonstrateStringSearch();
    demonstrateStatistics();
    demonstrateProductSearch();
    demonstrateFirstVsAll();
    demonstrateEdgeCases();
    demonstrateValidation();
    demonstrateEqualityBehavior();
    demonstrateUserSearch();
    demonstratePerformance();
    demonstrateEventSearch();
    demonstrateComplexity();
    demonstrateSecurityConsiderations();

    runTests();
}

main();
