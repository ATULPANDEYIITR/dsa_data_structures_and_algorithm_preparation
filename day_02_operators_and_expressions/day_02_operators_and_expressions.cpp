/*
 * Operators and Expressions
 * =========================
 *
 * C++17 case study:
 * A configurable transaction and billing engine for a small digital
 * marketplace.
 *
 * The program demonstrates how operators and expressions are used in a
 * realistic system involving:
 * - arithmetic calculations
 * - comparisons
 * - logical conditions
 * - assignment and compound assignment
 * - prefix and postfix increment/decrement
 * - modulo-based validation
 * - operator precedence
 * - conditional expressions
 * - bitwise flags
 * - overloaded operators
 * - validation
 * - error handling
 * - data structures
 * - algorithms
 * - complexity considerations
 *
 * Compile:
 *   g++ -std=c++17 -O2 operators_and_expressions.cpp -o operators
 *
 * Run:
 *   ./operators
 */

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

// ---------------------------------------------------------------------------
// Utility output functions
// ---------------------------------------------------------------------------

void section(const string& title) {
    cout << "\n" << string(78, '=') << "\n";
    cout << title << "\n";
    cout << string(78, '=') << "\n";
}

void subsection(const string& title) {
    cout << "\n" << string(78, '-') << "\n";
    cout << title << "\n";
    cout << string(78, '-') << "\n";
}

// ---------------------------------------------------------------------------
// Permission flags
// ---------------------------------------------------------------------------

enum class Permission : unsigned int {
    None = 0,
    View = 1u << 0,
    Purchase = 1u << 1,
    Refund = 1u << 2,
    Admin = 1u << 3
};

Permission operator|(Permission left, Permission right) {
    return static_cast<Permission>(
        static_cast<unsigned int>(left) |
        static_cast<unsigned int>(right)
    );
}

Permission operator&(Permission left, Permission right) {
    return static_cast<Permission>(
        static_cast<unsigned int>(left) &
        static_cast<unsigned int>(right)
    );
}

bool hasPermission(Permission permissions, Permission requested) {
    return (permissions & requested) != Permission::None;
}

// ---------------------------------------------------------------------------
// Money class
// ---------------------------------------------------------------------------

class Money {
private:
    long long cents_;

public:
    explicit Money(long long cents = 0) : cents_(cents) {}

    long long cents() const {
        return cents_;
    }

    double asDecimal() const {
        return static_cast<double>(cents_) / 100.0;
    }

    Money operator+(const Money& other) const {
        return Money(cents_ + other.cents_);
    }

    Money operator-(const Money& other) const {
        return Money(cents_ - other.cents_);
    }

    Money& operator+=(const Money& other) {
        cents_ += other.cents_;
        return *this;
    }

    Money& operator-=(const Money& other) {
        cents_ -= other.cents_;
        return *this;
    }

    bool operator<(const Money& other) const {
        return cents_ < other.cents_;
    }

    bool operator>(const Money& other) const {
        return cents_ > other.cents_;
    }

    bool operator==(const Money& other) const {
        return cents_ == other.cents_;
    }
};

ostream& operator<<(ostream& output, const Money& money) {
    output << fixed << setprecision(2) << money.asDecimal();
    return output;
}

// ---------------------------------------------------------------------------
// Product
// ---------------------------------------------------------------------------

struct Product {
    int id;
    string name;
    Money price;
    int stock;
    int categoryCode;
};

// ---------------------------------------------------------------------------
// Order
// ---------------------------------------------------------------------------

struct Order {
    int orderId;
    int productId;
    int quantity;
    Money subtotal;
    Money discount;
    Money tax;
    Money total;
};

// ---------------------------------------------------------------------------
// Marketplace engine
// ---------------------------------------------------------------------------

class Marketplace {
private:
    unordered_map<int, Product> products_;
    vector<Order> orders_;
    int nextOrderId_ = 1001;

