#include <iostream>
#include <string>
#include <vector>
#include <iomanip>
#include <cmath>
#include <algorithm>
#include <limits>

using namespace std;

/*
============================================================
C++ VARIABLES, DATA TYPES, INPUT/OUTPUT
DIFFERENT AND MORE COMPLEX PRACTICE PROGRAMS
============================================================

Programs:
1. Digital Wallet
2. Employee Payroll
3. Student Performance Analyzer
4. Mobile Data Usage
5. Travel Cost Estimator
6. Restaurant Bill Splitter
7. Fuel Cost Calculator
8. Loan Analysis
9. Product Profit Analyzer
10. Electricity Consumption Analyzer
11. Investment Portfolio Summary
12. Hospital Bill Calculator
13. Exam Statistics
14. Bank Transaction Summary
15. Internet Subscription Calculator
16. Car Resale Value Calculator
17. Monthly Budget Analyzer
18. Manufacturing Cost Calculator
19. Project Cost Estimator
20. Personal Financial Dashboard

Compile:
    g++ day1_different_programs.cpp -o day1

Run:
    ./day1

On Windows:
    .\day1.exe
============================================================
*/

void separator()
{
    cout << string(70, '=') << '\n';
}

void title(const string& name)
{
    cout << '\n';
    separator();
    cout << name << '\n';
    separator();
}


/*
============================================================
PROGRAM 1
DIGITAL WALLET
============================================================
*/

void program1()
{
    title("PROGRAM 1 - DIGITAL WALLET");

    string owner;
    double balance, deposit, withdrawal;

    cout << "Wallet owner: ";
    getline(cin >> ws, owner);

    cout << "Opening balance: ";
    cin >> balance;

    cout << "Deposit amount: ";
    cin >> deposit;

    cout << "Withdrawal amount: ";
    cin >> withdrawal;

    balance += deposit;

    bool withdrawalSuccessful = withdrawal <= balance;

    if (withdrawalSuccessful)
    {
        balance -= withdrawal;
    }

    cout << fixed << setprecision(2);

    cout << "\nWallet Summary\n";
    cout << "Owner: " << owner << '\n';
    cout << "Deposit: " << deposit << '\n';
    cout << "Withdrawal: " << withdrawal << '\n';
    cout << "Withdrawal Status: "
         << (withdrawalSuccessful ? "Successful" : "Rejected")
         << '\n';
    cout << "Final Balance: " << balance << '\n';
}


/*
============================================================
PROGRAM 2
EMPLOYEE PAYROLL
============================================================
*/

void program2()
{
    title("PROGRAM 2 - EMPLOYEE PAYROLL");

    string name;
    double basicSalary;
    double overtimeHours;
    double overtimeRate;

    cout << "Employee name: ";
    getline(cin >> ws, name);

    cout << "Basic salary: ";
    cin >> basicSalary;

    cout << "Overtime hours: ";
    cin >> overtimeHours;

    cout << "Overtime rate per hour: ";
    cin >> overtimeRate;

    double hra = basicSalary * 0.20;
    double da = basicSalary * 0.10;
    double overtimePay = overtimeHours * overtimeRate;

    double grossSalary =
        basicSalary +
        hra +
        da +
        overtimePay;

    double tax = grossSalary * 0.10;
    double netSalary = grossSalary - tax;

    cout << fixed << setprecision(2);

    cout << "\nPayroll Statement\n";
    cout << "Employee: " << name << '\n';
    cout << "Basic Salary: " << basicSalary << '\n';
    cout << "HRA: " << hra << '\n';
    cout << "DA: " << da << '\n';
    cout << "Overtime Pay: " << overtimePay << '\n';
    cout << "Gross Salary: " << grossSalary << '\n';
    cout << "Tax: " << tax << '\n';
    cout << "Net Salary: " << netSalary << '\n';
}


/*
============================================================
PROGRAM 3
STUDENT PERFORMANCE ANALYZER
============================================================
*/

