/*
 * Day 3 — Conditions
 * ===================
 *
 * A comprehensive JavaScript study file covering decision-making
 * from beginner concepts through structured application logic.
 *
 * Topics:
 * - if
 * - else
 * - else if
 * - nested conditions
 * - Boolean expressions
 * - compound conditions
 * - comparison operators
 * - logical operators
 * - truthy/falsy values
 * - equality and identity
 * - conditional expressions
 * - validation
 * - practical decision systems
 * - edge cases
 * - short-circuit evaluation
 * - guard clauses
 * - testing
 * - performance
 */

/* ==========================================================================
   1. BASIC if
   ========================================================================== */

function basicIfExamples() {
    console.log("\n=== 1. Basic if Statements ===");

    const temperature = 32;

    // The comparison produces true or false.
    if (temperature > 30) {
        console.log("It is a hot day.");
    }

    const age = 20;

    if (age >= 18) {
        console.log("The person is an adult.");
    }

    const balance = 100;

    // This branch is skipped because the condition is false.
    if (balance >= 500) {
        console.log("Premium threshold reached.");
    }

    console.log("Execution continues.");
}


/* ==========================================================================
   2. if / else
   ========================================================================== */

function ifElseExamples() {
    console.log("\n=== 2. if / else ===");

    const number = 17;

    if (number % 2 === 0) {
        console.log("Even");
    } else {
        console.log("Odd");
    }

    const age = 16;

    if (age >= 18) {
        console.log("Adult");
    } else {
        console.log("Minor");
    }
}


/* ==========================================================================
   3. if / else if / else
   ========================================================================== */

function elseIfExamples() {
    console.log("\n=== 3. else if ===");

    const score = 87;
    let grade;

    if (score >= 90) {
        grade = "A";
    } else if (score >= 80) {
        grade = "B";
    } else if (score >= 70) {
        grade = "C";
    } else if (score >= 60) {
        grade = "D";
    } else {
        grade = "F";
    }

    console.log(`Score ${score} -> Grade ${grade}`);
}


/* ==========================================================================
   4. COMPARISON OPERATORS
   ========================================================================== */

function comparisonExamples() {
    console.log("\n=== 4. Comparison Operators ===");

    const a = 10;
    const b = 20;

    console.log("a === b:", a === b);
    console.log("a !== b:", a !== b);
    console.log("a < b:", a < b);
    console.log("a <= b:", a <= b);
    console.log("a > b:", a > b);
    console.log("a >= b:", a >= b);

    // Strict equality is preferred because it compares both value and type.
    console.log('10 === "10":', 10 === "10");
    console.log('10 == "10":', 10 == "10");
}


/* ==========================================================================
   5. LOGICAL OPERATORS
   ========================================================================== */

function logicalOperatorExamples() {
    console.log("\n=== 5. Logical Operators ===");

    const age = 25;
    const hasId = true;
    const isStudent = false;

    // AND requires both expressions to be truthy.
    const canEnter = age >= 18 && hasId;

    // OR requires at least one expression to be truthy.
    const receivesDiscount = isStudent || age >= 60;

    // NOT reverses truthiness.
    const accountLocked = false;

    console.log("Can enter:", canEnter);
    console.log("Receives discount:", receivesDiscount);
    console.log("Account available:", !accountLocked);
}


/* ==========================================================================
   6. COMPOUND CONDITIONS
   ========================================================================== */

function compoundConditionExamples() {
    console.log("\n=== 6. Compound Conditions ===");

    const age = 25;
    const income = 80000;
    const creditScore = 760;

    const eligible =
        age >= 21 &&
        income >= 30000 &&
        creditScore >= 700;

    console.log("Eligible:", eligible);

    // Parentheses make complicated business rules easier to read.
    const priorityCustomer =
        (income >= 100000 && creditScore >= 750) ||
        creditScore >= 800;

    console.log("Priority customer:", priorityCustomer);
}


/* ==========================================================================
   7. NESTED CONDITIONS
   ========================================================================== */