    static Money percentageOf(Money amount, int percentage) {
        // All money is stored as integer cents. This avoids many of the
        // representation problems associated with binary floating point
        // for currency-like values.
        const long long cents =
            amount.cents() * percentage / 100;

        return Money(cents);
    }

public:
    void addProduct(const Product& product) {
        if (product.id <= 0) {
            throw invalid_argument("Product ID must be positive.");
        }

        if (product.name.empty()) {
            throw invalid_argument("Product name cannot be empty.");
        }

        if (product.price.cents() < 0) {
            throw invalid_argument("Product price cannot be negative.");
        }

        if (product.stock < 0) {
            throw invalid_argument("Stock cannot be negative.");
        }

        if (products_.contains(product.id)) {
            throw invalid_argument("Product ID already exists.");
        }

        products_.emplace(product.id, product);
    }

    const Product& getProduct(int productId) const {
        auto iterator = products_.find(productId);

        if (iterator == products_.end()) {
            throw out_of_range("Product was not found.");
        }

        return iterator->second;
    }

    optional<Order> createOrder(
        int productId,
        int quantity,
        int discountPercentage,
        int taxPercentage
    ) {
        if (quantity <= 0) {
            throw invalid_argument("Quantity must be positive.");
        }

        if (discountPercentage < 0 || discountPercentage > 100) {
            throw invalid_argument(
                "Discount percentage must be between 0 and 100."
            );
        }

        if (taxPercentage < 0 || taxPercentage > 100) {
            throw invalid_argument(
                "Tax percentage must be between 0 and 100."
            );
        }

        Product& product = products_.at(productId);

        if (quantity > product.stock) {
            return nullopt;
        }

        // Arithmetic expression:
        // subtotal = price * quantity.
        //
        // Because Money stores cents, multiplication remains integer-based.
        Money subtotal(
            product.price.cents() *
            static_cast<long long>(quantity)
        );

        Money discount =
            percentageOf(subtotal, discountPercentage);

        Money discountedSubtotal =
            subtotal - discount;

        Money tax =
            percentageOf(discountedSubtotal, taxPercentage);

        Money total =
            discountedSubtotal + tax;

        // Compound assignment updates stock after validation succeeds.
        product.stock -= quantity;

        Order order{
            nextOrderId_++,
            productId,
            quantity,
            subtotal,
            discount,
            tax,
            total
        };

        orders_.push_back(order);

        return order;
    }

    const vector<Order>& orders() const {
        return orders_;
    }

    Money totalRevenue() const {
        Money total;

        for (const Order& order : orders_) {
            total += order.total;
        }

        return total;
    }

    int totalUnitsSold() const {
        int total = 0;

        for (const Order& order : orders_) {
            total += order.quantity;
        }

        return total;
    }

    vector<Product> productsBelowStock(int threshold) const {
        vector<Product> result;

        for (const auto& [id, product] : products_) {
            if (product.stock < threshold) {
                result.push_back(product);
            }
        }

        return result;
    }
};

// ---------------------------------------------------------------------------
// Basic operator demonstrations
// ---------------------------------------------------------------------------

void demonstrateArithmetic() {
    section("1. Arithmetic operators");

    int a = 17;
    int b = 5;

    cout << "a + b = " << a + b << "\n";
    cout << "a - b = " << a - b << "\n";
    cout << "a * b = " << a * b << "\n";
    cout << "a / b = " << a / b
         << "  (integer division)\n";
    cout << "a % b = " << a % b << "\n";

    double preciseDivision =
        static_cast<double>(a) / b;

    cout << "static_cast<double>(a) / b = "
         << preciseDivision << "\n";

    cout << "a squared = " << a * a << "\n";
}

