/*
============================================================
DAY 1 - VARIABLES, DATA TYPES, INPUT/OUTPUT
ADVANCED JAVASCRIPT PRACTICE PROGRAMS
============================================================

Topics covered:
1. Variables and constants
2. Numbers
3. Strings
4. Boolean values
5. Arrays
6. Objects
7. User input
8. Type conversion
9. Arithmetic operations
10. String processing
11. Basic calculations
12. Financial calculations
13. Student result processing
14. Employee salary calculation
15. Electricity bill calculation
16. Shopping bill generation
17. Banking transaction calculation
18. BMI calculation
19. Time conversion
20. Date calculations
21. Data validation
22. Multi-step calculations
23. Mini record systems
24. Statistics
25. Real-world data processing

Run with:
    node day1_variables_datatypes_io.js
============================================================
*/

const readline = require("readline");

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function ask(question) {
    return new Promise(resolve => {
        rl.question(question, answer => {
            resolve(answer.trim());
        });
    });
}

function line() {
    console.log("=".repeat(70));
}

function section(title) {
    console.log("\n");
    line();
    console.log(title);
    line();
}


/*
============================================================
PROGRAM 1
Personal Information
============================================================
*/

async function program1() {
    section("PROGRAM 1 - PERSONAL INFORMATION");

    const name = await ask("Enter your name: ");
    const age = Number(await ask("Enter your age: "));
    const city = await ask("Enter your city: ");
    const profession = await ask("Enter your profession: ");

    console.log("\nPersonal Information");
    console.log("Name:", name);
    console.log("Age:", age);
    console.log("City:", city);
    console.log("Profession:", profession);
}


/*
============================================================
PROGRAM 2
Basic Arithmetic Calculator
============================================================
*/

async function program2() {
    section("PROGRAM 2 - BASIC ARITHMETIC CALCULATOR");

    const a = Number(await ask("Enter first number: "));
    const b = Number(await ask("Enter second number: "));

    console.log("\nResults");
    console.log("Addition:", a + b);
    console.log("Subtraction:", a - b);
    console.log("Multiplication:", a * b);

    if (b !== 0) {
        console.log("Division:", a / b);
        console.log("Remainder:", a % b);
    } else {
        console.log("Division: Cannot divide by zero");
        console.log("Remainder: Cannot divide by zero");
    }

    console.log("Power:", a ** b);
}


/*
============================================================
PROGRAM 3
Temperature Conversion
============================================================
*/

async function program3() {
    section("PROGRAM 3 - TEMPERATURE CONVERSION");

    const celsius = Number(await ask("Enter temperature in Celsius: "));

    const fahrenheit = (celsius * 9 / 5) + 32;
    const kelvin = celsius + 273.15;

    console.log("\nTemperature Conversion");
    console.log("Celsius:", celsius);
    console.log("Fahrenheit:", fahrenheit.toFixed(2));
    console.log("Kelvin:", kelvin.toFixed(2));
}


/*
============================================================
PROGRAM 4
Simple Interest
============================================================
*/

async function program4() {
    section("PROGRAM 4 - SIMPLE INTEREST");

    const principal = Number(await ask("Enter principal amount: "));
    const rate = Number(await ask("Enter annual interest rate (%): "));
    const time = Number(await ask("Enter time in years: "));

    const interest = (principal * rate * time) / 100;
    const total = principal + interest;

    console.log("\nFinancial Calculation");
    console.log("Principal:", principal);
    console.log("Interest:", interest.toFixed(2));
    console.log("Total Amount:", total.toFixed(2));
}


/*
============================================================
PROGRAM 5
Compound Interest
============================================================
*/

async function program5() {
    section("PROGRAM 5 - COMPOUND INTEREST");

    const principal = Number(await ask("Enter principal amount: "));
    const annualRate = Number(await ask("Enter annual interest rate (%): "));
    const years = Number(await ask("Enter number of years: "));
    const frequency = Number(
        await ask("Enter compounding frequency per year: ")
    );

    const rate = annualRate / 100;

    const amount =
        principal *
        Math.pow(
            1 + rate / frequency,
            frequency * years
        );

    const interest = amount - principal;

    console.log("\nCompound Interest Result");
    console.log("Principal:", principal.toFixed(2));
    console.log("Interest:", interest.toFixed(2));
    console.log("Final Amount:", amount.toFixed(2));
}