void program3()
{
    title("PROGRAM 3 - STUDENT PERFORMANCE ANALYZER");

    string name;
    int subjects;

    cout << "Student name: ";
    getline(cin >> ws, name);

    cout << "Number of subjects: ";
    cin >> subjects;

    vector<double> marks(subjects);

    double total = 0.0;
    double highest = -1.0;
    double lowest = 101.0;

    for (int i = 0; i < subjects; ++i)
    {
        cout << "Marks for subject " << i + 1 << ": ";
        cin >> marks[i];

        total += marks[i];

        highest = max(highest, marks[i]);
        lowest = min(lowest, marks[i]);
    }

    double average = total / subjects;

    cout << fixed << setprecision(2);

    cout << "\nPerformance Report\n";
    cout << "Student: " << name << '\n';
    cout << "Total: " << total << '\n';
    cout << "Average: " << average << '\n';
    cout << "Highest: " << highest << '\n';
    cout << "Lowest: " << lowest << '\n';

    if (average >= 90)
        cout << "Performance Level: Excellent\n";
    else if (average >= 75)
        cout << "Performance Level: Very Good\n";
    else if (average >= 60)
        cout << "Performance Level: Good\n";
    else if (average >= 50)
        cout << "Performance Level: Average\n";
    else
        cout << "Performance Level: Needs Improvement\n";
}


/*
============================================================
PROGRAM 4
MOBILE DATA USAGE
============================================================
*/

void program4()
{
    title("PROGRAM 4 - MOBILE DATA USAGE");

    double monthlyLimit;
    double usedData;

    cout << "Monthly data limit (GB): ";
    cin >> monthlyLimit;

    cout << "Data used (GB): ";
    cin >> usedData;

    double remaining = monthlyLimit - usedData;
    double usagePercentage =
        (usedData / monthlyLimit) * 100.0;

    cout << fixed << setprecision(2);

    cout << "\nData Usage Report\n";
    cout << "Monthly Limit: " << monthlyLimit << " GB\n";
    cout << "Used: " << usedData << " GB\n";
    cout << "Remaining: " << remaining << " GB\n";
    cout << "Usage: " << usagePercentage << "%\n";

    if (usedData > monthlyLimit)
        cout << "Status: Data limit exceeded\n";
    else if (usagePercentage >= 90)
        cout << "Status: Almost exhausted\n";
    else if (usagePercentage >= 70)
        cout << "Status: High usage\n";
    else
        cout << "Status: Normal usage\n";
}


/*
============================================================
PROGRAM 5
TRAVEL COST ESTIMATOR
============================================================
*/

void program5()
{
    title("PROGRAM 5 - TRAVEL COST ESTIMATOR");

    double distance;
    double mileage;
    double fuelPrice;
    double hotelCost;
    int nights;
    double foodPerDay;
    int days;

    cout << "Travel distance (km): ";
    cin >> distance;

    cout << "Vehicle mileage (km/litre): ";
    cin >> mileage;

    cout << "Fuel price per litre: ";
    cin >> fuelPrice;

    cout << "Hotel cost per night: ";
    cin >> hotelCost;

    cout << "Number of nights: ";
    cin >> nights;

    cout << "Food cost per day: ";
    cin >> foodPerDay;

    cout << "Number of travel days: ";
    cin >> days;

    double fuelRequired = distance / mileage;
    double fuelCost = fuelRequired * fuelPrice;
    double totalHotel = hotelCost * nights;
    double totalFood = foodPerDay * days;

    double totalCost =
        fuelCost +
        totalHotel +
        totalFood;

    cout << fixed << setprecision(2);

    cout << "\nTravel Budget\n";
    cout << "Fuel Required: " << fuelRequired << " litres\n";
    cout << "Fuel Cost: " << fuelCost << '\n';
    cout << "Hotel Cost: " << totalHotel << '\n';
    cout << "Food Cost: " << totalFood << '\n';
    cout << "Total Travel Cost: " << totalCost << '\n';
}


/*
============================================================
PROGRAM 6
RESTAURANT BILL SPLITTER
============================================================
*/

