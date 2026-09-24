/*
 * Day 3 — Conditions
 * ===================
 *
 * C++17 case study:
 * A rule-based electricity billing and customer account system.
 *
 * The program demonstrates:
 * - if
 * - else if
 * - else
 * - nested conditions
 * - compound Boolean expressions
 * - comparison operators
 * - validation
 * - classes and structures
 * - enums
 * - vectors
 * - functions
 * - algorithms
 * - exception handling
 * - decision tables represented as code
 * - edge cases
 * - guard clauses
 * - performance considerations
 *
 * Compile:
 *   g++ -std=c++17 -Wall -Wextra -pedantic conditions.cpp -o conditions
 */

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;


/* ==========================================================================
   1. BASIC CONDITION HELPERS
   ========================================================================== */

string classifyAge(int age) {
    if (age < 0) {
        throw invalid_argument("Age cannot be negative.");
    }

    if (age <= 12) {
        return "Child";
    } else if (age <= 17) {
        return "Teenager";
    } else if (age <= 59) {
        return "Adult";
    }

    return "Senior";
}


string calculateGrade(double score) {
    if (!isfinite(score) || score < 0.0 || score > 100.0) {
        throw invalid_argument("Score must be between 0 and 100.");
    }

    if (score >= 90.0) {
        return "A";
    } else if (score >= 80.0) {
        return "B";
    } else if (score >= 70.0) {
        return "C";
    } else if (score >= 60.0) {
        return "D";
    }

    return "F";
}


/* ==========================================================================
   2. LEAP YEAR
   ========================================================================== */

bool isLeapYear(int year) {
    if (year <= 0) {
        throw invalid_argument("Year must be positive.");
    }

    // A year divisible by 400 is a leap year.
    // A year divisible by 100 but not 400 is not a leap year.
    // A year divisible by 4 but not 100 is a leap year.
    return year % 400 == 0 ||
           (year % 4 == 0 && year % 100 != 0);
}


/* ==========================================================================
   3. TRIANGLE CLASSIFICATION
   ========================================================================== */

bool isValidTriangle(double a, double b, double c) {
    if (!isfinite(a) || !isfinite(b) || !isfinite(c)) {
        return false;
    }

    if (a <= 0.0 || b <= 0.0 || c <= 0.0) {
        return false;
    }

    return a + b > c &&
           a + c > b &&
           b + c > a;
}


string classifyTriangle(double a, double b, double c) {
    if (!isValidTriangle(a, b, c)) {
        return "Invalid";
    }

    if (a == b && b == c) {
        return "Equilateral";
    }

    if (a == b || b == c || a == c) {
        return "Isosceles";
    }

    return "Scalene";
}


/* ==========================================================================
   4. ENUM FOR CUSTOMER CATEGORY
   ========================================================================== */

enum class CustomerType {
    Regular,
    Member,
    Premium
};


string customerTypeName(CustomerType type) {
    switch (type) {
        case CustomerType::Regular:
            return "Regular";

        case CustomerType::Member:
            return "Member";

        case CustomerType::Premium:
            return "Premium";
    }

    throw logic_error("Unknown customer type.");
}


/* ==========================================================================
   5. CUSTOMER MODEL
   ========================================================================== */

struct Customer {
    int id;
    string name;
    int age;
    CustomerType type;
    bool seniorCitizen;
};


/* ==========================================================================
   6. ELECTRICITY BILL MODEL
   ========================================================================== */

struct ElectricityBill {
    double units;
    double energyCharge;
    double fixedCharge;
    double surcharge;
    double discount;
    double total;
    string decision;
};


/* ==========================================================================
   7. BILLING ENGINE
   ========================================================================== */

class ElectricityBillingEngine {
private:
    static constexpr double FIXED_CHARGE = 50.0;