/*
============================================================
PROGRAM 6
Student Marks and Percentage
============================================================
*/

async function program6() {
    section("PROGRAM 6 - STUDENT MARKS");

    const name = await ask("Enter student name: ");

    const mathematics = Number(await ask("Mathematics marks: "));
    const physics = Number(await ask("Physics marks: "));
    const chemistry = Number(await ask("Chemistry marks: "));
    const computer = Number(await ask("Computer Science marks: "));
    const english = Number(await ask("English marks: "));

    const total =
        mathematics +
        physics +
        chemistry +
        computer +
        english;

    const percentage = total / 5;

    console.log("\nStudent Result");
    console.log("Student:", name);
    console.log("Total Marks:", total);
    console.log("Percentage:", percentage.toFixed(2) + "%");
}


/*
============================================================
PROGRAM 7
Student Result With Grade
============================================================
*/

async function program7() {
    section("PROGRAM 7 - STUDENT RESULT AND GRADE");

    const name = await ask("Enter student name: ");

    const marks = [];

    for (let i = 1; i <= 5; i++) {
        marks.push(
            Number(await ask(`Enter marks for subject ${i}: `))
        );
    }

    const total = marks.reduce((sum, mark) => sum + mark, 0);
    const percentage = total / marks.length;

    let grade;

    if (percentage >= 90) {
        grade = "A+";
    } else if (percentage >= 80) {
        grade = "A";
    } else if (percentage >= 70) {
        grade = "B";
    } else if (percentage >= 60) {
        grade = "C";
    } else if (percentage >= 50) {
        grade = "D";
    } else {
        grade = "F";
    }

    console.log("\nResult");
    console.log("Name:", name);
    console.log("Marks:", marks);
    console.log("Total:", total);
    console.log("Percentage:", percentage.toFixed(2) + "%");
    console.log("Grade:", grade);
}


/*
============================================================
PROGRAM 8
Employee Salary Calculation
============================================================
*/

async function program8() {
    section("PROGRAM 8 - EMPLOYEE SALARY");

    const employeeName = await ask("Employee name: ");
    const basicSalary = Number(await ask("Basic salary: "));

    const hra = basicSalary * 0.20;
    const da = basicSalary * 0.10;
    const bonus = basicSalary * 0.05;

    const grossSalary =
        basicSalary +
        hra +
        da +
        bonus;

    const tax = grossSalary * 0.10;

    const netSalary = grossSalary - tax;

    console.log("\nSalary Statement");
    console.log("Employee:", employeeName);
    console.log("Basic Salary:", basicSalary.toFixed(2));
    console.log("HRA:", hra.toFixed(2));
    console.log("DA:", da.toFixed(2));
    console.log("Bonus:", bonus.toFixed(2));
    console.log("Gross Salary:", grossSalary.toFixed(2));
    console.log("Tax:", tax.toFixed(2));
    console.log("Net Salary:", netSalary.toFixed(2));
}


/*
============================================================
PROGRAM 9
Electricity Bill
============================================================
*/

async function program9() {
    section("PROGRAM 9 - ELECTRICITY BILL");

    const units = Number(await ask("Enter electricity units consumed: "));

    let bill = 0;

    if (units <= 100) {
        bill = units * 5;
    } else if (units <= 200) {
        bill =
            (100 * 5) +
            ((units - 100) * 7);
    } else {
        bill =
            (100 * 5) +
            (100 * 7) +
            ((units - 200) * 10);
    }

    const fixedCharge = 100;
    const finalBill = bill + fixedCharge;

    console.log("\nElectricity Bill");
    console.log("Units:", units);
    console.log("Energy Charge:", bill.toFixed(2));
    console.log("Fixed Charge:", fixedCharge.toFixed(2));
    console.log("Final Bill:", finalBill.toFixed(2));
}


/*
============================================================
PROGRAM 10
Shopping Bill
============================================================
*/