void program6()
{
    title("PROGRAM 6 - RESTAURANT BILL SPLITTER");

    double foodBill;
    double taxRate;
    double serviceChargeRate;
    int people;

    cout << "Food bill: ";
    cin >> foodBill;

    cout << "Tax rate (%): ";
    cin >> taxRate;

    cout << "Service charge (%): ";
    cin >> serviceChargeRate;

    cout << "Number of people: ";
    cin >> people;

    double tax = foodBill * taxRate / 100.0;
    double serviceCharge =
        foodBill * serviceChargeRate / 100.0;

    double finalBill =
        foodBill +
        tax +
        serviceCharge;

    double perPerson =
        finalBill / people;

    cout << fixed << setprecision(2);

    cout << "\nRestaurant Bill\n";
    cout << "Food Bill: " << foodBill << '\n';
    cout << "Tax: " << tax << '\n';
    cout << "Service Charge: " << serviceCharge << '\n';
    cout << "Final Bill: " << finalBill << '\n';
    cout << "Per Person: " << perPerson << '\n';
}


/*
============================================================
PROGRAM 7
FUEL COST CALCULATOR
============================================================
*/

void program7()
{
    title("PROGRAM 7 - FUEL COST CALCULATOR");

    double distance;
    double mileage;
    double fuelPrice;

    cout << "Distance travelled (km): ";
    cin >> distance;

    cout << "Vehicle mileage (km/l): ";
    cin >> mileage;

    cout << "Fuel price per litre: ";
    cin >> fuelPrice;

    double fuelConsumed = distance / mileage;
    double totalCost = fuelConsumed * fuelPrice;
    double costPerKm = totalCost / distance;

    cout << fixed << setprecision(2);

    cout << "\nFuel Analysis\n";
    cout << "Distance: " << distance << " km\n";
    cout << "Fuel Consumed: " << fuelConsumed << " litres\n";
    cout << "Total Fuel Cost: " << totalCost << '\n';
    cout << "Cost Per KM: " << costPerKm << '\n';
}


/*
============================================================
PROGRAM 8
LOAN ANALYSIS
============================================================
*/

void program8()
{
    title("PROGRAM 8 - LOAN ANALYSIS");

    double principal;
    double annualRate;
    int years;

    cout << "Loan amount: ";
    cin >> principal;

    cout << "Annual interest rate (%): ";
    cin >> annualRate;

    cout << "Loan duration (years): ";
    cin >> years;

    int months = years * 12;

    double monthlyRate =
        annualRate / 12.0 / 100.0;

    double emi;

    if (monthlyRate == 0)
    {
        emi = principal / months;
    }
    else
    {
        double factor =
            pow(1 + monthlyRate, months);

        emi =
            principal *
            monthlyRate *
            factor /
            (factor - 1);
    }

    double totalPayment = emi * months;
    double totalInterest =
        totalPayment - principal;

    cout << fixed << setprecision(2);

    cout << "\nLoan Analysis\n";
    cout << "Principal: " << principal << '\n';
    cout << "Monthly EMI: " << emi << '\n';
    cout << "Total Payment: " << totalPayment << '\n';
    cout << "Total Interest: " << totalInterest << '\n';
}


/*
============================================================
PROGRAM 9
PRODUCT PROFIT ANALYZER
============================================================
*/

void program9()
{
    title("PROGRAM 9 - PRODUCT PROFIT ANALYZER");

    string productName;
    double costPrice;
    double sellingPrice;
    int quantity;

    cout << "Product name: ";
    getline(cin >> ws, productName);

    cout << "Cost price per unit: ";
    cin >> costPrice;

    cout << "Selling price per unit: ";
    cin >> sellingPrice;

    cout << "Quantity sold: ";
    cin >> quantity;

    double profitPerUnit =
        sellingPrice - costPrice;

    double totalProfit =
        profitPerUnit * quantity;

    double profitMargin =
        (profitPerUnit / sellingPrice) * 100.0;

    cout << fixed << setprecision(2);

    cout << "\nProduct Analysis\n";
    cout << "Product: " << productName << '\n';
    cout << "Profit Per Unit: " << profitPerUnit << '\n';
    cout << "Total Profit: " << totalProfit << '\n';
    cout << "Profit Margin: " << profitMargin << "%\n";

    if (totalProfit > 0)
        cout << "Result: Profitable\n";
    else if (totalProfit < 0)
        cout << "Result: Loss\n";
    else
        cout << "Result: Break-even\n";
}


/*
============================================================
PROGRAM 10
ELECTRICITY CONSUMPTION ANALYZER
============================================================
*/

