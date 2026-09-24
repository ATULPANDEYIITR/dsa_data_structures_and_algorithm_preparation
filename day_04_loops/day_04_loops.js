/*
 * Day 4 — Loops
 *
 * Comprehensive JavaScript study file covering:
 * for, while, do-while, nested loops, counters, termination,
 * break, continue, sequences, sums, factorials, multiplication tables,
 * digit operations, palindrome numbers, primes, Fibonacci numbers,
 * patterns, validation, iterables, generators, searching, complexity,
 * edge cases, and a practical case study.
 *
 * Run with:
 * node day4_loops.js
 */

"use strict";

// ============================================================================
// 1. UTILITY FUNCTIONS
// ============================================================================

function section(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function assertEqual(actual, expected, message) {
    const actualJson = JSON.stringify(actual);
    const expectedJson = JSON.stringify(expected);

    if (actualJson !== expectedJson) {
        throw new Error(
            `${message}\nExpected: ${expectedJson}\nActual: ${actualJson}`
        );
    }
}


// ============================================================================
// 2. FOR LOOP
// ============================================================================

function demonstrateForLoop() {
    section("1. FOR LOOPS");

    console.log("Numbers from 0 through 4:");
    for (let number = 0; number < 5; number++) {
        process.stdout.write(`${number} `);
    }
    console.log();

    console.log("Even numbers from 2 through 10:");
    for (let number = 2; number <= 10; number += 2) {
        process.stdout.write(`${number} `);
    }
    console.log();

    console.log("Countdown:");
    for (let number = 10; number >= 1; number--) {
        process.stdout.write(`${number} `);
    }
    console.log();

    const languages = ["JavaScript", "Python", "C++", "Java"];

    console.log("Array iteration:");
    for (let index = 0; index < languages.length; index++) {
        console.log(index, languages[index]);
    }
}


// ============================================================================
// 3. WHILE LOOP
// ============================================================================

function demonstrateWhileLoop() {
    section("2. WHILE LOOPS");

    let counter = 1;

    while (counter <= 5) {
        process.stdout.write(`${counter} `);
        counter++;
    }

    console.log();

    let countdown = 5;

    while (countdown > 0) {
        console.log(`Countdown: ${countdown}`);
        countdown--;
    }
}


// ============================================================================
// 4. DO-WHILE LOOP
// ============================================================================

function demonstrateDoWhileLoop() {
    section("3. DO-WHILE LOOPS");

    /*
     * A do-while loop executes the body before checking its condition.
     * Therefore the body always executes at least once.
     */
    let attempts = 0;

    do {
        attempts++;
        console.log(`Body executed on attempt ${attempts}`);
    } while (attempts < 3);

    console.log("Even a false initial condition still executes once:");

    let value = 10;

    do {
        console.log(`value = ${value}`);
    } while (value < 5);
}


// ============================================================================
// 5. BREAK AND CONTINUE
// ============================================================================

function demonstrateBreakAndContinue() {
    section("4. BREAK AND CONTINUE");

    console.log("break:");
    for (let number = 1; number <= 10; number++) {
        if (number === 6) {
            break;
        }

        process.stdout.write(`${number} `);
    }
    console.log();

    console.log("continue:");
    for (let number = 1; number <= 10; number++) {
        if (number % 2 === 0) {
            continue;
        }

        process.stdout.write(`${number} `);
    }
    console.log();

    console.log("Nested loop break:");
    for (let row = 0; row < 3; row++) {
        for (let column = 0; column < 5; column++) {
            if (column === 2) {
                break;
            }

            process.stdout.write(`(${row},${column}) `);
        }

        console.log();
    }
}


// ============================================================================
// 6. SEQUENCES AND SUMS
// ============================================================================

function numberSequence(start, end, step = 1) {
    if (step === 0) {
        throw new Error("step cannot be zero");
    }

    const result = [];

    if (step > 0) {
        for (let value = start; value <= end; value += step) {
            result.push(value);
        }
    } else {
        for (let value = start; value >= end; value += step) {
            result.push(value);
        }
    }

    return result;
}

function sumWithFor(numbers) {
    let total = 0;

    for (const number of numbers) {
        total += number;
    }

    return total;
}

function sumWithWhile(numbers) {
    let total = 0;
    let index = 0;

    while (index < numbers.length) {
        total += numbers[index];
        index++;
    }

    return total;
}

function sumEvenNumbers(limit) {
    let total = 0;

    for (let number = 1; number <= limit; number++) {
        if (number % 2 !== 0) {
            continue;
        }

        total += number;
    }

    return total;
}


// ============================================================================
// 7. FACTORIAL
// ============================================================================

function factorial(number) {
    if (!Number.isInteger(number) || number < 0) {
        throw new Error("factorial requires a non-negative integer");
    }

    /*
     * JavaScript Number loses integer precision for sufficiently large
     * values. BigInt is used for the exact implementation below.
     */
    let result = 1n;

    for (let value = 2n; value <= BigInt(number); value++) {
        result *= value;
    }

    return result;
}


// ============================================================================
// 8. MULTIPLICATION TABLES
// ============================================================================

function multiplicationTable(number, limit = 10) {
    const table = [];

    for (let multiplier = 1; multiplier <= limit; multiplier++) {
        table.push(
            `${number} × ${multiplier} = ${number * multiplier}`
        );
    }

    return table;
}

function printAllMultiplicationTables(maxNumber, maxMultiplier) {
    for (let number = 1; number <= maxNumber; number++) {
        console.log(`\nTable of ${number}`);

        for (let multiplier = 1; multiplier <= maxMultiplier; multiplier++) {
            console.log(
                `${number} × ${multiplier} = ${number * multiplier}`
            );
        }
    }
}


// ============================================================================
// 9. DIGIT OPERATIONS
// ============================================================================

function countDigits(number) {
    number = Math.abs(Math.trunc(number));

    if (number === 0) {
        return 1;
    }

    let count = 0;

    while (number > 0) {
        number = Math.floor(number / 10);
        count++;
    }

    return count;
}

function reverseNumber(number) {
    const sign = number < 0 ? -1 : 1;
    let remaining = Math.abs(Math.trunc(number));
    let reversed = 0;

    while (remaining > 0) {
        const digit = remaining % 10;
        reversed = reversed * 10 + digit;
        remaining = Math.floor(remaining / 10);
    }

    return sign * reversed;
}

function sumOfDigits(number) {
    let remaining = Math.abs(Math.trunc(number));
    let total = 0;

    while (remaining > 0) {
        total += remaining % 10;
        remaining = Math.floor(remaining / 10);
    }

    return total;
}


// ============================================================================
// 10. PALINDROME
// ============================================================================

function isPalindromeNumber(number) {
    if (!Number.isInteger(number) || number < 0) {
        return false;
    }

    return number === reverseNumber(number);
}

function isPalindromeWithoutFullReversal(number) {
    if (!Number.isInteger(number) || number < 0) {
        return false;
    }

    if (number < 10) {
        return true;
    }

    let divisor = 1;

    while (Math.floor(number / divisor) >= 10) {
        divisor *= 10;
    }

    while (number !== 0) {
        const leadingDigit = Math.floor(number / divisor);
        const trailingDigit = number % 10;

        if (leadingDigit !== trailingDigit) {
            return false;
        }

        number = Math.floor((number % divisor) / 10);
        divisor = Math.floor(divisor / 100);
    }

    return true;
}


// ============================================================================
// 11. PRIME NUMBERS
// ============================================================================

function isPrimeBasic(number) {
    if (!Number.isInteger(number) || number < 2) {
        return false;
    }

    for (let divisor = 2; divisor < number; divisor++) {
        if (number % divisor === 0) {
            return false;
        }
    }

    return true;
}

function isPrimeOptimized(number) {
    if (!Number.isInteger(number) || number < 2) {
        return false;
    }

    if (number === 2) {
        return true;
    }

    if (number % 2 === 0) {
        return false;
    }

    for (
        let divisor = 3;
        divisor * divisor <= number;
        divisor += 2
    ) {
        if (number % divisor === 0) {
            return false;
        }
    }

    return true;
}

function generatePrimes(limit) {
    const primes = [];

    for (let number = 2; number <= limit; number++) {
        if (isPrimeOptimized(number)) {
            primes.push(number);
        }
    }

    return primes;
}


// ============================================================================
// 12. FIBONACCI
// ============================================================================

function fibonacciSequence(count) {
    if (!Number.isInteger(count) || count < 0) {
        throw new Error("count must be a non-negative integer");
    }

    const sequence = [];
    let first = 0;
    let second = 1;

    for (let index = 0; index < count; index++) {
        sequence.push(first);

        const next = first + second;
        first = second;
        second = next;
    }

    return sequence;
}

function fibonacciUntilLimit(limit) {
    if (limit < 0) {
        return [];
    }

    const sequence = [];
    let first = 0;
    let second = 1;

    while (first <= limit) {
        sequence.push(first);

        const next = first + second;
        first = second;
        second = next;
    }

    return sequence;
}


// ============================================================================
// 13. NESTED LOOPS AND PATTERNS
// ============================================================================

function squarePattern(size) {
    const lines = [];

    for (let row = 0; row < size; row++) {
        let line = "";

        for (let column = 0; column < size; column++) {
            line += "* ";
        }

        lines.push(line.trim());
    }

    return lines;
}

function trianglePattern(height) {
    const lines = [];

    for (let row = 1; row <= height; row++) {
        let line = "";

        for (let column = 0; column < row; column++) {
            line += "* ";
        }

        lines.push(line.trim());
    }

    return lines;
}

function numberTriangle(height) {
    const lines = [];

    for (let row = 1; row <= height; row++) {
        const values = [];

        for (let column = 0; column < row; column++) {
            values.push(String(row));
        }

        lines.push(values.join(" "));
    }

    return lines;
}

function multiplicationGrid(size) {
    const grid = [];

    for (let row = 1; row <= size; row++) {
        const currentRow = [];

        for (let column = 1; column <= size; column++) {
            currentRow.push(row * column);
        }

        grid.push(currentRow);
    }

    return grid;
}


// ============================================================================
// 14. SEARCH
// ============================================================================

function firstMultiple(numbers, divisor) {
    if (divisor === 0) {
        throw new Error("divisor cannot be zero");
    }

    for (const number of numbers) {
        if (number % divisor === 0) {
            return number;
        }
    }

    return null;
}

function firstPrimeInRange(start, end) {
    for (let number = start; number <= end; number++) {
        if (isPrimeOptimized(number)) {
            return number;
        }
    }

    return null;
}


// ============================================================================
// 15. ITERABLES AND GENERATORS
// ============================================================================

function* countdownGenerator(start) {
    /*
     * A generator pauses at each yield.
     * The for-of loop requests values one at a time.
     */
    for (let value = start; value >= 0; value--) {
        yield value;
    }
}

function demonstrateGenerator() {
    section("15. GENERATOR-BASED LOOP");

    for (const value of countdownGenerator(5)) {
        process.stdout.write(`${value} `);
    }

    console.log();
}


// ============================================================================
// 16. ARRAY PROCESSING
// ============================================================================

class NumberAnalyzer {
    constructor(numbers) {
        this.numbers = [...numbers];
    }

    total() {
        let total = 0;

        for (const number of this.numbers) {
            total += number;
        }

        return total;
    }

    positiveNumbers() {
        const result = [];

        for (const number of this.numbers) {
            if (number > 0) {
                result.push(number);
            }
        }

        return result;
    }

    evenNumbers() {
        const result = [];

        for (const number of this.numbers) {
            if (number % 2 === 0) {
                result.push(number);
            }
        }

        return result;
    }

    primeNumbers() {
        const result = [];

        for (const number of this.numbers) {
            if (isPrimeOptimized(number)) {
                result.push(number);
            }
        }

        return result;
    }

    frequencyTable() {
        const frequencies = new Map();

        for (const number of this.numbers) {
            const currentCount = frequencies.get(number) ?? 0;
            frequencies.set(number, currentCount + 1);
        }

        return Object.fromEntries(frequencies);
    }
}


// ============================================================================
// 17. MATRIX PROCESSING
// ============================================================================

function matrixRowSums(matrix) {
    const rowSums = [];

    for (const row of matrix) {
        let total = 0;

        for (const value of row) {
            total += value;
        }

        rowSums.push(total);
    }

    return rowSums;
}

function matrixColumnSums(matrix) {
    if (matrix.length === 0) {
        return [];
    }

    const columnCount = matrix[0].length;

    for (const row of matrix) {
        if (row.length !== columnCount) {
            throw new Error("matrix must be rectangular");
        }
    }

    const columnSums = new Array(columnCount).fill(0);

    for (const row of matrix) {
        for (let column = 0; column < columnCount; column++) {
            columnSums[column] += row[column];
        }
    }

    return columnSums;
}


// ============================================================================
// 18. LOOP TERMINATION AND VALIDATION
// ============================================================================

function parsePositiveInteger(text) {
    if (!/^\d+$/.test(text)) {
        throw new Error("input must contain only digits");
    }

    const value = Number(text);

    if (!Number.isSafeInteger(value) || value <= 0) {
        throw new Error("input must be a positive safe integer");
    }

    return value;
}

function demonstrateValidation() {
    section("18. VALIDATION LOOP");

    const simulatedInputs = ["hello", "-5", "0", "42"];

    for (const input of simulatedInputs) {
        try {
            const value = parsePositiveInteger(input);
            console.log(`${input}: accepted as ${value}`);
            break;
        } catch (error) {
            console.log(`${input}: rejected (${error.message})`);
        }
    }
}


// ============================================================================
// 19. COMPLEXITY
// ============================================================================

function linearWork(limit) {
    let operations = 0;

    for (let index = 0; index < limit; index++) {
        operations++;
    }

    return operations;
}

function quadraticWork(limit) {
    let operations = 0;

    for (let row = 0; row < limit; row++) {
        for (let column = 0; column < limit; column++) {
            operations++;
        }
    }

    return operations;
}

function triangularWork(limit) {
    let operations = 0;

    for (let row = 1; row <= limit; row++) {
        for (let column = 0; column < row; column++) {
            operations++;
        }
    }

    return operations;
}

function sumWithFormula(limit) {
    return limit * (limit + 1) / 2;
}


// ============================================================================
// 20. PRACTICAL CASE STUDY: TRANSACTION PROCESSOR
// ============================================================================

class TransactionProcessor {
    constructor(transactions) {
        this.transactions = transactions.map(transaction => ({
            id: transaction.id,
            amount: transaction.amount,
            status: transaction.status,
            category: transaction.category
        }));
    }

    totalSuccessfulAmount() {
        let total = 0;

        for (const transaction of this.transactions) {
            if (transaction.status !== "SUCCESS") {
                continue;
            }

            total += transaction.amount;
        }

        return total;
    }

    failedTransactionIds() {
        const ids = [];

        for (const transaction of this.transactions) {
            if (transaction.status === "FAILED") {
                ids.push(transaction.id);
            }
        }

        return ids;
    }

    categoryTotals() {
        const totals = {};

        for (const transaction of this.transactions) {
            if (transaction.status !== "SUCCESS") {
                continue;
            }

            if (!(transaction.category in totals)) {
                totals[transaction.category] = 0;
            }

            totals[transaction.category] += transaction.amount;
        }

        return totals;
    }

    largestSuccessfulTransaction() {
        let largest = null;

        for (const transaction of this.transactions) {
            if (transaction.status !== "SUCCESS") {
                continue;
            }

            if (largest === null || transaction.amount > largest.amount) {
                largest = transaction;
            }
        }

        return largest;
    }
}


// ============================================================================
// 21. TESTS
// ============================================================================

function runTests() {
    section("21. AUTOMATED TESTS");

    assertEqual(
        numberSequence(1, 5),
        [1, 2, 3, 4, 5],
        "ascending sequence"
    );

    assertEqual(
        numberSequence(5, 1, -1),
        [5, 4, 3, 2, 1],
        "descending sequence"
    );

    assertEqual(sumWithFor([1, 2, 3, 4]), 10, "for sum");
    assertEqual(sumWithWhile([1, 2, 3, 4]), 10, "while sum");
    assertEqual(sumEvenNumbers(10), 30, "even sum");

    assertEqual(factorial(0), 1n, "zero factorial");
    assertEqual(factorial(5), 120n, "factorial");

    assertEqual(countDigits(0), 1, "zero digit count");
    assertEqual(countDigits(12345), 5, "digit count");
    assertEqual(reverseNumber(1200), 21, "reverse");

    assertEqual(isPalindromeNumber(1221), true, "palindrome");
    assertEqual(isPalindromeNumber(1234), false, "non-palindrome");

    assertEqual(isPrimeOptimized(2), true, "2 is prime");
    assertEqual(isPrimeOptimized(97), true, "97 is prime");
    assertEqual(isPrimeOptimized(100), false, "100 is composite");

    assertEqual(
        fibonacciSequence(8),
        [0, 1, 1, 2, 3, 5, 8, 13],
        "Fibonacci"
    );

    const analyzer = new NumberAnalyzer([1, 2, 2, 3, 5, 6]);

    assertEqual(analyzer.total(), 19, "analyzer total");
    assertEqual(
        analyzer.evenNumbers(),
        [2, 2, 6],
        "analyzer even numbers"
    );
    assertEqual(
        analyzer.primeNumbers(),
        [2, 2, 3, 5],
        "analyzer prime numbers"
    );

    const matrix = [
        [1, 2, 3],
        [4, 5, 6]
    ];

    assertEqual(matrixRowSums(matrix), [6, 15], "row sums");
    assertEqual(matrixColumnSums(matrix), [5, 7, 9], "column sums");

    assertEqual(firstPrimeInRange(50, 100), 53, "first prime");
    assertEqual(firstMultiple([3, 5, 7, 14], 7), 7, "first multiple");

    const processor = new TransactionProcessor([
        { id: 1, amount: 100, status: "SUCCESS", category: "food" },
        { id: 2, amount: 250, status: "FAILED", category: "travel" },
        { id: 3, amount: 300, status: "SUCCESS", category: "travel" }
    ]);

    assertEqual(
        processor.totalSuccessfulAmount(),
        400,
        "successful amount"
    );

    assertEqual(
        processor.failedTransactionIds(),
        [2],
        "failed transaction IDs"
    );

    assertEqual(
        processor.categoryTotals(),
        { food: 100, travel: 300 },
        "category totals"
    );

    console.log("All tests passed.");
}


// ============================================================================
// 22. MAIN
// ============================================================================

function main() {
    section("DAY 4 — LOOPS");

    demonstrateForLoop();
    demonstrateWhileLoop();
    demonstrateDoWhileLoop();
    demonstrateBreakAndContinue();

    section("NUMBER SEQUENCES");
    console.log(numberSequence(1, 10));
    console.log(numberSequence(10, 1, -1));

    section("SUMS");
    console.log("for:", sumWithFor([1, 2, 3, 4, 5]));
    console.log("while:", sumWithWhile([1, 2, 3, 4, 5]));
    console.log("even through 20:", sumEvenNumbers(20));

    section("FACTORIAL");
    for (let number = 0; number <= 7; number++) {
        console.log(`${number}! = ${factorial(number)}`);
    }

    section("MULTIPLICATION TABLE");
    console.log(multiplicationTable(7).join("\n"));

    section("DIGIT OPERATIONS");
    console.log("digits:", countDigits(987654));
    console.log("reverse:", reverseNumber(987654));
    console.log("digit sum:", sumOfDigits(987654));

    section("PALINDROMES");
    for (const number of [121, 123, 1331, 12321]) {
        console.log(number, isPalindromeNumber(number));
    }

    section("PRIMES");
    console.log(generatePrimes(50));

    section("FIBONACCI");
    console.log(fibonacciSequence(12));
    console.log(fibonacciUntilLimit(100));

    section("PATTERNS");
    console.log(squarePattern(4).join("\n"));
    console.log();
    console.log(trianglePattern(5).join("\n"));
    console.log();
    console.log(numberTriangle(5).join("\n"));

    section("MULTIPLICATION GRID");
    console.table(multiplicationGrid(5));

    demonstrateGenerator();
    demonstrateValidation();

    section("NUMBER ANALYZER");
    const analyzer = new NumberAnalyzer([12, 7, 7, 13, 20, 29, 30, 30]);

    console.log("Numbers:", analyzer.numbers);
    console.log("Total:", analyzer.total());
    console.log("Positive:", analyzer.positiveNumbers());
    console.log("Even:", analyzer.evenNumbers());
    console.log("Prime:", analyzer.primeNumbers());
    console.log("Frequency:", analyzer.frequencyTable());

    section("MATRIX PROCESSING");

    const matrix = [
        [10, 20, 30],
        [40, 50, 60],
        [70, 80, 90]
    ];

    console.log("Row sums:", matrixRowSums(matrix));
    console.log("Column sums:", matrixColumnSums(matrix));

    section("COMPLEXITY");

    for (const size of [5, 10, 100]) {
        console.log(
            `n=${size}: linear=${linearWork(size)}, ` +
            `quadratic=${quadraticWork(size)}, ` +
            `triangular=${triangularWork(size)}`
        );
    }

    console.log("Formula sum 1..100000:", sumWithFormula(100000));

    section("TRANSACTION CASE STUDY");

    const transactions = new TransactionProcessor([
        { id: "TX001", amount: 1250, status: "SUCCESS", category: "food" },
        { id: "TX002", amount: 5000, status: "SUCCESS", category: "travel" },
        { id: "TX003", amount: 800, status: "FAILED", category: "food" },
        { id: "TX004", amount: 2200, status: "SUCCESS", category: "utilities" },
        { id: "TX005", amount: 750, status: "FAILED", category: "travel" }
    ]);

    console.log(
        "Successful amount:",
        transactions.totalSuccessfulAmount()
    );

    console.log(
        "Failed IDs:",
        transactions.failedTransactionIds()
    );

    console.log(
        "Category totals:",
        transactions.categoryTotals()
    );

    console.log(
        "Largest successful transaction:",
        transactions.largestSuccessfulTransaction()
    );

    runTests();

    section("DAY 4 COMPLETE");
    console.log("Loop fundamentals and practical algorithms completed.");
}


main();