async function program10() {
    section("PROGRAM 10 - SHOPPING BILL");

    const item1 = await ask("Item 1 name: ");
    const price1 = Number(await ask("Item 1 price: "));
    const quantity1 = Number(await ask("Item 1 quantity: "));

    const item2 = await ask("Item 2 name: ");
    const price2 = Number(await ask("Item 2 price: "));
    const quantity2 = Number(await ask("Item 2 quantity: "));

    const item3 = await ask("Item 3 name: ");
    const price3 = Number(await ask("Item 3 price: "));
    const quantity3 = Number(await ask("Item 3 quantity: "));

    const total1 = price1 * quantity1;
    const total2 = price2 * quantity2;
    const total3 = price3 * quantity3;

    const subtotal = total1 + total2 + total3;
    const tax = subtotal * 0.18;
    const finalAmount = subtotal + tax;

    console.log("\nShopping Bill");
    console.log("---------------------------------------------");
    console.log(item1, ":", total1.toFixed(2));
    console.log(item2, ":", total2.toFixed(2));
    console.log(item3, ":", total3.toFixed(2));
    console.log("---------------------------------------------");
    console.log("Subtotal:", subtotal.toFixed(2));
    console.log("GST:", tax.toFixed(2));
    console.log("Final Amount:", finalAmount.toFixed(2));
}


/*
============================================================
PROGRAM 11
BMI Calculator
============================================================
*/

async function program11() {
    section("PROGRAM 11 - BMI CALCULATOR");

    const weight = Number(await ask("Enter weight in kilograms: "));
    const height = Number(await ask("Enter height in meters: "));

    if (height <= 0) {
        console.log("Height must be greater than zero.");
        return;
    }

    const bmi = weight / (height * height);

    console.log("\nBMI Result");
    console.log("Weight:", weight, "kg");
    console.log("Height:", height, "m");
    console.log("BMI:", bmi.toFixed(2));

    if (bmi < 18.5) {
        console.log("Category: Underweight");
    } else if (bmi < 25) {
        console.log("Category: Normal range");
    } else if (bmi < 30) {
        console.log("Category: Overweight");
    } else {
        console.log("Category: Obesity range");
    }
}


/*
============================================================
PROGRAM 12
Age Calculator
============================================================
*/

async function program12() {
    section("PROGRAM 12 - AGE CALCULATOR");

    const birthYear = Number(await ask("Enter your birth year: "));
    const currentYear = new Date().getFullYear();

    const age = currentYear - birthYear;

    console.log("\nAge Information");
    console.log("Birth Year:", birthYear);
    console.log("Current Year:", currentYear);
    console.log("Approximate Age:", age);
}


/*
============================================================
PROGRAM 13
Time Conversion
============================================================
*/

async function program13() {
    section("PROGRAM 13 - TIME CONVERSION");

    const seconds = Number(
        await ask("Enter total number of seconds: ")
    );

    const hours = Math.floor(seconds / 3600);
    const remainingSeconds = seconds % 3600;

    const minutes = Math.floor(remainingSeconds / 60);
    const finalSeconds = remainingSeconds % 60;

    console.log("\nTime");
    console.log("Hours:", hours);
    console.log("Minutes:", minutes);
    console.log("Seconds:", finalSeconds);

    console.log(
        `Formatted Time: ${hours}h ${minutes}m ${finalSeconds}s`
    );
}


/*
============================================================
PROGRAM 14
Distance Converter
============================================================
*/

async function program14() {
    section("PROGRAM 14 - DISTANCE CONVERTER");

    const kilometers = Number(
        await ask("Enter distance in kilometers: ")
    );

    const meters = kilometers * 1000;
    const centimeters = kilometers * 100000;
    const miles = kilometers * 0.621371;
    const feet = kilometers * 3280.84;

    console.log("\nDistance Conversion");
    console.log("Kilometers:", kilometers);
    console.log("Meters:", meters);
    console.log("Centimeters:", centimeters);
    console.log("Miles:", miles.toFixed(4));
    console.log("Feet:", feet.toFixed(2));
}


/*
============================================================
PROGRAM 15
Currency Breakdown
============================================================
*/

async function program15() {
    section("PROGRAM 15 - CURRENCY BREAKDOWN");

    const amount = Number(
        await ask("Enter amount in rupees: ")
    );

    const notes = [500, 200, 100, 50, 20, 10, 5, 2, 1];

    let remaining = amount;

    console.log("\nCurrency Breakdown");

    for (const note of notes) {
        const count = Math.floor(remaining / note);

        if (count > 0) {
            console.log(`₹${note}: ${count}`);
            remaining %= note;
        }
    }
}


/*
============================================================
PROGRAM 16
Average, Minimum and Maximum
============================================================
*/