void program10()
{
    title("PROGRAM 10 - ELECTRICITY CONSUMPTION ANALYZER");

    double units;
    double previousUnits;

    cout << "Previous meter reading: ";
    cin >> previousUnits;

    cout << "Current meter reading: ";
    cin >> units;

    double consumption =
        units - previousUnits;

    double bill = 0;

    if (consumption <= 100)
    {
        bill = consumption * 5;
    }
    else if (consumption <= 200)
    {
        bill =
            100 * 5 +
            (consumption - 100) * 7;
    }
    else
    {
        bill =
            100 * 5 +
            100 * 7 +
            (consumption - 200) * 10;
    }

    double fixedCharge = 100;

    double totalBill =
        bill + fixedCharge;

    cout << fixed << setprecision(2);

    cout << "\nElectricity Analysis\n";
    cout << "Consumption: " << consumption << " units\n";
    cout << "Energy Charge: " << bill << '\n';
    cout << "Fixed Charge: " << fixedCharge << '\n';
    cout << "Total Bill: " << totalBill << '\n';
}


/*
============================================================
PROGRAM 11
INVESTMENT PORTFOLIO SUMMARY
============================================================
*/

void program11()
{
    title("PROGRAM 11 - INVESTMENT PORTFOLIO");

    int investments;

    cout << "Number of investments: ";
    cin >> investments;

    vector<double> invested(investments);
    vector<double> current(investments);

    double totalInvested = 0;
    double totalCurrent = 0;

    for (int i = 0; i < investments; ++i)
    {
        cout << "\nInvestment " << i + 1 << '\n';

        cout << "Amount invested: ";
        cin >> invested[i];

        cout << "Current value: ";
        cin >> current[i];

        totalInvested += invested[i];
        totalCurrent += current[i];
    }

    double profitLoss =
        totalCurrent - totalInvested;

    double returnPercentage =
        (profitLoss / totalInvested) * 100.0;

    cout << fixed << setprecision(2);

    cout << "\nPortfolio Summary\n";
    cout << "Total Invested: " << totalInvested << '\n';
    cout << "Current Value: " << totalCurrent << '\n';
    cout << "Profit/Loss: " << profitLoss << '\n';
    cout << "Return: " << returnPercentage << "%\n";
}


/*
============================================================
PROGRAM 12
HOSPITAL BILL CALCULATOR
============================================================
*/

void program12()
{
    title("PROGRAM 12 - HOSPITAL BILL");

    string patient;
    double consultation;
    double medicines;
    double tests;
    double roomPerDay;
    int days;

    cout << "Patient name: ";
    getline(cin >> ws, patient);

    cout << "Consultation fee: ";
    cin >> consultation;

    cout << "Medicine cost: ";
    cin >> medicines;

    cout << "Test cost: ";
    cin >> tests;

    cout << "Room cost per day: ";
    cin >> roomPerDay;

    cout << "Number of days: ";
    cin >> days;

    double roomCost =
        roomPerDay * days;

    double total =
        consultation +
        medicines +
        tests +
        roomCost;

    cout << fixed << setprecision(2);

    cout << "\nHospital Bill\n";
    cout << "Patient: " << patient << '\n';
    cout << "Consultation: " << consultation << '\n';
    cout << "Medicines: " << medicines << '\n';
    cout << "Tests: " << tests << '\n';
    cout << "Room: " << roomCost << '\n';
    cout << "Total: " << total << '\n';
}


/*
============================================================
PROGRAM 13
EXAM STATISTICS
============================================================
*/

void program13()
{
    title("PROGRAM 13 - EXAM STATISTICS");

    int count;

    cout << "Number of students: ";
    cin >> count;

    vector<double> marks(count);

    double total = 0;
    int passed = 0;
    int failed = 0;

    double highest = -1;
    double lowest = 101;

    for (int i = 0; i < count; ++i)
    {
        cout << "Marks of student "
             << i + 1 << ": ";

        cin >> marks[i];

        total += marks[i];

        highest = max(highest, marks[i]);
        lowest = min(lowest, marks[i]);

        if (marks[i] >= 40)
            passed++;
        else
            failed++;
    }

    double average =
        total / count;

    cout << fixed << setprecision(2);

    cout << "\nExam Statistics\n";
    cout << "Average: " << average << '\n';
    cout << "Highest: " << highest << '\n';
    cout << "Lowest: " << lowest << '\n';
    cout << "Passed: " << passed << '\n';
    cout << "Failed: " << failed << '\n';
}