void demonstrateComparisons() {
    section("2. Comparison operators");

    const int age = 25;

    cout << boolalpha;
    cout << "age == 25: " << (age == 25) << "\n";
    cout << "age != 30: " << (age != 30) << "\n";
    cout << "age >= 18: " << (age >= 18) << "\n";
    cout << "age < 18: " << (age < 18) << "\n";

    // C++ does not support Python-style chained comparisons such as
    // 0 <= age <= 100. The correct C++ expression is explicit.
    bool validAge = age >= 0 && age <= 100;

    cout << "age >= 0 && age <= 100: "
         << validAge << "\n";
}

void demonstrateLogicalOperators() {
    section("3. Logical operators");

    bool adult = true;
    bool verified = true;
    bool suspended = false;

    bool canPurchase =
        adult &&
        verified &&
        !suspended;

    cout << "Can purchase: " << canPurchase << "\n";

    bool needsReview =
        !verified || suspended;

    cout << "Needs review: " << needsReview << "\n";

    cout << "\nShort-circuit example:\n";

    int denominator = 0;

    // The right side is not evaluated because the first condition is false.
    bool safeDivision =
        denominator != 0 &&
        (100 / denominator > 2);

    cout << "Safe division expression: "
         << safeDivision << "\n";
}

void demonstrateAssignment() {
    section("4. Assignment and compound assignment");

    int value = 10;

    cout << "Initial value: " << value << "\n";

    value += 5;
    cout << "After += 5: " << value << "\n";

    value -= 3;
    cout << "After -= 3: " << value << "\n";

    value *= 2;
    cout << "After *= 2: " << value << "\n";

    value /= 4;
    cout << "After /= 4: " << value << "\n";

    value %= 3;
    cout << "After %= 3: " << value << "\n";
}

void demonstrateIncrementDecrement() {
    section("5. Increment and decrement");

    int counter = 5;

    cout << "counter++ returns: "
         << counter++ << "\n";

    cout << "counter after postfix increment: "
         << counter << "\n";

    cout << "++counter returns: "
         << ++counter << "\n";

    cout << "counter-- returns: "
         << counter-- << "\n";

    cout << "--counter returns: "
         << --counter << "\n";

    cout << "\nPostfix uses the old value in the expression; "
         << "prefix changes the value before it is used.\n";
}

void demonstrateModulo() {
    section("6. Modulo and practical remainder operations");

    for (int number = 0; number <= 10; ++number) {
        cout << number << " -> "
             << ((number % 2 == 0) ? "even" : "odd")
             << "\n";
    }

    int number = 58327;

    cout << "\nLast digit of " << number
         << " = " << number % 10 << "\n";

    int sum = 0;
    int working = number;

    while (working > 0) {
        sum += working % 10;
        working /= 10;
    }

    cout << "Digit sum = " << sum << "\n";
}

void demonstratePrecedence() {
    section("7. Operator precedence");

    cout << "2 + 3 * 4 = "
         << 2 + 3 * 4 << "\n";

    cout << "(2 + 3) * 4 = "
         << (2 + 3) * 4 << "\n";

    cout << "20 - 4 * 3 = "
         << 20 - 4 * 3 << "\n";

    cout << "(20 - 4) * 3 = "
         << (20 - 4) * 3 << "\n";

    cout << "\nParentheses should be used when they make the "
         << "intended meaning clearer.\n";
}

void demonstrateConditionalOperator() {
    section("8. Conditional operator");

    int number = 17;

    string classification =
        (number % 2 == 0)
            ? "even"
            : "odd";

    cout << number << " is " << classification << "\n";

    int larger =
        (10 > 25)
            ? 10
            : 25;

    cout << "Larger number: "
         << larger << "\n";
}