async function program16() {
    section("PROGRAM 16 - BASIC STATISTICS");

    const count = Number(
        await ask("How many numbers do you want to enter? ")
    );

    const numbers = [];

    for (let i = 0; i < count; i++) {
        const value = Number(
            await ask(`Enter number ${i + 1}: `)
        );

        numbers.push(value);
    }

    const sum = numbers.reduce(
        (total, value) => total + value,
        0
    );

    const average = sum / numbers.length;
    const minimum = Math.min(...numbers);
    const maximum = Math.max(...numbers);

    console.log("\nStatistics");
    console.log("Numbers:", numbers);
    console.log("Sum:", sum);
    console.log("Average:", average);
    console.log("Minimum:", minimum);
    console.log("Maximum:", maximum);
}


/*
============================================================
PROGRAM 17
Bank Account Simulation
============================================================
*/

async function program17() {
    section("PROGRAM 17 - BANK ACCOUNT");

    const accountHolder = await ask("Account holder name: ");
    let balance = Number(await ask("Opening balance: "));

    const deposit = Number(
        await ask("Deposit amount: ")
    );

    const withdrawal = Number(
        await ask("Withdrawal amount: ")
    );

    balance += deposit;

    if (withdrawal <= balance) {
        balance -= withdrawal;
    } else {
        console.log("Withdrawal exceeds available balance.");
    }

    console.log("\nBank Account");
    console.log("Account Holder:", accountHolder);
    console.log("Deposit:", deposit);
    console.log("Withdrawal:", withdrawal);
    console.log("Final Balance:", balance.toFixed(2));
}


/*
============================================================
PROGRAM 18
Loan EMI Calculation
============================================================
*/

async function program18() {
    section("PROGRAM 18 - LOAN EMI CALCULATOR");

    const principal = Number(
        await ask("Enter loan amount: ")
    );

    const annualRate = Number(
        await ask("Enter annual interest rate (%): ")
    );

    const years = Number(
        await ask("Enter loan duration in years: ")
    );

    const monthlyRate = annualRate / 12 / 100;
    const months = years * 12;

    if (monthlyRate === 0) {
        const emi = principal / months;

        console.log("Monthly EMI:", emi.toFixed(2));
        return;
    }

    const emi =
        principal *
        monthlyRate *
        Math.pow(1 + monthlyRate, months) /
        (Math.pow(1 + monthlyRate, months) - 1);

    const totalPayment = emi * months;
    const totalInterest = totalPayment - principal;

    console.log("\nLoan Summary");
    console.log("Loan Amount:", principal.toFixed(2));
    console.log("Monthly EMI:", emi.toFixed(2));
    console.log("Total Payment:", totalPayment.toFixed(2));
    console.log("Total Interest:", totalInterest.toFixed(2));
}


/*
============================================================
PROGRAM 19
Shopping Discount System
============================================================
*/

async function program19() {
    section("PROGRAM 19 - DISCOUNT CALCULATOR");

    const amount = Number(
        await ask("Enter shopping amount: ")
    );

    let discountRate;

    if (amount >= 100000) {
        discountRate = 20;
    } else if (amount >= 50000) {
        discountRate = 15;
    } else if (amount >= 20000) {
        discountRate = 10;
    } else if (amount >= 10000) {
        discountRate = 5;
    } else {
        discountRate = 0;
    }

    const discount = amount * discountRate / 100;
    const finalAmount = amount - discount;

    console.log("\nDiscount Summary");
    console.log("Original Amount:", amount.toFixed(2));
    console.log("Discount Rate:", discountRate + "%");
    console.log("Discount:", discount.toFixed(2));
    console.log("Final Amount:", finalAmount.toFixed(2));
}


/*
============================================================
PROGRAM 20
Employee Performance Record
============================================================
*/

async function program20() {
    section("PROGRAM 20 - EMPLOYEE PERFORMANCE");

    const name = await ask("Employee name: ");
    const department = await ask("Department: ");

    const projects = Number(
        await ask("Number of projects completed: ")
    );

    const rating = Number(
        await ask("Performance rating out of 5: ")
    );

    const experience = Number(
        await ask("Years of experience: ")
    );

    const employee = {
        name: name,
        department: department,
        projectsCompleted: projects,
        performanceRating: rating,
        experienceYears: experience
    };

    console.log("\nEmployee Record");
    console.log(employee);

    const score =
        projects * 2 +
        rating * 10 +
        experience * 3;

    console.log("Performance Score:", score);
}