/*
============================================================
PROGRAM 14
BANK TRANSACTION SUMMARY
============================================================
*/

void program14()
{
    title("PROGRAM 14 - BANK TRANSACTION SUMMARY");

    double openingBalance;
    int transactions;

    cout << "Opening balance: ";
    cin >> openingBalance;

    cout << "Number of transactions: ";
    cin >> transactions;

    double balance = openingBalance;
    double totalDeposits = 0;
    double totalWithdrawals = 0;

    for (int i = 0; i < transactions; ++i)
    {
        int type;
        double amount;

        cout << "\nTransaction " << i + 1 << '\n';
        cout << "1. Deposit\n";
        cout << "2. Withdrawal\n";
        cout << "Choose: ";
        cin >> type;

        cout << "Amount: ";
        cin >> amount;

        if (type == 1)
        {
            balance += amount;
            totalDeposits += amount;
        }
        else if (type == 2)
        {
            if (amount <= balance)
            {
                balance -= amount;
                totalWithdrawals += amount;
            }
            else
            {
                cout << "Insufficient balance.\n";
            }
        }
    }

    cout << fixed << setprecision(2);

    cout << "\nBank Summary\n";
    cout << "Opening Balance: " << openingBalance << '\n';
    cout << "Total Deposits: " << totalDeposits << '\n';
    cout << "Total Withdrawals: " << totalWithdrawals << '\n';
    cout << "Closing Balance: " << balance << '\n';
}


/*
============================================================
PROGRAM 15
INTERNET SUBSCRIPTION
============================================================
*/

void program15()
{
    title("PROGRAM 15 - INTERNET SUBSCRIPTION");

    int plan;
    int months;

    cout << "Select plan:\n";
    cout << "1. Basic  - Rs. 499/month\n";
    cout << "2. Pro    - Rs. 799/month\n";
    cout << "3. Ultra  - Rs. 1299/month\n";

    cout << "Choose plan: ";
    cin >> plan;

    cout << "Number of months: ";
    cin >> months;

    double monthlyPrice = 0;

    switch (plan)
    {
        case 1:
            monthlyPrice = 499;
            break;

        case 2:
            monthlyPrice = 799;
            break;

        case 3:
            monthlyPrice = 1299;
            break;

        default:
            cout << "Invalid plan.\n";
            return;
    }

    double subtotal =
        monthlyPrice * months;

    double tax = subtotal * 0.18;

    double finalAmount =
        subtotal + tax;

    cout << fixed << setprecision(2);

    cout << "\nSubscription Bill\n";
    cout << "Monthly Price: " << monthlyPrice << '\n';
    cout << "Months: " << months << '\n';
    cout << "Subtotal: " << subtotal << '\n';
    cout << "Tax: " << tax << '\n';
    cout << "Final Amount: " << finalAmount << '\n';
}


/*
============================================================
PROGRAM 16
CAR RESALE VALUE
============================================================
*/

void program16()
{
    title("PROGRAM 16 - CAR RESALE VALUE");

    double purchasePrice;
    int age;
    double annualDepreciation;

    cout << "Original purchase price: ";
    cin >> purchasePrice;

    cout << "Car age in years: ";
    cin >> age;

    cout << "Annual depreciation rate (%): ";
    cin >> annualDepreciation;

    double currentValue = purchasePrice;

    for (int i = 0; i < age; ++i)
    {
        currentValue *=
            (1 - annualDepreciation / 100.0);
    }

    double depreciation =
        purchasePrice - currentValue;

    cout << fixed << setprecision(2);

    cout << "\nVehicle Valuation\n";
    cout << "Original Price: " << purchasePrice << '\n';
    cout << "Current Estimated Value: "
         << currentValue << '\n';
    cout << "Total Depreciation: "
         << depreciation << '\n';
}


/*
============================================================
PROGRAM 17
MONTHLY BUDGET ANALYZER
============================================================
*/