void demonstrateBitwiseOperators() {
    section("9. Bitwise operators");

    unsigned int a = 0b1100;
    unsigned int b = 0b1010;

    cout << "a & b = " << (a & b) << "\n";
    cout << "a | b = " << (a | b) << "\n";
    cout << "a ^ b = " << (a ^ b) << "\n";
    cout << "a << 1 = " << (a << 1) << "\n";
    cout << "a >> 1 = " << (a >> 1) << "\n";

    Permission permissions =
        Permission::View |
        Permission::Purchase;

    cout << "Has View: "
         << hasPermission(permissions, Permission::View)
         << "\n";

    cout << "Has Refund: "
         << hasPermission(permissions, Permission::Refund)
         << "\n";

    permissions =
        permissions |
        Permission::Refund;

    cout << "Has Refund after update: "
         << hasPermission(permissions, Permission::Refund)
         << "\n";
}

// ---------------------------------------------------------------------------
// Digit calculation functions
// ---------------------------------------------------------------------------

bool isEven(int number) {
    return number % 2 == 0;
}

bool isDivisible(int number, int divisor) {
    if (divisor == 0) {
        throw invalid_argument(
            "A divisor cannot be zero."
        );
    }

    return number % divisor == 0;
}

int digitSum(int number) {
    long long value = llabs(static_cast<long long>(number));
    int total = 0;

    if (value == 0) {
        return 0;
    }

    while (value > 0) {
        total += static_cast<int>(value % 10);
        value /= 10;
    }

    return total;
}

int reverseInteger(int number) {
    long long value =
        llabs(static_cast<long long>(number));

    long long reversed = 0;

    while (value > 0) {
        int digit =
            static_cast<int>(value % 10);

        reversed =
            reversed * 10 + digit;

        value /= 10;
    }

    if (number < 0) {
        reversed = -reversed;
    }

    if (
        reversed < numeric_limits<int>::min() ||
        reversed > numeric_limits<int>::max()
    ) {
        throw overflow_error(
            "Reversed integer does not fit in int."
        );
    }

    return static_cast<int>(reversed);
}

// ---------------------------------------------------------------------------
// Marketplace case study
// ---------------------------------------------------------------------------

void demonstrateMarketplace() {
    section("10. Industry-style case study: marketplace billing engine");

    Marketplace marketplace;

    marketplace.addProduct({
        101,
        "Cloud Storage",
        Money(1200),
        50,
        1
    });

    marketplace.addProduct({
        102,
        "Security Scanner",
        Money(3500),
        25,
        2
    });

    marketplace.addProduct({
        103,
        "Analytics Package",
        Money(4999),
        12,
        3
    });

    cout << "\nProducts loaded into the marketplace.\n";

    auto order1 =
        marketplace.createOrder(
            101,
            3,
            10,
            18
        );

    auto order2 =
        marketplace.createOrder(
            102,
            2,
            5,
            18
        );

    auto order3 =
        marketplace.createOrder(
            103,
            1,
            0,
            18
        );

    vector<optional<Order>> createdOrders{
        order1,
        order2,
        order3
    };

    for (const auto& order : createdOrders) {
        if (!order.has_value()) {
            cout << "Order could not be created because "
                 << "stock was insufficient.\n";
            continue;
        }

        const Order& current = order.value();

        cout << "\nOrder #" << current.orderId << "\n";
        cout << "Product ID: " << current.productId << "\n";
        cout << "Quantity: " << current.quantity << "\n";
        cout << "Subtotal: " << current.subtotal << "\n";
        cout << "Discount: " << current.discount << "\n";
        cout << "Tax: " << current.tax << "\n";
        cout << "Total: " << current.total << "\n";
    }

    cout << "\nMarketplace revenue: "
         << marketplace.totalRevenue()
         << "\n";

    cout << "Units sold: "
         << marketplace.totalUnitsSold()
         << "\n";

    subsection("Low-stock report");

    const auto lowStock =
        marketplace.productsBelowStock(20);

    for (const Product& product : lowStock) {
        cout << product.name
             << " -> stock=" << product.stock
             << "\n";
    }

    subsection("Insufficient-stock condition");

    auto failedOrder =
        marketplace.createOrder(
            103,
            100,
            0,
            18
        );

    cout << "Large order accepted: "
         << failedOrder.has_value()
         << "\n";
}