/*
============================================================
PROGRAM 21
Product Inventory Record
============================================================
*/

async function program21() {
    section("PROGRAM 21 - PRODUCT INVENTORY");

    const productName = await ask("Product name: ");
    const productCode = await ask("Product code: ");

    const price = Number(
        await ask("Product price: ")
    );

    const quantity = Number(
        await ask("Quantity available: ")
    );

    const inventoryValue = price * quantity;

    const product = {
        code: productCode,
        name: productName,
        price: price,
        quantity: quantity,
        inventoryValue: inventoryValue
    };

    console.log("\nProduct Record");
    console.log(product);

    if (quantity === 0) {
        console.log("Stock Status: Out of stock");
    } else if (quantity < 10) {
        console.log("Stock Status: Low stock");
    } else {
        console.log("Stock Status: Available");
    }
}


/*
============================================================
PROGRAM 22
Data Type Explorer
============================================================
*/

async function program22() {
    section("PROGRAM 22 - JAVASCRIPT DATA TYPES");

    const name = "Atul";
    const age = 30;
    const isStudent = true;
    const salary = 75000.50;
    const skills = ["Python", "JavaScript", "Git"];
    const person = {
        name: "Atul",
        age: 30
    };
    const emptyValue = null;
    let undefinedValue;

    console.log("name:", name, "| Type:", typeof name);
    console.log("age:", age, "| Type:", typeof age);
    console.log("isStudent:", isStudent, "| Type:", typeof isStudent);
    console.log("salary:", salary, "| Type:", typeof salary);
    console.log("skills:", skills, "| Type:", typeof skills);
    console.log("person:", person, "| Type:", typeof person);
    console.log("null:", emptyValue, "| Type:", typeof emptyValue);
    console.log(
        "undefined:",
        undefinedValue,
        "| Type:",
        typeof undefinedValue
    );
}


/*
============================================================
PROGRAM 23
String Processing
============================================================
*/

async function program23() {
    section("PROGRAM 23 - STRING PROCESSING");

    const firstName = await ask("Enter first name: ");
    const lastName = await ask("Enter last name: ");

    const fullName = `${firstName} ${lastName}`;

    console.log("\nString Information");
    console.log("Full Name:", fullName);
    console.log("Uppercase:", fullName.toUpperCase());
    console.log("Lowercase:", fullName.toLowerCase());
    console.log("Length:", fullName.length);
    console.log("First Character:", fullName[0]);
    console.log(
        "Last Character:",
        fullName[fullName.length - 1]
    );
}


/*
============================================================
PROGRAM 24
Percentage Change
============================================================
*/

async function program24() {
    section("PROGRAM 24 - PERCENTAGE CHANGE");

    const oldValue = Number(
        await ask("Enter old value: ")
    );

    const newValue = Number(
        await ask("Enter new value: ")
    );

    if (oldValue === 0) {
        console.log("Old value cannot be zero.");
        return;
    }

    const change =
        ((newValue - oldValue) / oldValue) * 100;

    console.log("\nPercentage Change");
    console.log("Old Value:", oldValue);
    console.log("New Value:", newValue);
    console.log("Change:", change.toFixed(2) + "%");

    if (change > 0) {
        console.log("Direction: Increase");
    } else if (change < 0) {
        console.log("Direction: Decrease");
    } else {
        console.log("Direction: No change");
    }
}


/*
============================================================
PROGRAM 25
Investment Return Calculator
============================================================
*/

async function program25() {
    section("PROGRAM 25 - INVESTMENT RETURN");

    const investment = Number(
        await ask("Initial investment: ")
    );

    const finalValue = Number(
        await ask("Final investment value: ")
    );

    const years = Number(
        await ask("Investment duration in years: ")
    );

    const profit = finalValue - investment;
    const returnPercentage =
        (profit / investment) * 100;

    const annualizedReturn =
        years > 0
            ? (Math.pow(finalValue / investment, 1 / years) - 1) * 100
            : 0;

    console.log("\nInvestment Analysis");
    console.log("Initial Investment:", investment.toFixed(2));
    console.log("Final Value:", finalValue.toFixed(2));
    console.log("Profit/Loss:", profit.toFixed(2));
    console.log(
        "Total Return:",
        returnPercentage.toFixed(2) + "%"
    );
    console.log(
        "Annualized Return:",
        annualizedReturn.toFixed(2) + "%"
    );
}