    /*
     * Calculates the energy component using progressive slabs:
     *
     * 0–100 units       -> ₹1.50/unit
     * 101–300 units     -> ₹2.50/unit
     * 301–500 units     -> ₹4.00/unit
     * above 500 units   -> ₹6.00/unit
     *
     * The conditions are deliberately ordered from the lowest slab
     * to the highest slab so that each boundary is handled correctly.
     */
    static double calculateEnergyCharge(double units) {
        if (units < 0.0 || !isfinite(units)) {
            throw invalid_argument("Units must be a finite non-negative number.");
        }

        if (units <= 100.0) {
            return units * 1.50;
        }

        if (units <= 300.0) {
            return
                100.0 * 1.50 +
                (units - 100.0) * 2.50;
        }

        if (units <= 500.0) {
            return
                100.0 * 1.50 +
                200.0 * 2.50 +
                (units - 300.0) * 4.00;
        }

        return
            100.0 * 1.50 +
            200.0 * 2.50 +
            200.0 * 4.00 +
            (units - 500.0) * 6.00;
    }

    /*
     * A surcharge demonstrates another compound decision:
     * high consumption AND non-senior customer.
     */
    static double calculateSurcharge(
        double units,
        const Customer& customer
    ) {
        if (units > 500.0 && !customer.seniorCitizen) {
            return 100.0;
        }

        return 0.0;
    }

    /*
     * Senior citizens receive a small educational example discount.
     * The discount is applied only when consumption is not excessive.
     */
    static double calculateDiscount(
        double subtotal,
        double units,
        const Customer& customer
    ) {
        if (customer.seniorCitizen && units <= 300.0) {
            return subtotal * 0.05;
        }

        return 0.0;
    }

public:
    ElectricityBill calculate(
        double units,
        const Customer& customer
    ) const {
        // Guard clause prevents invalid input from reaching the
        // financial calculation.
        if (units < 0.0 || !isfinite(units)) {
            throw invalid_argument("Invalid electricity consumption.");
        }

        if (customer.age < 0) {
            throw invalid_argument("Customer age cannot be negative.");
        }

        const double energyCharge = calculateEnergyCharge(units);

        const double subtotal =
            FIXED_CHARGE + energyCharge;

        const double surcharge =
            calculateSurcharge(units, customer);

        const double discount =
            calculateDiscount(subtotal, units, customer);

        const double total =
            subtotal + surcharge - discount;

        string decision;

        if (customer.seniorCitizen && units <= 300.0) {
            decision = "Senior-citizen discount applied.";
        } else if (units > 500.0 && !customer.seniorCitizen) {
            decision = "High-consumption surcharge applied.";
        } else {
            decision = "Standard billing rules applied.";
        }

        return {
            units,
            energyCharge,
            FIXED_CHARGE,
            surcharge,
            discount,
            total,
            decision
        };
    }
};


/* ==========================================================================
   8. CUSTOMER ELIGIBILITY ENGINE
   ========================================================================== */

class CustomerEligibilityEngine {
public:
    static string assess(const Customer& customer) {
        if (customer.age < 18) {
            return "Restricted: customer is below adult age.";
        }

        if (customer.type == CustomerType::Premium &&
            customer.age >= 60) {
            return "Priority service category.";
        }

        if (customer.type == CustomerType::Premium) {
            return "Premium service category.";
        }

        if (customer.type == CustomerType::Member) {
            return "Member service category.";
        }

        return "Standard service category.";
    }
};


/* ==========================================================================
   9. BILLING REPORT
   ========================================================================== */

void printBill(
    const Customer& customer,
    const ElectricityBill& bill
) {
    cout << fixed << setprecision(2);

    cout << "\n----------------------------------------\n";
    cout << "Customer ID:       " << customer.id << '\n';
    cout << "Customer:          " << customer.name << '\n';
    cout << "Age:               " << customer.age << '\n';
    cout << "Customer Type:     "
         << customerTypeName(customer.type) << '\n';

    cout << "Consumption:       "
         << bill.units << " units\n";

    cout << "Energy Charge:     ₹"
         << bill.energyCharge << '\n';

    cout << "Fixed Charge:      ₹"
         << bill.fixedCharge << '\n';

    cout << "Surcharge:         ₹"
         << bill.surcharge << '\n';

    cout << "Discount:          ₹"
         << bill.discount << '\n';

    cout << "Total:             ₹"
         << bill.total << '\n';

    cout << "Billing Decision:  "
         << bill.decision << '\n';

    cout << "Eligibility:       "
         << CustomerEligibilityEngine::assess(customer)
         << '\n';

    cout << "----------------------------------------\n";
}


/* ==========================================================================
   10. INPUT VALIDATION
   ========================================================================== */