function nestedConditionExamples() {
    console.log("\n=== 7. Nested Conditions ===");

    const age = 24;
    const hasTicket = true;

    if (age >= 18) {
        if (hasTicket) {
            console.log("Entry approved.");
        } else {
            console.log("Ticket required.");
        }
    } else {
        console.log("Minimum age not met.");
    }

    // Nested authentication example.
    const username = "admin";
    const passwordCorrect = true;
    const accountActive = true;

    if (username === "admin") {
        if (passwordCorrect) {
            if (accountActive) {
                console.log("Login successful.");
            } else {
                console.log("Account inactive.");
            }
        } else {
            console.log("Incorrect password.");
        }
    } else {
        console.log("Unknown user.");
    }
}


/* ==========================================================================
   8. TRUTHY AND FALSY
   ========================================================================== */

function truthinessExamples() {
    console.log("\n=== 8. Truthy and Falsy Values ===");

    const values = [
        true,
        false,
        0,
        1,
        "",
        "JavaScript",
        null,
        undefined,
        [],
        {},
        NaN
    ];

    for (const value of values) {
        if (value) {
            console.log(value, "is truthy");
        } else {
            console.log(value, "is falsy");
        }
    }

    // Arrays and objects are truthy even when empty.
    console.log("[] is truthy:", Boolean([]));
    console.log("{} is truthy:", Boolean({}));
}


/* ==========================================================================
   9. CONDITIONAL EXPRESSION
   ========================================================================== */

function conditionalExpressionExamples() {
    console.log("\n=== 9. Conditional Expression ===");

    const number = 42;

    // JavaScript's ternary operator provides a compact conditional expression.
    const classification = number % 2 === 0 ? "even" : "odd";

    console.log(classification);

    const age = 20;
    const category = age >= 18 ? "adult" : "minor";

    console.log(category);
}


/* ==========================================================================
   10. GRADE CALCULATOR
   ========================================================================== */

function calculateGrade(score) {
    if (!Number.isFinite(score) || score < 0 || score > 100) {
        throw new RangeError("Score must be between 0 and 100.");
    }

    if (score >= 90) {
        return "A";
    } else if (score >= 80) {
        return "B";
    } else if (score >= 70) {
        return "C";
    } else if (score >= 60) {
        return "D";
    }

    return "F";
}

function gradeDemo() {
    console.log("\n=== 10. Grade Calculator ===");

    for (const score of [100, 90, 89.99, 80, 70, 60, 59.99, 0]) {
        console.log(`${score} -> ${calculateGrade(score)}`);
    }
}


/* ==========================================================================
   11. LEAP YEAR
   ========================================================================== */

function isLeapYear(year) {
    if (!Number.isInteger(year) || year <= 0) {
        throw new RangeError("Year must be a positive integer.");
    }

    return (
        year % 400 === 0 ||
        (year % 4 === 0 && year % 100 !== 0)
    );
}

function leapYearDemo() {
    console.log("\n=== 11. Leap Year ===");

    for (const year of [1600, 1700, 1900, 2000, 2024, 2025, 2100]) {
        console.log(`${year} -> ${isLeapYear(year)}`);
    }
}


/* ==========================================================================
   12. NUMBER CLASSIFICATION
   ========================================================================== */

function classifyNumber(number) {
    if (!Number.isFinite(number)) {
        throw new TypeError("Number must be finite.");
    }

    if (number === 0) {
        return "zero";
    }

    if (number > 0) {
        return Number.isInteger(number)
            ? "positive integer"
            : "positive number";
    }

    return Number.isInteger(number)
        ? "negative integer"
        : "negative number";
}

function numberClassificationDemo() {
    console.log("\n=== 12. Number Classification ===");

    for (const number of [-10, -2.5, 0, 3, 4.75]) {
        console.log(`${number} -> ${classifyNumber(number)}`);
    }
}


/* ==========================================================================
   13. TRIANGLE VALIDITY
   ========================================================================== */

function isValidTriangle(a, b, c) {
    if (![a, b, c].every(Number.isFinite)) {
        return false;
    }

    if (a <= 0 || b <= 0 || c <= 0) {
        return false;
    }

    return (
        a + b > c &&
        a + c > b &&
        b + c > a
    );
}

function classifyTriangle(a, b, c) {
    if (!isValidTriangle(a, b, c)) {
        return "invalid";
    }

    if (a === b && b === c) {
        return "equilateral";
    }

    if (a === b || b === c || a === c) {
        return "isosceles";
    }

    return "scalene";
}