/*
============================================================
PROGRAM 26
Student Object Record
============================================================
*/

async function program26() {
    section("PROGRAM 26 - STUDENT OBJECT");

    const student = {
        name: await ask("Student name: "),
        rollNumber: await ask("Roll number: "),
        age: Number(await ask("Age: ")),
        course: await ask("Course: "),
        marks: Number(await ask("Marks: "))
    };

    console.log("\nStudent Object");
    console.log(student);

    console.log("\nIndividual Properties");
    console.log("Name:", student.name);
    console.log("Roll Number:", student.rollNumber);
    console.log("Age:", student.age);
    console.log("Course:", student.course);
    console.log("Marks:", student.marks);
}


/*
============================================================
PROGRAM 27
Multiple Student Records
============================================================
*/

async function program27() {
    section("PROGRAM 27 - MULTIPLE STUDENT RECORDS");

    const students = [];

    const count = Number(
        await ask("How many students? ")
    );

    for (let i = 0; i < count; i++) {
        console.log(`\nStudent ${i + 1}`);

        const name = await ask("Name: ");
        const age = Number(await ask("Age: "));
        const marks = Number(await ask("Marks: "));

        students.push({
            name,
            age,
            marks
        });
    }

    console.log("\nAll Students");

    for (const student of students) {
        console.log(
            `${student.name} | Age: ${student.age} | Marks: ${student.marks}`
        );
    }
}


/*
============================================================
PROGRAM 28
Profit and Loss
============================================================
*/

async function program28() {
    section("PROGRAM 28 - PROFIT AND LOSS");

    const costPrice = Number(
        await ask("Enter cost price: ")
    );

    const sellingPrice = Number(
        await ask("Enter selling price: ")
    );

    const difference = sellingPrice - costPrice;

    console.log("\nTransaction Analysis");

    if (difference > 0) {
        const profit = difference;
        const profitPercentage =
            (profit / costPrice) * 100;

        console.log("Result: Profit");
        console.log("Profit:", profit.toFixed(2));
        console.log(
            "Profit Percentage:",
            profitPercentage.toFixed(2) + "%"
        );
    } else if (difference < 0) {
        const loss = Math.abs(difference);
        const lossPercentage =
            (loss / costPrice) * 100;

        console.log("Result: Loss");
        console.log("Loss:", loss.toFixed(2));
        console.log(
            "Loss Percentage:",
            lossPercentage.toFixed(2) + "%"
        );
    } else {
        console.log("Result: No Profit, No Loss");
    }
}


/*
============================================================
PROGRAM 29
Multi-Subject Academic Report
============================================================
*/

async function program29() {
    section("PROGRAM 29 - ACADEMIC REPORT");

    const name = await ask("Student name: ");

    const subjects = [
        "Mathematics",
        "Physics",
        "Chemistry",
        "Computer Science",
        "English",
        "Data Structures",
        "Database Systems"
    ];

    const marks = {};

    for (const subject of subjects) {
        marks[subject] = Number(
            await ask(`${subject} marks: `)
        );
    }

    let total = 0;

    for (const subject of subjects) {
        total += marks[subject];
    }

    const percentage = total / subjects.length;

    console.log("\nAcademic Report");
    console.log("Student:", name);

    for (const subject of subjects) {
        console.log(
            `${subject}: ${marks[subject]}`
        );
    }

    console.log("Total:", total);
    console.log(
        "Average:",
        percentage.toFixed(2)
    );
}


/*
============================================================
PROGRAM 30
Personal Financial Summary
============================================================
*/