void program17()
{
    title("PROGRAM 17 - MONTHLY BUDGET ANALYZER");

    double income;
    double rent;
    double food;
    double transport;
    double utilities;
    double entertainment;
    double investments;

    cout << "Monthly income: ";
    cin >> income;

    cout << "Rent: ";
    cin >> rent;

    cout << "Food: ";
    cin >> food;

    cout << "Transport: ";
    cin >> transport;

    cout << "Utilities: ";
    cin >> utilities;

    cout << "Entertainment: ";
    cin >> entertainment;

    cout << "Investments: ";
    cin >> investments;

    double totalExpenses =
        rent +
        food +
        transport +
        utilities +
        entertainment +
        investments;

    double balance =
        income - totalExpenses;

    cout << fixed << setprecision(2);

    cout << "\nBudget Analysis\n";
    cout << "Income: " << income << '\n';
    cout << "Total Expenses: " << totalExpenses << '\n';
    cout << "Remaining: " << balance << '\n';

    if (income > 0)
    {
        cout << "Expense Ratio: "
             << (totalExpenses / income) * 100
             << "%\n";
    }

    if (balance > 0)
        cout << "Status: Positive cash flow\n";
    else if (balance < 0)
        cout << "Status: Negative cash flow\n";
    else
        cout << "Status: Break-even\n";
}


/*
============================================================
PROGRAM 18
MANUFACTURING COST CALCULATOR
============================================================
*/

void program18()
{
    title("PROGRAM 18 - MANUFACTURING COST");

    int quantity;

    double rawMaterialPerUnit;
    double laborPerUnit;
    double overheadPerUnit;
    double packagingPerUnit;

    cout << "Production quantity: ";
    cin >> quantity;

    cout << "Raw material per unit: ";
    cin >> rawMaterialPerUnit;

    cout << "Labor per unit: ";
    cin >> laborPerUnit;

    cout << "Overhead per unit: ";
    cin >> overheadPerUnit;

    cout << "Packaging per unit: ";
    cin >> packagingPerUnit;

    double unitCost =
        rawMaterialPerUnit +
        laborPerUnit +
        overheadPerUnit +
        packagingPerUnit;

    double totalCost =
        unitCost * quantity;

    cout << fixed << setprecision(2);

    cout << "\nManufacturing Cost\n";
    cout << "Unit Cost: " << unitCost << '\n';
    cout << "Production Quantity: " << quantity << '\n';
    cout << "Total Production Cost: "
         << totalCost << '\n';
}


/*
============================================================
PROGRAM 19
PROJECT COST ESTIMATOR
============================================================
*/

void program19()
{
    title("PROGRAM 19 - PROJECT COST ESTIMATOR");

    int developers;
    int months;

    double salaryPerDeveloper;
    double softwareCost;
    double cloudCost;
    double miscellaneous;

    cout << "Number of developers: ";
    cin >> developers;

    cout << "Project duration (months): ";
    cin >> months;

    cout << "Monthly salary per developer: ";
    cin >> salaryPerDeveloper;

    cout << "Software cost: ";
    cin >> softwareCost;

    cout << "Cloud cost per month: ";
    cin >> cloudCost;

    cout << "Miscellaneous cost: ";
    cin >> miscellaneous;

    double developerCost =
        developers *
        salaryPerDeveloper *
        months;

    double totalCloudCost =
        cloudCost * months;

    double totalCost =
        developerCost +
        softwareCost +
        totalCloudCost +
        miscellaneous;

    cout << fixed << setprecision(2);

    cout << "\nProject Cost Estimate\n";
    cout << "Developer Cost: " << developerCost << '\n';
    cout << "Software Cost: " << softwareCost << '\n';
    cout << "Cloud Cost: " << totalCloudCost << '\n';
    cout << "Miscellaneous: " << miscellaneous << '\n';
    cout << "Total Project Cost: "
         << totalCost << '\n';
}


/*
============================================================
PROGRAM 20
PERSONAL FINANCIAL DASHBOARD
============================================================
*/