double readNonNegativeDouble(const string& prompt) {
    double value;

    while (true) {
        cout << prompt;

        if (cin >> value && isfinite(value) && value >= 0.0) {
            return value;
        }

        cout << "Invalid input. Enter a non-negative number.\n";

        cin.clear();
        cin.ignore(
            numeric_limits<streamsize>::max(),
            '\n'
        );
    }
}


int readPositiveInteger(const string& prompt) {
    int value;

    while (true) {
        cout << prompt;

        if (cin >> value && value > 0) {
            return value;
        }

        cout << "Invalid input. Enter a positive integer.\n";

        cin.clear();
        cin.ignore(
            numeric_limits<streamsize>::max(),
            '\n'
        );
    }
}


/* ==========================================================================
   11. DECISION EXAMPLES
   ========================================================================== */

void runBasicExamples() {
    cout << "\n=== BASIC CONDITIONS ===\n";

    int age = 25;
    double score = 87.5;

    if (age >= 18) {
        cout << "Adult condition is true.\n";
    } else {
        cout << "Adult condition is false.\n";
    }

    cout << "Grade: "
         << calculateGrade(score)
         << '\n';

    cout << "2024 leap year: "
         << (isLeapYear(2024) ? "yes" : "no")
         << '\n';

    cout << "Triangle 3,4,5: "
         << classifyTriangle(3, 4, 5)
         << '\n';
}


/* ==========================================================================
   12. EDGE CASE TESTS
   ========================================================================== */

void runEdgeCaseTests() {
    cout << "\n=== EDGE CASE TESTS ===\n";

    const vector<double> boundaryScores = {
        0.0,
        59.99,
        60.0,
        69.99,
        70.0,
        79.99,
        80.0,
        89.99,
        90.0,
        100.0
    };

    for (double score : boundaryScores) {
        cout << score
             << " -> "
             << calculateGrade(score)
             << '\n';
    }

    cout << "\nLeap-year boundaries:\n";

    for (int year : {1600, 1700, 1900, 2000, 2024, 2025, 2100}) {
        cout << year
             << " -> "
             << (isLeapYear(year) ? "leap" : "not leap")
             << '\n';
    }

    cout << "\nTriangle boundaries:\n";

    cout << "(3,3,3) -> "
         << classifyTriangle(3, 3, 3) << '\n';

    cout << "(3,3,4) -> "
         << classifyTriangle(3, 3, 4) << '\n';

    cout << "(3,4,5) -> "
         << classifyTriangle(3, 4, 5) << '\n';

    cout << "(1,2,3) -> "
         << classifyTriangle(1, 2, 3) << '\n';
}


/* ==========================================================================
   13. BILLING CASE STUDY
   ========================================================================== */

void runBillingCaseStudy() {
    cout << "\n=== ELECTRICITY BILLING CASE STUDY ===\n";

    ElectricityBillingEngine engine;

    vector<Customer> customers = {
        {
            101,
            "Aarav",
            35,
            CustomerType::Regular,
            false
        },
        {
            102,
            "Meera",
            64,
            CustomerType::Member,
            true
        },
        {
            103,
            "Kabir",
            45,
            CustomerType::Premium,
            false
        },
        {
            104,
            "Nisha",
            72,
            CustomerType::Premium,
            true
        }
    };

    vector<double> consumption = {
        80.0,
        250.0,
        520.0,
        300.0
    };

    for (size_t i = 0; i < customers.size(); ++i) {
        ElectricityBill bill =
            engine.calculate(
                consumption[i],
                customers[i]
            );

        printBill(customers[i], bill);
    }
}


/* ==========================================================================
   14. BILLING TESTS
   ========================================================================== */

void runBillingAssertions() {
    cout << "\n=== BILLING ASSERTIONS ===\n";

    ElectricityBillingEngine engine;

    Customer regular {
        1,
        "Test Regular",
        35,
        CustomerType::Regular,
        false
    };

    Customer senior {
        2,
        "Test Senior",
        70,
        CustomerType::Member,
        true
    };

    const ElectricityBill zeroUnits =
        engine.calculate(0.0, regular);

    // Fixed charge remains even when consumption is zero.
    if (zeroUnits.total != 50.0) {
        throw logic_error("Zero-unit billing test failed.");
    }

    const ElectricityBill seniorBill =
        engine.calculate(100.0, senior);

    if (!(seniorBill.discount > 0.0)) {
        throw logic_error("Senior discount test failed.");
    }

    const ElectricityBill highUsage =
        engine.calculate(600.0, regular);

    if (!(highUsage.surcharge > 0.0)) {
        throw logic_error("High-usage surcharge test failed.");
    }

    cout << "All billing assertions passed.\n";
}