// ---------------------------------------------------------------------------
// Validation and failure conditions
// ---------------------------------------------------------------------------

void demonstrateValidation() {
    section("11. Validation and failure conditions");

    Marketplace marketplace;

    try {
        marketplace.addProduct({
            1,
            "",
            Money(100),
            10,
            1
        });
    } catch (const exception& error) {
        cout << "Invalid product rejected: "
             << error.what() << "\n";
    }

    try {
        isDivisible(10, 0);
    } catch (const exception& error) {
        cout << "Invalid divisibility operation rejected: "
             << error.what() << "\n";
    }

    try {
        reverseInteger(numeric_limits<int>::min());
        cout << "Minimum integer reversal completed.\n";
    } catch (const exception& error) {
        cout << "Integer edge case: "
             << error.what() << "\n";
    }
}

// ---------------------------------------------------------------------------
// Algorithmic complexity demonstration
// ---------------------------------------------------------------------------

void demonstrateComplexity() {
    section("12. Algorithmic complexity");

    vector<int> values;

    for (int value = 1; value <= 100000; ++value) {
        values.push_back(value);
    }

    int evenCount = 0;

    // One modulo operation is O(1). Applying it to n values produces
    // an O(n) loop.
    for (int value : values) {
        if (value % 2 == 0) {
            ++evenCount;
        }
    }

    cout << "Even numbers from 1 to 100000: "
         << evenCount << "\n";

    cout << "\nTime complexity: O(n)\n";
    cout << "Additional counting space: O(1), "
         << "excluding the input vector.\n";
}

// ---------------------------------------------------------------------------
// Verification
// ---------------------------------------------------------------------------

void runAssertions() {
    section("13. Verification");

    if (2 + 3 != 5) {
        throw runtime_error("Addition test failed.");
    }

    if (10 - 4 != 6) {
        throw runtime_error("Subtraction test failed.");
    }

    if (6 * 7 != 42) {
        throw runtime_error("Multiplication test failed.");
    }

    if (20 / 4 != 5) {
        throw runtime_error("Division test failed.");
    }

    if (20 % 6 != 2) {
        throw runtime_error("Modulo test failed.");
    }

    if (!isEven(10)) {
        throw runtime_error("Even-number test failed.");
    }

    if (isEven(11)) {
        throw runtime_error("Odd-number test failed.");
    }

    if (digitSum(12345) != 15) {
        throw runtime_error("Digit-sum test failed.");
    }

    if (reverseInteger(12345) != 54321) {
        throw runtime_error("Reverse-number test failed.");
    }

    if (largest(1, 2, 3) != 3) {
        throw runtime_error("Largest-value test failed.");
    }

    cout << "All verification tests passed.\n";
}

// ---------------------------------------------------------------------------
// Helper needed by verification
// ---------------------------------------------------------------------------

int largest(int a, int b, int c) {
    return max(a, max(b, c));
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

int main() {
    try {
        cout << "OPERATORS AND EXPRESSIONS\n";
        cout << "C++17 technical case study and practice program\n";

        demonstrateArithmetic();
        demonstrateComparisons();
        demonstrateLogicalOperators();
        demonstrateAssignment();
        demonstrateIncrementDecrement();
        demonstrateModulo();
        demonstratePrecedence();
        demonstrateConditionalOperator();
        demonstrateBitwiseOperators();

        cout << "\nDigit calculation examples:\n";
        cout << "digitSum(58327) = "
             << digitSum(58327) << "\n";
        cout << "reverseInteger(58327) = "
             << reverseInteger(58327) << "\n";

        demonstrateMarketplace();
        demonstrateValidation();
        demonstrateComplexity();
        runAssertions();

        section("End of operators and expressions case study");

        return 0;
    }
    catch (const exception& error) {
        cerr << "Fatal error: "
             << error.what()
             << "\n";

        return 1;
    }
}