void program20()
{
    title("PROGRAM 20 - PERSONAL FINANCIAL DASHBOARD");

    string name;

    double monthlyIncome;
    double monthlyExpenses;
    double investments;
    double debtPayment;
    double emergencyFund;

    cout << "Name: ";
    getline(cin >> ws, name);

    cout << "Monthly income: ";
    cin >> monthlyIncome;

    cout << "Monthly living expenses: ";
    cin >> monthlyExpenses;

    cout << "Monthly investments: ";
    cin >> investments;

    cout << "Monthly debt payment: ";
    cin >> debtPayment;

    cout << "Current emergency fund: ";
    cin >> emergencyFund;

    double totalOutflow =
        monthlyExpenses +
        investments +
        debtPayment;

    double monthlySurplus =
        monthlyIncome - totalOutflow;

    double annualIncome =
        monthlyIncome * 12;

    double annualExpenses =
        totalOutflow * 12;

    double annualSurplus =
        monthlySurplus * 12;

    double savingsRate =
        monthlyIncome > 0
            ? (monthlySurplus / monthlyIncome) * 100
            : 0;

    double emergencyCoverage =
        monthlyExpenses > 0
            ? emergencyFund / monthlyExpenses
            : 0;

    cout << fixed << setprecision(2);

    cout << "\n========================================\n";
    cout << "PERSONAL FINANCIAL DASHBOARD\n";
    cout << "========================================\n";

    cout << "Name: " << name << '\n';

    cout << "\nMonthly Information\n";
    cout << "Income: " << monthlyIncome << '\n';
    cout << "Living Expenses: " << monthlyExpenses << '\n';
    cout << "Investments: " << investments << '\n';
    cout << "Debt Payment: " << debtPayment << '\n';
    cout << "Total Outflow: " << totalOutflow << '\n';
    cout << "Monthly Surplus: " << monthlySurplus << '\n';

    cout << "\nAnnual Projection\n";
    cout << "Annual Income: " << annualIncome << '\n';
    cout << "Annual Outflow: " << annualExpenses << '\n';
    cout << "Annual Surplus: " << annualSurplus << '\n';

    cout << "\nFinancial Metrics\n";
    cout << "Savings Rate: "
         << savingsRate << "%\n";

    cout << "Emergency Fund Coverage: "
         << emergencyCoverage
         << " months\n";

    if (monthlySurplus > 0)
        cout << "Cash Flow: Positive\n";
    else if (monthlySurplus < 0)
        cout << "Cash Flow: Negative\n";
    else
        cout << "Cash Flow: Break-even\n";
}


/*
============================================================
MAIN MENU
============================================================
*/

int main()
{
    int choice;

    cout << "\n";
    separator();

    cout << "C++ VARIABLES, DATA TYPES AND I/O\n";
    cout << "DIFFERENT PRACTICE PROGRAMS\n";

    separator();

    cout << "\n";
    cout << " 1. Digital Wallet\n";
    cout << " 2. Employee Payroll\n";
    cout << " 3. Student Performance Analyzer\n";
    cout << " 4. Mobile Data Usage\n";
    cout << " 5. Travel Cost Estimator\n";
    cout << " 6. Restaurant Bill Splitter\n";
    cout << " 7. Fuel Cost Calculator\n";
    cout << " 8. Loan Analysis\n";
    cout << " 9. Product Profit Analyzer\n";
    cout << "10. Electricity Consumption Analyzer\n";
    cout << "11. Investment Portfolio Summary\n";
    cout << "12. Hospital Bill Calculator\n";
    cout << "13. Exam Statistics\n";
    cout << "14. Bank Transaction Summary\n";
    cout << "15. Internet Subscription Calculator\n";
    cout << "16. Car Resale Value Calculator\n";
    cout << "17. Monthly Budget Analyzer\n";
    cout << "18. Manufacturing Cost Calculator\n";
    cout << "19. Project Cost Estimator\n";
    cout << "20. Personal Financial Dashboard\n";

    cout << "\nEnter program number: ";
    cin >> choice;

    switch (choice)
    {
        case 1:
            program1();
            break;

        case 2:
            program2();
            break;

        case 3:
            program3();
            break;

        case 4:
            program4();
            break;

        case 5:
            program5();
            break;

        case 6:
            program6();
            break;

        case 7:
            program7();
            break;

        case 8:
            program8();
            break;

        case 9:
            program9();
            break;

        case 10:
            program10();
            break;

        case 11:
            program11();
            break;

        case 12:
            program12();
            break;

        case 13:
            program13();
            break;

        case 14:
            program14();
            break;

        case 15:
            program15();
            break;

        case 16:
            program16();
            break;

        case 17:
            program17();
            break;

        case 18:
            program18();
            break;

        case 19:
            program19();
            break;

        case 20:
            program20();
            break;

        default:
            cout << "Invalid program number.\n";
    }

    return 0;
}