/* ==========================================================================
   15. EXCEPTION DEMONSTRATION
   ========================================================================== */

void demonstrateErrorHandling() {
    cout << "\n=== ERROR HANDLING ===\n";

    try {
        cout << calculateGrade(120.0) << '\n';
    } catch (const exception& error) {
        cout << "Caught expected error: "
             << error.what()
             << '\n';
    }

    try {
        cout << classifyTriangle(-1, 2, 2) << '\n';
    } catch (const exception& error) {
        cout << "Caught error: "
             << error.what()
             << '\n';
    }

    try {
        ElectricityBillingEngine engine;

        Customer customer {
            999,
            "Invalid",
            30,
            CustomerType::Regular,
            false
        };

        engine.calculate(-100.0, customer);
    } catch (const exception& error) {
        cout << "Caught billing error: "
             << error.what()
             << '\n';
    }
}


/* ==========================================================================
   16. COMPLEXITY DISCUSSION IN CODE
   ========================================================================== */

/*
 * Most decisions in this case study are O(1):
 *
 * - grade classification: O(1)
 * - leap-year check: O(1)
 * - triangle classification: O(1)
 * - electricity slab calculation: O(1)
 * - customer eligibility: O(1)
 *
 * Processing N customers is O(N) because each customer is evaluated once.
 *
 * The billing engine uses constant auxiliary memory for each calculation.
 */


/* ==========================================================================
   17. OPTIONAL INTERACTIVE MODE
   ========================================================================== */

void interactiveMode() {
    cout << "\n=== INTERACTIVE BILLING MODE ===\n";

    cout << "Enter customer information.\n";

    int id = readPositiveInteger("Customer ID: ");

    cin.ignore(
        numeric_limits<streamsize>::max(),
        '\n'
    );

    string name;

    cout << "Customer name: ";
    getline(cin, name);

    int age = readPositiveInteger("Age: ");
    double units = readNonNegativeDouble("Electricity units: ");

    cout << "\nCustomer type:\n";
    cout << "1. Regular\n";
    cout << "2. Member\n";
    cout << "3. Premium\n";

    int typeChoice =
        readPositiveInteger("Select type: ");

    CustomerType type;

    if (typeChoice == 1) {
        type = CustomerType::Regular;
    } else if (typeChoice == 2) {
        type = CustomerType::Member;
    } else if (typeChoice == 3) {
        type = CustomerType::Premium;
    } else {
        cout << "Unknown choice. Regular type selected.\n";
        type = CustomerType::Regular;
    }

    const bool seniorCitizen = age >= 60;

    Customer customer {
        id,
        name,
        age,
        type,
        seniorCitizen
    };

    ElectricityBillingEngine engine;

    try {
        const ElectricityBill bill =
            engine.calculate(units, customer);

        printBill(customer, bill);
    } catch (const exception& error) {
        cout << "Could not calculate bill: "
             << error.what()
             << '\n';
    }
}


/* ==========================================================================
   18. MAIN
   ========================================================================== */

int main() {
    cout << string(72, '=') << '\n';
    cout << "DAY 3 — CONDITIONS\n";
    cout << "C++ Rule-Based Electricity Billing Case Study\n";
    cout << string(72, '=') << '\n';

    try {
        runBasicExamples();
        runEdgeCaseTests();
        runBillingCaseStudy();
        runBillingAssertions();
        demonstrateErrorHandling();

        /*
         * The interactive mode is intentionally not called automatically
         * so the program can run as a deterministic study and test program.
         *
         * To use it manually, uncomment:
         *
         * interactiveMode();
         */
    } catch (const exception& error) {
        cerr << "Fatal error: "
             << error.what()
             << '\n';

        return 1;
    }

    cout << "\n" << string(72, '=') << '\n';
    cout << "CONDITION CASE STUDY COMPLETE\n";
    cout << string(72, '=') << '\n';

    return 0;
}
