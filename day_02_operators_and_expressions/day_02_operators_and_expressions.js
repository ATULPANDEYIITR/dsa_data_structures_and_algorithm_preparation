/*
 * Operators and Expressions
 * =========================
 *
 * A comprehensive JavaScript study program covering:
 * - Arithmetic operators
 * - Comparison operators
 * - Logical operators
 * - Assignment operators
 * - Increment and decrement
 * - Modulo
 * - Operator precedence
 * - Expressions
 * - Type conversion and coercion
 * - Short-circuit evaluation
 * - Nullish coalescing
 * - Optional chaining
 * - Bitwise operators
 * - Practical numerical problems
 * - Validation and error handling
 * - Floating-point considerations
 * - Objects and operator-related behavior
 * - Performance and debugging considerations
 *
 * Run with:
 *   node operators_and_expressions.js
 */

"use strict";

function section(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function subsection(title) {
    console.log("\n" + "-".repeat(78));
    console.log(title);
    console.log("-".repeat(78));
}

function show(label, value) {
    console.log(`${label.padEnd(42)} ->`, value);
}

// ---------------------------------------------------------------------------
// 1. Expressions
// ---------------------------------------------------------------------------

function demonstrateExpressions() {
    section("1. Expressions and values");

    const age = 25;
    const yearsToRetirement = 60 - age;
    const expressionResult = (10 + 5) * 2;

    show("age", age);
    show("60 - age", yearsToRetirement);
    show("(10 + 5) * 2", expressionResult);

    // A function call is also an expression because it produces a value.
    show("Math.abs(-42)", Math.abs(-42));
    show("Math.round(3.6)", Math.round(3.6));

    const temperature = 28;
    const isHot = temperature > 25;
    show("temperature > 25", isHot);
}

// ---------------------------------------------------------------------------
// 2. Arithmetic operators
// ---------------------------------------------------------------------------

function demonstrateArithmetic() {
    section("2. Arithmetic operators");

    const a = 17;
    const b = 5;

    show("a + b", a + b);
    show("a - b", a - b);
    show("a * b", a * b);
    show("a / b", a / b);
    show("a % b", a % b);
    show("a ** b", a ** b);

    // JavaScript's / produces a floating-point result.
    show("17 / 5", 17 / 5);

    // JavaScript has no separate integer-division operator like Python's //.
    // Math.floor can be used when floor division is actually intended.
    show("Math.floor(17 / 5)", Math.floor(17 / 5));

    subsection("Negative modulo behavior");

    for (const value of [-17, -5, 5, 17]) {
        console.log(`${value} % 3 = ${value % 3}`);
    }

    subsection("Floating-point representation");

    const result = 0.1 + 0.2;
    show("0.1 + 0.2", result);
    show("(0.1 + 0.2) === 0.3", result === 0.3);
}

// ---------------------------------------------------------------------------
// 3. Modulo and digit calculations
// ---------------------------------------------------------------------------

function isEven(number) {
    return number % 2 === 0;
}

function digitSum(number) {
    let value = Math.abs(Math.trunc(number));
    let total = 0;

    if (value === 0) {
        return 0;
    }

    while (value > 0) {
        total += value % 10;
        value = Math.floor(value / 10);
    }

    return total;
}

function reverseInteger(number) {
    const sign = number < 0 ? -1 : 1;
    let value = Math.abs(Math.trunc(number));
    let result = 0;

    while (value > 0) {
        result = result * 10 + (value % 10);
        value = Math.floor(value / 10);
    }

    return sign * result;
}

function demonstrateModulo() {
    section("3. Modulo and remainder");

    const number = 58327;

    show("58327 % 2", number % 2);
    show("58327 % 3", number % 3);
    show("58327 % 10", number % 10);

    console.log("\nEven/odd classification:");

    for (let value = 0; value <= 10; value++) {
        console.log(`${value} -> ${isEven(value) ? "even" : "odd"}`);
    }

    console.log("\nDigit extraction:");

    show("Digit sum of 58327", digitSum(58327));
    show("Reverse of 58327", reverseInteger(58327));
    show("Reverse of -12345", reverseInteger(-12345));
}

// ---------------------------------------------------------------------------
// 4. Comparison operators
// ---------------------------------------------------------------------------

function demonstrateComparisons() {
    section("4. Comparison operators");

    const a = 10;
    const b = 20;

    show("a === b", a === b);
    show("a !== b", a !== b);
    show("a < b", a < b);
    show("a <= b", a <= b);
    show("a > b", a > b);
    show("a >= b", a >= b);

    subsection("Strict equality versus loose equality");

    // === checks both value and type.
    show("5 === '5'", 5 === "5");

    // == performs type coercion before comparison.
    show("5 == '5'", 5 == "5");

    console.log(
        "Strict equality (===) is normally preferred because it makes " +
        "type conversion explicit."
    );
}

// ---------------------------------------------------------------------------
// 5. Logical operators
// ---------------------------------------------------------------------------

function demonstrateLogicalOperators() {
    section("5. Logical operators");

    const values = [true, false];

    console.log("\nAND truth table:");
    for (const left of values) {
        for (const right of values) {
            console.log(`${left} && ${right} = ${left && right}`);
        }
    }

    console.log("\nOR truth table:");
    for (const left of values) {
        for (const right of values) {
            console.log(`${left} || ${right} = ${left || right}`);
        }
    }

    console.log("\nNOT:");
    for (const value of values) {
        console.log(`!${value} = ${!value}`);
    }

    const age = 25;
    const hasId = true;
    const allowed = age >= 18 && hasId;

    show("Adult with valid ID", allowed);

    const weekend = false;
    const holiday = true;

    show("Weekend OR holiday", weekend || holiday);

    subsection("Short-circuit evaluation");

    function expensiveCheck() {
        console.log("expensiveCheck() was evaluated");
        return true;
    }

    const first = false && expensiveCheck();
    show("false && expensiveCheck()", first);

    const second = true || expensiveCheck();
    show("true || expensiveCheck()", second);
}

// ---------------------------------------------------------------------------
// 6. Assignment operators
// ---------------------------------------------------------------------------

function demonstrateAssignment() {
    section("6. Assignment operators");

    let value = 10;
    show("Initial value", value);

    value += 5;
    show("value += 5", value);

    value -= 3;
    show("value -= 3", value);

    value *= 2;
    show("value *= 2", value);

    value /= 4;
    show("value /= 4", value);

    value %= 5;
    show("value %= 5", value);

    value **= 3;
    show("value **= 3", value);

    // JavaScript also supports bitwise assignment operators.
    let mask = 0b0011;
    mask |= 0b0100;
    show("mask after |= 0b0100", mask.toString(2));
}

// ---------------------------------------------------------------------------
// 7. Increment and decrement
// ---------------------------------------------------------------------------

function demonstrateIncrementDecrement() {
    section("7. Increment and decrement");

    let counter = 0;

    // Postfix increment returns the old value before incrementing.
    show("counter++ returns", counter++);
    show("counter after counter++", counter);

    // Prefix increment increments first and then returns the new value.
    show("++counter returns", ++counter);
    show("counter after ++counter", counter);

    // The same distinction exists for decrement.
    show("counter-- returns", counter--);
    show("counter after counter--", counter);

    show("--counter returns", --counter);
    show("counter after --counter", counter);

    console.log(
        "\nPre-increment changes the variable before its value is used; " +
        "post-increment uses the old value first."
    );
}

// ---------------------------------------------------------------------------
// 8. Operator precedence
// ---------------------------------------------------------------------------

function demonstratePrecedence() {
    section("8. Operator precedence");

    show("2 + 3 * 4", 2 + 3 * 4);
    show("(2 + 3) * 4", (2 + 3) * 4);

    show("20 - 4 * 3", 20 - 4 * 3);
    show("(20 - 4) * 3", (20 - 4) * 3);

    // Parentheses make intended evaluation order explicit.
    const principal = 1000;
    const rate = 0.08;
    const years = 2;

    const amount = principal * (1 + rate) ** years;
    show("Compound growth", amount);

    console.log(
        "Use parentheses when a calculation would otherwise be difficult "
        + "to read or easy to misunderstand."
    );
}

// ---------------------------------------------------------------------------
// 9. Conditional expressions
// ---------------------------------------------------------------------------

function demonstrateConditionalExpressions() {
    section("9. Conditional expressions");

    const number = 17;
    const classification = number % 2 === 0 ? "even" : "odd";

    show("17 classification", classification);

    const score = 82;
    const grade =
        score >= 90 ? "A" :
        score >= 80 ? "B" :
        score >= 70 ? "C" :
        score >= 60 ? "D" : "F";

    show("Grade for 82", grade);
}

// ---------------------------------------------------------------------------
// 10. Practical problems
// ---------------------------------------------------------------------------

function isPositive(number) {
    return number > 0;
}

function largestOfTwo(a, b) {
    return a >= b ? a : b;
}

function largestOfThree(a, b, c) {
    return Math.max(a, b, c);
}

function isDivisible(number, divisor) {
    if (divisor === 0) {
        throw new Error("A divisor cannot be zero.");
    }

    return number % divisor === 0;
}

function countDigits(number) {
    let value = Math.abs(Math.trunc(number));

    if (value === 0) {
        return 1;
    }

    let count = 0;

    while (value > 0) {
        value = Math.floor(value / 10);
        count++;
    }

    return count;
}

function demonstratePracticalProblems() {
    section("10. Practical beginner problems");

    const numbers = [0, 1, 2, 17, -8, 101];

    for (const number of numbers) {
        const classification =
            number > 0 ? "positive" :
            number < 0 ? "negative" : "zero";

        console.log(
            `${number}: ${classification}, ` +
            `even=${isEven(number)}, ` +
            `digits=${countDigits(number)}, ` +
            `digitSum=${digitSum(number)}, ` +
            `reverse=${reverseInteger(number)}`
        );
    }

    show("Largest of 10 and 25", largestOfTwo(10, 25));
    show("Largest of 10, 25 and 17", largestOfThree(10, 25, 17));

    for (const divisor of [2, 3, 5, 7]) {
        show(
            `100 divisible by ${divisor}`,
            isDivisible(100, divisor)
        );
    }
}

// ---------------------------------------------------------------------------
// 11. Calculator
// ---------------------------------------------------------------------------

const operations = {
    "+": (a, b) => a + b,
    "-": (a, b) => a - b,
    "*": (a, b) => a * b,
    "/": (a, b) => a / b,
    "%": (a, b) => a % b,
    "**": (a, b) => a ** b
};

function calculate(left, symbol, right) {
    if (!Object.prototype.hasOwnProperty.call(operations, symbol)) {
        throw new Error(`Unsupported operator: ${symbol}`);
    }

    if ((symbol === "/" || symbol === "%") && right === 0) {
        throw new Error("Division or remainder by zero is invalid.");
    }

    return operations[symbol](left, right);
}

function demonstrateCalculator() {
    section("11. Simple calculator");

    const examples = [
        [10, "+", 5],
        [10, "-", 5],
        [10, "*", 5],
        [10, "/", 5],
        [10, "%", 3],
        [2, "**", 5]
    ];

    for (const [left, symbol, right] of examples) {
        console.log(
            `${left} ${symbol} ${right} = ${calculate(left, symbol, right)}`
        );
    }

    subsection("Calculator errors");

    for (const example of [
        [10, "/", 0],
        [10, "%", 0],
        [10, "$", 2]
    ]) {
        try {
            console.log(calculate(...example));
        } catch (error) {
            console.log(
                `${example.join(" ")} -> ERROR: ${error.message}`
            );
        }
    }
}

// ---------------------------------------------------------------------------
// 12. Type coercion
// ---------------------------------------------------------------------------

function demonstrateTypeCoercion() {
    section("12. Type coercion and expressions");

    show("5 + 3", 5 + 3);
    show("'5' + 3", "5" + 3);
    show("'5' - 3", "5" - 3);
    show("Number('5') + 3", Number("5") + 3);

    show("Boolean(0)", Boolean(0));
    show("Boolean(1)", Boolean(1));
    show("Boolean('')", Boolean(""));
    show("Boolean('text')", Boolean("text"));

    console.log(
        "\nThe + operator can perform numeric addition or string "
        + "concatenation, so operand types matter."
    );
}

// ---------------------------------------------------------------------------
// 13. Nullish coalescing and optional chaining
// ---------------------------------------------------------------------------

function demonstrateModernExpressionOperators() {
    section("13. Nullish coalescing and optional chaining");

    const settings = {
        username: "Atul",
        preferences: {
            theme: "dark"
        }
    };

    const theme = settings.preferences?.theme ?? "light";
    show("Existing theme", theme);

    const missingLanguage =
        settings.preferences?.language ?? "English";

    show("Missing language with ??", missingLanguage);

    const missingObject = null;
    show("Optional property access", missingObject?.name);

    console.log(
        "\n?? uses the fallback only for null or undefined. "
        + "This differs from ||, which also treats values such as 0 and '' as false."
    );

    show("0 || 100", 0 || 100);
    show("0 ?? 100", 0 ?? 100);
}

// ---------------------------------------------------------------------------
// 14. Bitwise operators
// ---------------------------------------------------------------------------

function demonstrateBitwiseOperators() {
    section("14. Bitwise operators");

    const a = 0b1100;
    const b = 0b1010;

    show("a", a.toString(2));
    show("b", b.toString(2));
    show("a & b", (a & b).toString(2));
    show("a | b", (a | b).toString(2));
    show("a ^ b", (a ^ b).toString(2));
    show("~a", (~a).toString(2));
    show("a << 1", (a << 1).toString(2));
    show("a >> 1", (a >> 1).toString(2));

    const READ = 0b001;
    const WRITE = 0b010;
    const EXECUTE = 0b100;

    let permissions = READ | WRITE;

    show("Has READ", Boolean(permissions & READ));
    show("Has EXECUTE", Boolean(permissions & EXECUTE));

    permissions |= EXECUTE;
    show("Permissions after EXECUTE", permissions.toString(2));

    permissions &= ~WRITE;
    show("Permissions after removing WRITE", permissions.toString(2));
}

// ---------------------------------------------------------------------------
// 15. Truthy and falsy values
// ---------------------------------------------------------------------------

function demonstrateTruthyFalsy() {
    section("15. Truthy and falsy values");

    const values = [
        false,
        true,
        0,
        1,
        "",
        "text",
        null,
        undefined,
        [],
        {}
    ];

    for (const value of values) {
        console.log(`${String(value).padEnd(12)} -> ${Boolean(value)}`);
    }

    console.log(
        "\nEmpty arrays and empty objects are truthy in JavaScript."
    );
}

// ---------------------------------------------------------------------------
// 16. Logical operators returning operands
// ---------------------------------------------------------------------------

function demonstrateLogicalOperandBehavior() {
    section("16. Logical operators as value-producing expressions");

    // JavaScript && and || return one of their operands rather than always
    // returning true or false.
    show("'hello' && 42", "hello" && 42);
    show("'' && 42", "" && 42);
    show("null || 'fallback'", null || "fallback");
    show("'value' || 'fallback'", "value" || "fallback");

    const username = "";
    const displayName = username || "Guest";

    show("Default display name", displayName);
}

// ---------------------------------------------------------------------------
// 17. Object-based expression example
// ---------------------------------------------------------------------------

class Measurement {
    constructor(value, unit) {
        if (!Number.isFinite(value)) {
            throw new TypeError("Measurement value must be finite.");
        }

        if (typeof unit !== "string" || unit.trim() === "") {
            throw new TypeError("Unit must be a non-empty string.");
        }

        this.value = value;
        this.unit = unit;
    }

    scale(factor) {
        if (!Number.isFinite(factor)) {
            throw new TypeError("Scale factor must be finite.");
        }

        return new Measurement(this.value * factor, this.unit);
    }

    toString() {
        return `${this.value} ${this.unit}`;
    }
}

function demonstrateObjectsAndExpressions() {
    section("17. Objects and operator-like behavior");

    const distance = new Measurement(10, "km");
    const doubled = distance.scale(2);

    show("Original measurement", distance.toString());
    show("Scaled measurement", doubled.toString());

    console.log(
        "\nJavaScript does not support Python-style custom operator "
        + "overloading for user-defined classes. Domain operations are "
        + "normally represented with methods such as scale()."
    );
}

// ---------------------------------------------------------------------------
// 18. Mathematical expressions
// ---------------------------------------------------------------------------

function demonstrateMathematicalExpressions() {
    section("18. Practical mathematical expressions");

    const length = 12;
    const width = 7;

    show("Rectangle area", length * width);
    show("Rectangle perimeter", 2 * (length + width));

    const radius = 5;

    show("Circle area", Math.PI * radius ** 2);
    show("Circle circumference", 2 * Math.PI * radius);

    const principal = 10000;
    const rate = 7.5;
    const years = 3;

    const simpleInterest = principal * rate * years / 100;
    show("Simple interest", simpleInterest);
    show("Total amount", principal + simpleInterest);

    const celsius = 25;
    show("25 Celsius in Fahrenheit", celsius * 9 / 5 + 32);
}

// ---------------------------------------------------------------------------
// 19. Validation and special numeric values
// ---------------------------------------------------------------------------

function demonstrateValidation() {
    section("19. Validation and special numeric values");

    const values = [42, 0, -5, Infinity, -Infinity, NaN];

    for (const value of values) {
        console.log(
            `${String(value).padEnd(10)} ` +
            `finite=${Number.isFinite(value)} ` +
            `integer=${Number.isInteger(value)}`
        );
    }

    console.log("\nDivision by zero in JavaScript:");

    show("10 / 0", 10 / 0);
    show("-10 / 0", -10 / 0);
    show("0 / 0", 0 / 0);

    console.log(
        "\nUnlike Python, JavaScript numeric division by zero normally "
        + "produces Infinity or NaN instead of throwing an exception."
    );
}

// ---------------------------------------------------------------------------
// 20. BigInt
// ---------------------------------------------------------------------------

function demonstrateBigInt() {
    section("20. BigInt and integer precision");

    const ordinaryLarge = 9007199254740991;
    const safeLimit = Number.MAX_SAFE_INTEGER;

    show("Number.MAX_SAFE_INTEGER", safeLimit);
    show("Large ordinary integer", ordinaryLarge);

    const preciseLarge = 9007199254740991n + 2n;
    show("BigInt precise result", preciseLarge);

    console.log(
        "\nBigInt is useful when integer values exceed the safe precision "
        + "range of JavaScript Number. Number and BigInt should not be mixed "
        + "directly in arithmetic expressions."
    );
}

// ---------------------------------------------------------------------------
// 21. Performance considerations
// ---------------------------------------------------------------------------

function demonstratePerformance() {
    section("21. Performance considerations");

    const limit = 1_000_000;
    let evenCount = 0;

    for (let value = 0; value < limit; value++) {
        if (value % 2 === 0) {
            evenCount++;
        }
    }

    show("Even numbers below one million", evenCount);

    console.log(
        "For performance-sensitive applications, algorithmic complexity "
        + "usually matters more than replacing one basic arithmetic operator "
        + "with another equivalent expression."
    );
}

// ---------------------------------------------------------------------------
// 22. Assertions
// ---------------------------------------------------------------------------

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function runAssertions() {
    section("22. Built-in verification");

    assert(2 + 3 === 5, "addition");
    assert(10 - 4 === 6, "subtraction");
    assert(6 * 7 === 42, "multiplication");
    assert(20 / 4 === 5, "division");
    assert(20 % 6 === 2, "modulo");
    assert(2 ** 5 === 32, "exponentiation");

    assert(isEven(10), "10 should be even");
    assert(!isEven(11), "11 should be odd");

    assert(largestOfTwo(5, 10) === 10, "largest of two");
    assert(largestOfThree(1, 9, 3) === 9, "largest of three");

    assert(digitSum(12345) === 15, "digit sum");
    assert(reverseInteger(12345) === 54321, "reverse integer");

    assert(calculate(10, "+", 5) === 15, "calculator");

    try {
        calculate(10, "/", 0);
        throw new Error("Expected division-by-zero validation.");
    } catch (error) {
        if (!error.message.includes("division")) {
            throw error;
        }
    }

    console.log("All demonstration assertions passed.");
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function main() {
    console.log("OPERATORS AND EXPRESSIONS");
    console.log("A structured JavaScript study and practice program");

    demonstrateExpressions();
    demonstrateArithmetic();
    demonstrateModulo();
    demonstrateComparisons();
    demonstrateLogicalOperators();
    demonstrateAssignment();
    demonstrateIncrementDecrement();
    demonstratePrecedence();
    demonstrateConditionalExpressions();
    demonstratePracticalProblems();
    demonstrateCalculator();
    demonstrateTypeCoercion();
    demonstrateModernExpressionOperators();
    demonstrateBitwiseOperators();
    demonstrateTruthyFalsy();
    demonstrateLogicalOperandBehavior();
    demonstrateObjectsAndExpressions();
    demonstrateMathematicalExpressions();
    demonstrateValidation();
    demonstrateBigInt();
    demonstratePerformance();
    runAssertions();

    section("End of operators and expressions study program");
}

main();