async function program30() {
    section("PROGRAM 30 - PERSONAL FINANCIAL SUMMARY");

    const salary = Number(
        await ask("Monthly salary: ")
    );

    const rent = Number(
        await ask("Monthly rent: ")
    );

    const food = Number(
        await ask("Monthly food expense: ")
    );

    const transport = Number(
        await ask("Monthly transport expense: ")
    );

    const utilities = Number(
        await ask("Monthly utilities: ")
    );

    const investments = Number(
        await ask("Monthly investments: ")
    );

    const otherExpenses = Number(
        await ask("Other monthly expenses: ")
    );

    const totalExpenses =
        rent +
        food +
        transport +
        utilities +
        investments +
        otherExpenses;

    const remaining = salary - totalExpenses;

    const savingsRate =
        salary > 0
            ? (remaining / salary) * 100
            : 0;

    console.log("\nFinancial Summary");
    console.log("---------------------------------------");
    console.log("Monthly Salary:", salary.toFixed(2));
    console.log("Rent:", rent.toFixed(2));
    console.log("Food:", food.toFixed(2));
    console.log("Transport:", transport.toFixed(2));
    console.log("Utilities:", utilities.toFixed(2));
    console.log("Investments:", investments.toFixed(2));
    console.log("Other Expenses:", otherExpenses.toFixed(2));
    console.log("---------------------------------------");
    console.log(
        "Total Expenses:",
        totalExpenses.toFixed(2)
    );
    console.log(
        "Remaining Amount:",
        remaining.toFixed(2)
    );
    console.log(
        "Savings Rate:",
        savingsRate.toFixed(2) + "%"
    );
}


/*
============================================================
PROGRAM 31
Simple Data Validation
============================================================
*/

async function program31() {
    section("PROGRAM 31 - DATA VALIDATION");

    const name = await ask("Enter your name: ");
    const age = Number(await ask("Enter your age: "));
    const email = await ask("Enter your email: ");

    const validName =
        name.length >= 2;

    const validAge =
        Number.isInteger(age) &&
        age >= 0 &&
        age <= 120;

    const validEmail =
        email.includes("@") &&
        email.includes(".");

    console.log("\nValidation Results");

    console.log(
        "Name:",
        validName ? "Valid" : "Invalid"
    );

    console.log(
        "Age:",
        validAge ? "Valid" : "Invalid"
    );

    console.log(
        "Email:",
        validEmail ? "Valid" : "Invalid"
    );
}


/*
============================================================
PROGRAM 32
Number Analysis
============================================================
*/

async function program32() {
    section("PROGRAM 32 - NUMBER ANALYSIS");

    const number = Number(
        await ask("Enter a number: ")
    );

    console.log("\nNumber Analysis");
    console.log("Number:", number);
    console.log("Absolute Value:", Math.abs(number));
    console.log("Square:", number ** 2);
    console.log("Cube:", number ** 3);
    console.log("Square Root:", Math.sqrt(Math.abs(number)));

    console.log(
        "Integer:",
        Number.isInteger(number)
    );

    console.log(
        "Positive:",
        number > 0
    );

    console.log(
        "Negative:",
        number < 0
    );

    console.log(
        "Zero:",
        number === 0
    );

    console.log(
        "Even:",
        number % 2 === 0
    );

    console.log(
        "Odd:",
        number % 2 !== 0
    );
}


/*
============================================================
PROGRAM 33
Data Conversion
============================================================
*/

async function program33() {
    section("PROGRAM 33 - DATA TYPE CONVERSION");

    const stringNumber = await ask(
        "Enter a number as text: "
    );

    const numberValue = Number(stringNumber);
    const integerValue = parseInt(stringNumber);
    const floatValue = parseFloat(stringNumber);

    console.log("\nConversion Results");

    console.log(
        "Original:",
        stringNumber,
        "| Type:",
        typeof stringNumber
    );

    console.log(
        "Number():",
        numberValue,
        "| Type:",
        typeof numberValue
    );

    console.log(
        "parseInt():",
        integerValue,
        "| Type:",
        typeof integerValue
    );

    console.log(
        "parseFloat():",
        floatValue,
        "| Type:",
        typeof floatValue
    );
}


/*
============================================================
PROGRAM 34
Rectangle and Circle Calculations
============================================================
*/

async function program34() {
    section("PROGRAM 34 - GEOMETRY CALCULATOR");

    const length = Number(
        await ask("Rectangle length: ")
    );

    const width = Number(
        await ask("Rectangle width: ")
    );

    const radius = Number(
        await ask("Circle radius: ")
    );

    const rectangleArea = length * width;

    const rectanglePerimeter =
        2 * (length + width);

    const circleArea =
        Math.PI * radius * radius;

    const circleCircumference =
        2 * Math.PI * radius;

    console.log("\nGeometry Results");

    console.log(
        "Rectangle Area:",
        rectangleArea.toFixed(2)
    );

    console.log(
        "Rectangle Perimeter:",
        rectanglePerimeter.toFixed(2)
    );

    console.log(
        "Circle Area:",
        circleArea.toFixed(2)
    );

    console.log(
        "Circle Circumference:",
        circleCircumference.toFixed(2)
    );
}