function triangleDemo() {
    console.log("\n=== 13. Triangle Classification ===");

    const triangles = [
        [3, 3, 3],
        [3, 3, 4],
        [3, 4, 5],
        [1, 2, 3],
        [-1, 2, 2]
    ];

    for (const triangle of triangles) {
        console.log(triangle, "->", classifyTriangle(...triangle));
    }
}


/* ==========================================================================
   14. LARGEST OF MULTIPLE VALUES
   ========================================================================== */

function largestOfValues(values) {
    if (!Array.isArray(values) || values.length === 0) {
        throw new RangeError("At least one value is required.");
    }

    if (!values.every(Number.isFinite)) {
        throw new TypeError("All values must be finite numbers.");
    }

    let largest = values[0];

    for (const value of values.slice(1)) {
        if (value > largest) {
            largest = value;
        }
    }

    return largest;
}

function largestDemo() {
    console.log("\n=== 14. Largest Value ===");

    console.log(largestOfValues([10, 25, 7]));
    console.log(largestOfValues([-100, -5, -20, -1]));
    console.log(largestOfValues([4, 4, 4]));
}


/* ==========================================================================
   15. BILLING SYSTEM
   ========================================================================== */

function calculateBill(
    unitPrice,
    quantity,
    discountThreshold = 5000,
    discountRate = 0.10,
    taxRate = 0.18
) {
    if (!Number.isFinite(unitPrice) || unitPrice < 0) {
        throw new RangeError("Unit price cannot be negative.");
    }

    if (!Number.isInteger(quantity) || quantity <= 0) {
        throw new RangeError("Quantity must be a positive integer.");
    }

    const subtotal = unitPrice * quantity;

    const discount =
        subtotal >= discountThreshold
            ? subtotal * discountRate
            : 0;

    const taxableAmount = subtotal - discount;
    const tax = taxableAmount * taxRate;
    const total = taxableAmount + tax;

    return {
        subtotal,
        discount,
        tax,
        total
    };
}

function billingDemo() {
    console.log("\n=== 15. Billing System ===");

    for (const [price, quantity] of [
        [100, 3],
        [1000, 6],
        [5000, 1]
    ]) {
        console.log(
            [price, quantity],
            "->",
            calculateBill(price, quantity)
        );
    }
}


/* ==========================================================================
   16. AGE CLASSIFICATION
   ========================================================================== */

function classifyAge(age) {
    if (!Number.isInteger(age)) {
        throw new TypeError("Age must be an integer.");
    }

    if (age < 0) {
        throw new RangeError("Age cannot be negative.");
    }

    if (age <= 12) {
        return "child";
    } else if (age <= 17) {
        return "teenager";
    } else if (age <= 59) {
        return "adult";
    }

    return "senior";
}

function ageDemo() {
    console.log("\n=== 16. Age Classification ===");

    for (const age of [0, 12, 13, 17, 18, 59, 60, 100]) {
        console.log(`${age} -> ${classifyAge(age)}`);
    }
}


/* ==========================================================================
   17. ELECTRICITY BILL
   ========================================================================== */

function electricityBill(units) {
    if (!Number.isFinite(units) || units < 0) {
        throw new RangeError("Units cannot be negative.");
    }

    const fixedCharge = 50;
    let energyCharge;

    if (units <= 100) {
        energyCharge = units * 1.5;
    } else if (units <= 300) {
        energyCharge =
            100 * 1.5 +
            (units - 100) * 2.5;
    } else if (units <= 500) {
        energyCharge =
            100 * 1.5 +
            200 * 2.5 +
            (units - 300) * 4;
    } else {
        energyCharge =
            100 * 1.5 +
            200 * 2.5 +
            200 * 4 +
            (units - 500) * 6;
    }

    return fixedCharge + energyCharge;
}

function electricityDemo() {
    console.log("\n=== 17. Electricity Bill ===");

    for (const units of [0, 50, 100, 101, 300, 301, 500, 501, 1000]) {
        console.log(
            `${units} units -> ₹${electricityBill(units).toFixed(2)}`
        );
    }
}


/* ==========================================================================
   18. SHIPPING DECISION
   ========================================================================== */