/*
============================================================
PROGRAM 35
Complete Personal Profile
============================================================
*/

async function program35() {
    section("PROGRAM 35 - COMPLETE PERSONAL PROFILE");

    const profile = {
        name: await ask("Name: "),
        age: Number(await ask("Age: ")),
        city: await ask("City: "),
        country: await ask("Country: "),
        profession: await ask("Profession: "),
        monthlyIncome: Number(
            await ask("Monthly income: ")
        ),
        yearsExperience: Number(
            await ask("Years of experience: ")
        )
    };

    console.log("\nComplete Profile");
    console.log("---------------------------------------");

    console.log("Name:", profile.name);
    console.log("Age:", profile.age);
    console.log("City:", profile.city);
    console.log("Country:", profile.country);
    console.log("Profession:", profile.profession);
    console.log(
        "Monthly Income:",
        profile.monthlyIncome.toFixed(2)
    );
    console.log(
        "Experience:",
        profile.yearsExperience,
        "years"
    );

    console.log("---------------------------------------");

    const annualIncome =
        profile.monthlyIncome * 12;

    console.log(
        "Estimated Annual Income:",
        annualIncome.toFixed(2)
    );

    console.log(
        "Profile Created:",
        new Date().toLocaleString()
    );
}


/*
============================================================
PROGRAM MENU
============================================================

Change this number to run a particular program.

Examples:

1  = Personal Information
2  = Arithmetic Calculator
3  = Temperature Conversion
...
35 = Complete Personal Profile
============================================================
*/

async function main() {
    console.log("\n");
    line();
    console.log("DAY 1 JAVASCRIPT PRACTICE PROGRAMS");
    line();

    console.log(`
1.  Personal Information
2.  Basic Arithmetic Calculator
3.  Temperature Conversion
4.  Simple Interest
5.  Compound Interest
6.  Student Marks
7.  Student Result and Grade
8.  Employee Salary
9.  Electricity Bill
10. Shopping Bill
11. BMI Calculator
12. Age Calculator
13. Time Conversion
14. Distance Converter
15. Currency Breakdown
16. Basic Statistics
17. Bank Account
18. Loan EMI
19. Discount Calculator
20. Employee Performance
21. Product Inventory
22. JavaScript Data Types
23. String Processing
24. Percentage Change
25. Investment Return
26. Student Object
27. Multiple Student Records
28. Profit and Loss
29. Academic Report
30. Personal Financial Summary
31. Data Validation
32. Number Analysis
33. Data Type Conversion
34. Geometry Calculator
35. Complete Personal Profile
`);

    const choice = Number(
        await ask("Enter program number (1-35): ")
    );

    switch (choice) {
        case 1:
            await program1();
            break;

        case 2:
            await program2();
            break;

        case 3:
            await program3();
            break;

        case 4:
            await program4();
            break;

        case 5:
            await program5();
            break;

        case 6:
            await program6();
            break;

        case 7:
            await program7();
            break;

        case 8:
            await program8();
            break;

        case 9:
            await program9();
            break;

        case 10:
            await program10();
            break;

        case 11:
            await program11();
            break;

        case 12:
            await program12();
            break;

        case 13:
            await program13();
            break;

        case 14:
            await program14();
            break;

        case 15:
            await program15();
            break;

        case 16:
            await program16();
            break;

        case 17:
            await program17();
            break;

        case 18:
            await program18();
            break;

        case 19:
            await program19();
            break;

        case 20:
            await program20();
            break;

        case 21:
            await program21();
            break;

        case 22:
            await program22();
            break;

        case 23:
            await program23();
            break;

        case 24:
            await program24();
            break;

        case 25:
            await program25();
            break;

        case 26:
            await program26();
            break;

        case 27:
            await program27();
            break;

        case 28:
            await program28();
            break;

        case 29:
            await program29();
            break;

        case 30:
            await program30();
            break;

        case 31:
            await program31();
            break;

        case 32:
            await program32();
            break;

        case 33:
            await program33();
            break;

        case 34:
            await program34();
            break;

        case 35:
            await program35();
            break;

        default:
            console.log("Invalid program number.");
    }

    rl.close();
}

main();