function shippingCost(weightKg, express, international) {
    if (!Number.isFinite(weightKg) || weightKg <= 0) {
        throw new RangeError("Weight must be positive.");
    }

    const base = international ? 1500 : 100;

    let weightCharge;

    if (weightKg <= 1) {
        weightCharge = 0;
    } else if (weightKg <= 5) {
        weightCharge = (weightKg - 1) * 50;
    } else {
        weightCharge =
            4 * 50 +
            (weightKg - 5) * 75;
    }

    const expressCharge = express ? 500 : 0;

    return base + weightCharge + expressCharge;
}

function shippingDemo() {
    console.log("\n=== 18. Shipping Decision ===");

    const scenarios = [
        [0.5, false, false],
        [3, false, false],
        [8, true, false],
        [2, true, true]
    ];

    for (const scenario of scenarios) {
        console.log(
            scenario,
            "-> ₹" + shippingCost(...scenario).toFixed(2)
        );
    }
}


/* ==========================================================================
   19. GUARD CLAUSES
   ========================================================================== */

function processPayment(amount, accountActive, balance) {
    // Guard clauses reject invalid cases immediately.
    if (!Number.isFinite(amount) || amount <= 0) {
        return "invalid amount";
    }

    if (!accountActive) {
        return "account inactive";
    }

    if (balance < amount) {
        return "insufficient funds";
    }

    return "payment approved";
}

function guardClauseDemo() {
    console.log("\n=== 19. Guard Clauses ===");

    const cases = [
        [-10, true, 100],
        [50, false, 100],
        [150, true, 100],
        [50, true, 100]
    ];

    for (const testCase of cases) {
        console.log(testCase, "->", processPayment(...testCase));
    }
}


/* ==========================================================================
   20. SHORT-CIRCUIT EVALUATION
   ========================================================================== */

function shortCircuitDemo() {
    console.log("\n=== 20. Short-Circuit Evaluation ===");

    const values = [];

    // If values.length is zero, the second expression is not evaluated.
    if (values.length > 0 && values[0] > 10) {
        console.log("First value is greater than 10.");
    } else {
        console.log("Safe empty-array evaluation.");
    }

    const username = "";
    const displayName = username || "Guest";

    console.log("Display name:", displayName);

    // Nullish coalescing only treats null and undefined as absent.
    const score = 0;
    console.log("Score:", score ?? 50);
}


/* ==========================================================================
   21. MULTI-CRITERIA DECISION
   ========================================================================== */

function loanDecision(age, monthlyIncome, creditScore, existingDebt) {
    if (age < 18) {
        return "rejected: applicant must be an adult";
    }

    if (monthlyIncome <= 0) {
        return "rejected: income must be positive";
    }

    if (creditScore < 300 || creditScore > 900) {
        return "rejected: invalid credit score";
    }

    if (existingDebt < 0) {
        return "rejected: debt cannot be negative";
    }

    const debtToIncome = existingDebt / (monthlyIncome * 12);

    if (
        creditScore >= 750 &&
        monthlyIncome >= 50000 &&
        debtToIncome < 0.40
    ) {
        return "standard approval";
    }

    if (
        creditScore >= 650 &&
        monthlyIncome >= 30000 &&
        debtToIncome < 0.50
    ) {
        return "manual review";
    }

    return "rejected";
}

function loanDemo() {
    console.log("\n=== 21. Multi-Criteria Decision ===");

    const applicants = [
        [30, 80000, 780, 100000],
        [25, 40000, 680, 150000],
        [17, 50000, 800, 10000],
        [40, 20000, 600, 50000]
    ];

    for (const applicant of applicants) {
        console.log(
            applicant,
            "->",
            loanDecision(...applicant)
        );
    }
}


/* ==========================================================================
   22. STRUCTURED BILLING SYSTEM
   ========================================================================== */

class Customer {
    constructor(age, member, premiumMember) {
        this.age = age;
        this.member = member;
        this.premiumMember = premiumMember;
    }
}

class Product {
    constructor(name, price, quantity) {
        this.name = name;
        this.price = price;
        this.quantity = quantity;
    }
}

function createInvoice(customer, products, taxRate = 0.18) {
    if (!Array.isArray(products) || products.length === 0) {
        throw new Error("At least one product is required.");
    }

    let subtotal = 0;

    for (const product of products) {
        if (!Number.isFinite(product.price) || product.price < 0) {
            throw new RangeError(
                `Invalid price for ${product.name}.`
            );
        }

        if (!Number.isInteger(product.quantity) || product.quantity <= 0) {
            throw new RangeError(
                `Invalid quantity for ${product.name}.`
            );
        }

        subtotal += product.price * product.quantity;
    }

    let discountRate = 0;

    if (customer.premiumMember) {
        discountRate = 0.15;
    } else if (customer.member && subtotal >= 5000) {
        discountRate = 0.10;
    }

    if (customer.age >= 60) {
        discountRate += 0.05;
    }

    discountRate = Math.min(discountRate, 0.20);

    const discount = subtotal * discountRate;
    const taxableAmount = subtotal - discount;
    const tax = taxableAmount * taxRate;
    const total = taxableAmount + tax;

    let message;

    if (discountRate >= 0.20) {
        message = "Maximum discount applied.";
    } else if (discountRate > 0) {
        message = "Discount applied.";
    } else {
        message = "No discount applied.";
    }

    return {
        subtotal,
        discount,
        tax,
        total,
        message
    };
}

function invoiceDemo() {
    console.log("\n=== 22. Structured Billing Case Study ===");

    const customer = new Customer(62, true, true);

    const products = [
        new Product("Laptop", 60000, 1),
        new Product("Keyboard", 2500, 1),
        new Product("Mouse", 1500, 2)
    ];

    const invoice = createInvoice(customer, products);

    console.log(`Subtotal: ₹${invoice.subtotal.toFixed(2)}`);
    console.log(`Discount: ₹${invoice.discount.toFixed(2)}`);
    console.log(`Tax:      ₹${invoice.tax.toFixed(2)}`);
    console.log(`Total:    ₹${invoice.total.toFixed(2)}`);
    console.log("Decision:", invoice.message);
}


/* ==========================================================================
   23. TESTING
   ========================================================================== */

function runTests() {
    console.log("\n=== 23. Tests ===");

    console.assert(calculateGrade(100) === "A");
    console.assert(calculateGrade(90) === "A");
    console.assert(calculateGrade(89.99) === "B");
    console.assert(calculateGrade(80) === "B");
    console.assert(calculateGrade(79.99) === "C");
    console.assert(calculateGrade(0) === "F");

    console.assert(isLeapYear(2000) === true);
    console.assert(isLeapYear(1900) === false);
    console.assert(isLeapYear(2024) === true);
    console.assert(isLeapYear(2025) === false);

    console.assert(isValidTriangle(3, 4, 5) === true);
    console.assert(isValidTriangle(1, 2, 3) === false);

    console.assert(classifyTriangle(3, 3, 3) === "equilateral");
    console.assert(classifyTriangle(3, 3, 4) === "isosceles");
    console.assert(classifyTriangle(3, 4, 5) === "scalene");

    console.assert(classifyAge(12) === "child");
    console.assert(classifyAge(13) === "teenager");
    console.assert(classifyAge(18) === "adult");
    console.assert(classifyAge(60) === "senior");

    console.log("All assertions completed.");
}


/* ==========================================================================
   24. MAIN
   ========================================================================== */

function main() {
    console.log("=".repeat(72));
    console.log("DAY 3 — CONDITIONS");
    console.log("=".repeat(72));

    basicIfExamples();
    ifElseExamples();
    elseIfExamples();
    comparisonExamples();
    logicalOperatorExamples();
    compoundConditionExamples();
    nestedConditionExamples();
    truthinessExamples();
    conditionalExpressionExamples();
    gradeDemo();
    leapYearDemo();
    numberClassificationDemo();
    triangleDemo();
    largestDemo();
    billingDemo();
    ageDemo();
    electricityDemo();
    shippingDemo();
    guardClauseDemo();
    shortCircuitDemo();
    loanDemo();
    invoiceDemo();
    runTests();

    console.log("\n" + "=".repeat(72));
    console.log("CONDITION STUDY COMPLETE");
    console.log("=".repeat(72));
}

main();
