/*
 * Day 4 — Loops
 *
 * C++17 case study:
 * Transaction Monitoring and Risk Analysis Engine
 *
 * The program demonstrates:
 * - for loops
 * - range-based for loops
 * - while loops
 * - do-while loops
 * - nested loops
 * - loop counters
 * - break and continue
 * - loop termination
 * - accumulators
 * - searching
 * - digit algorithms
 * - factorial
 * - prime detection
 * - Fibonacci generation
 * - pattern generation
 * - vectors, maps, classes, structs
 * - validation and error handling
 * - complexity considerations
 *
 * Compile:
 * g++ -std=c++17 -O2 -Wall -Wextra -pedantic day4_loops.cpp -o day4_loops
 */

#include <algorithm>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace std;


// ============================================================================
// BASIC LOOP DEMONSTRATIONS
// ============================================================================

void demonstrateForLoop() {
    cout << "\n=== FOR LOOP ===\n";

    for (int number = 1; number <= 5; ++number) {
        cout << number << ' ';
    }

    cout << "\nEven numbers:\n";

    for (int number = 2; number <= 10; number += 2) {
        cout << number << ' ';
    }

    cout << '\n';
}


void demonstrateWhileLoop() {
    cout << "\n=== WHILE LOOP ===\n";

    int counter = 1;

    while (counter <= 5) {
        cout << counter << ' ';
        ++counter;
    }

    cout << '\n';
}


void demonstrateDoWhileLoop() {
    cout << "\n=== DO-WHILE LOOP ===\n";

    /*
     * The body executes before the condition is checked.
     * This guarantees at least one execution.
     */
    int attempts = 0;

    do {
        ++attempts;
        cout << "Attempt " << attempts << '\n';
    } while (attempts < 3);
}


void demonstrateBreakAndContinue() {
    cout << "\n=== BREAK AND CONTINUE ===\n";

    cout << "break example: ";

    for (int number = 1; number <= 10; ++number) {
        if (number == 6) {
            break;
        }

        cout << number << ' ';
    }

    cout << "\ncontinue example: ";

    for (int number = 1; number <= 10; ++number) {
        if (number % 2 == 0) {
            continue;
        }

        cout << number << ' ';
    }

    cout << '\n';
}


// ============================================================================
// NUMBER ALGORITHMS
// ============================================================================

long long sumNumbers(int limit) {
    if (limit < 0) {
        throw invalid_argument("limit cannot be negative");
    }

    long long total = 0;

    for (int number = 1; number <= limit; ++number) {
        total += number;
    }

    return total;
}


unsigned long long factorial(unsigned int number) {
    unsigned long long result = 1;

    for (unsigned int value = 2; value <= number; ++value) {
        /*
         * unsigned long long overflows for sufficiently large factorials.
         * This function intentionally uses a fixed-width integer because
         * the case study focuses on loop mechanics rather than arbitrary
         * precision arithmetic.
         */
        result *= value;
    }

    return result;
}


int countDigits(long long number) {
    if (number == 0) {
        return 1;
    }

    if (number == numeric_limits<long long>::min()) {
        /*
         * std::abs cannot safely represent LLONG_MIN as a long long.
         * Handle this exceptional boundary case explicitly.
         */
        return 19;
    }

    number = llabs(number);

    int count = 0;

    while (number > 0) {
        number /= 10;
        ++count;
    }

    return count;
}


long long reverseNumber(long long number) {
    const bool negative = number < 0;

    /*
     * Convert to an unsigned magnitude to avoid undefined behavior
     * when processing LLONG_MIN.
     */
    unsigned long long magnitude;

    if (number == numeric_limits<long long>::min()) {
        magnitude =
            static_cast<unsigned long long>(
                numeric_limits<long long>::max()
            ) + 1ULL;
    } else {
        magnitude = static_cast<unsigned long long>(
            negative ? -number : number
        );
    }

    unsigned long long reversed = 0;

    while (magnitude > 0) {
        const unsigned int digit =
            static_cast<unsigned int>(magnitude % 10ULL);

        /*
         * Detect overflow before multiplying by 10.
         */
        if (
            reversed >
            (numeric_limits<unsigned long long>::max() - digit) / 10ULL
        ) {
            throw overflow_error("reversed number exceeds unsigned range");
        }

        reversed = reversed * 10ULL + digit;
        magnitude /= 10ULL;
    }

    if (!negative) {
        if (
            reversed >
            static_cast<unsigned long long>(
                numeric_limits<long long>::max()
            )
        ) {
            throw overflow_error("reversed number exceeds signed range");
        }

        return static_cast<long long>(reversed);
    }

    const unsigned long long negativeLimit =
        static_cast<unsigned long long>(
            numeric_limits<long long>::max()
        ) + 1ULL;

    if (reversed > negativeLimit) {
        throw overflow_error("reversed negative number overflows");
    }

    if (reversed == negativeLimit) {
        return numeric_limits<long long>::min();
    }

    return -static_cast<long long>(reversed);
}


bool isPalindrome(long long number) {
    if (number < 0) {
        return false;
    }

    return number == reverseNumber(number);
}


bool isPrime(long long number) {
    if (number < 2) {
        return false;
    }

    if (number == 2) {
        return true;
    }

    if (number % 2 == 0) {
        return false;
    }

    /*
     * Only divisors through sqrt(number) are required.
     * divisor * divisor <= number avoids computing sqrt repeatedly.
     */
    for (long long divisor = 3; divisor <= number / divisor; divisor += 2) {
        if (number % divisor == 0) {
            return false;
        }
    }

    return true;
}


vector<int> generatePrimes(int limit) {
    vector<int> primes;

    for (int number = 2; number <= limit; ++number) {
        if (isPrime(number)) {
            primes.push_back(number);
        }
    }

    return primes;
}


vector<unsigned long long> fibonacci(size_t count) {
    vector<unsigned long long> values;
    values.reserve(count);

    unsigned long long first = 0;
    unsigned long long second = 1;

    for (size_t index = 0; index < count; ++index) {
        values.push_back(first);

        /*
         * Overflow is detected before addition.
         */
        if (
            second >
            numeric_limits<unsigned long long>::max() - first
        ) {
            break;
        }

        const unsigned long long next = first + second;
        first = second;
        second = next;
    }

    return values;
}


// ============================================================================
// NESTED LOOP PATTERNS
// ============================================================================

void printSquare(int size) {
    if (size < 0) {
        throw invalid_argument("size cannot be negative");
    }

    for (int row = 0; row < size; ++row) {
        for (int column = 0; column < size; ++column) {
            cout << "* ";
        }

        cout << '\n';
    }
}


void printTriangle(int height) {
    if (height < 0) {
        throw invalid_argument("height cannot be negative");
    }

    for (int row = 1; row <= height; ++row) {
        for (int column = 0; column < row; ++column) {
            cout << "* ";
        }

        cout << '\n';
    }
}


vector<vector<int>> multiplicationGrid(int size) {
    vector<vector<int>> grid;

    for (int row = 1; row <= size; ++row) {
        vector<int> currentRow;

        for (int column = 1; column <= size; ++column) {
            currentRow.push_back(row * column);
        }

        grid.push_back(currentRow);
    }

    return grid;
}


void printMultiplicationGrid(const vector<vector<int>>& grid) {
    for (const auto& row : grid) {
        for (const int value : row) {
            cout << setw(4) << value;
        }

        cout << '\n';
    }
}


// ============================================================================
// TRANSACTION DOMAIN MODEL
// ============================================================================

enum class TransactionStatus {
    SUCCESS,
    FAILED,
    PENDING
};


string statusToString(TransactionStatus status) {
    switch (status) {
        case TransactionStatus::SUCCESS:
            return "SUCCESS";
        case TransactionStatus::FAILED:
            return "FAILED";
        case TransactionStatus::PENDING:
            return "PENDING";
    }

    return "UNKNOWN";
}


struct Transaction {
    string id;
    double amount;
    TransactionStatus status;
    string category;
};


// ============================================================================
// TRANSACTION MONITOR
// ============================================================================

class TransactionMonitor {
private:
    vector<Transaction> transactions;

public:
    explicit TransactionMonitor(vector<Transaction> data)
        : transactions(move(data)) {}

    /*
     * Sum only successful transactions.
     *
     * Complexity:
     * Time: O(n)
     * Extra working space: O(1)
     */
    double successfulTotal() const {
        double total = 0.0;

        for (const Transaction& transaction : transactions) {
            if (transaction.status != TransactionStatus::SUCCESS) {
                continue;
            }

            total += transaction.amount;
        }

        return total;
    }


    /*
     * Find the largest successful transaction.
     *
     * This demonstrates a loop invariant:
     * after each iteration, largest points to the largest successful
     * transaction seen so far.
     */
    optional<Transaction> largestSuccessful() const {
        optional<Transaction> largest;

        for (const Transaction& transaction : transactions) {
            if (transaction.status != TransactionStatus::SUCCESS) {
                continue;
            }

            if (!largest.has_value() ||
                transaction.amount > largest->amount) {
                largest = transaction;
            }
        }

        return largest;
    }


    vector<string> failedTransactionIds() const {
        vector<string> ids;

        for (const Transaction& transaction : transactions) {
            if (transaction.status == TransactionStatus::FAILED) {
                ids.push_back(transaction.id);
            }
        }

        return ids;
    }


    map<string, double> successfulTotalsByCategory() const {
        map<string, double> totals;

        for (const Transaction& transaction : transactions) {
            if (transaction.status != TransactionStatus::SUCCESS) {
                continue;
            }

            totals[transaction.category] += transaction.amount;
        }

        return totals;
    }


    map<TransactionStatus, int> statusCounts() const {
        map<TransactionStatus, int> counts;

        for (const Transaction& transaction : transactions) {
            ++counts[transaction.status];
        }

        return counts;
    }


    optional<Transaction> findTransaction(const string& id) const {
        for (const Transaction& transaction : transactions) {
            if (transaction.id == id) {
                return transaction;
            }
        }

        return nullopt;
    }


    vector<string> highValueSuccessfulTransactions(
        double threshold
    ) const {
        vector<string> result;

        for (const Transaction& transaction : transactions) {
            if (transaction.status != TransactionStatus::SUCCESS) {
                continue;
            }

            if (transaction.amount > threshold) {
                result.push_back(transaction.id);
            }
        }

        return result;
    }


    void printReport() const {
        cout << "\n=== TRANSACTION REPORT ===\n";

        cout << fixed << setprecision(2);
        cout << "Successful total: " << successfulTotal() << '\n';

        const auto largest = largestSuccessful();

        if (largest.has_value()) {
            cout << "Largest successful transaction: "
                 << largest->id
                 << " / "
                 << largest->amount
                 << '\n';
        } else {
            cout << "Largest successful transaction: none\n";
        }

        cout << "Failed transaction IDs: ";

        const auto failed = failedTransactionIds();

        if (failed.empty()) {
            cout << "none";
        } else {
            for (const string& id : failed) {
                cout << id << ' ';
            }
        }

        cout << "\n\nSuccessful totals by category:\n";

        const auto categoryTotals = successfulTotalsByCategory();

        for (const auto& [category, total] : categoryTotals) {
            cout << "  " << category << ": " << total << '\n';
        }

        cout << "\nStatus counts:\n";

        const auto counts = statusCounts();

        for (const auto& [status, count] : counts) {
            cout << "  " << statusToString(status)
                 << ": " << count << '\n';
        }
    }
};


// ============================================================================
// LOOP-BASED VALIDATION
// ============================================================================

int readPositiveIntegerFromValues(
    const vector<string>& simulatedInputs
) {
    for (const string& input : simulatedInputs) {
        try {
            size_t processedCharacters = 0;
            const long long value =
                stoll(input, &processedCharacters);

            if (processedCharacters != input.size()) {
                throw invalid_argument("input contains non-numeric characters");
            }

            if (value <= 0 ||
                value > numeric_limits<int>::max()) {
                throw invalid_argument(
                    "value must be a positive int"
                );
            }

            return static_cast<int>(value);
        } catch (const exception& error) {
            cout << "Rejected input '" << input
                 << "': " << error.what() << '\n';

            /*
             * continue moves to the next candidate.
             */
            continue;
        }
    }

    throw invalid_argument("no valid positive integer was supplied");
}


// ============================================================================
// MATRIX PROCESSING
// ============================================================================

vector<int> rowSums(const vector<vector<int>>& matrix) {
    vector<int> sums;

    for (const auto& row : matrix) {
        int total = 0;

        for (const int value : row) {
            total += value;
        }

        sums.push_back(total);
    }

    return sums;
}


vector<int> columnSums(const vector<vector<int>>& matrix) {
    if (matrix.empty()) {
        return {};
    }

    const size_t columnCount = matrix.front().size();

    for (const auto& row : matrix) {
        if (row.size() != columnCount) {
            throw invalid_argument("matrix must be rectangular");
        }
    }

    vector<int> sums(columnCount, 0);

    for (const auto& row : matrix) {
        for (size_t column = 0; column < columnCount; ++column) {
            sums[column] += row[column];
        }
    }

    return sums;
}


// ============================================================================
// COMPLEXITY DEMONSTRATIONS
// ============================================================================

long long linearWork(int n) {
    long long operations = 0;

    for (int index = 0; index < n; ++index) {
        ++operations;
    }

    return operations;
}


long long quadraticWork(int n) {
    long long operations = 0;

    for (int row = 0; row < n; ++row) {
        for (int column = 0; column < n; ++column) {
            ++operations;
        }
    }

    return operations;
}


long long triangularWork(int n) {
    long long operations = 0;

    for (int row = 1; row <= n; ++row) {
        for (int column = 0; column < row; ++column) {
            ++operations;
        }
    }

    return operations;
}


// ============================================================================
// TESTS
// ============================================================================

void runTests() {
    cout << "\n=== AUTOMATED TESTS ===\n";

    if (sumNumbers(5) != 15) {
        throw runtime_error("sumNumbers failed");
    }

    if (factorial(5) != 120) {
        throw runtime_error("factorial failed");
    }

    if (countDigits(0) != 1) {
        throw runtime_error("countDigits(0) failed");
    }

    if (countDigits(12345) != 5) {
        throw runtime_error("countDigits failed");
    }

    if (reverseNumber(12345) != 54321) {
        throw runtime_error("reverseNumber failed");
    }

    if (!isPalindrome(1221)) {
        throw runtime_error("palindrome failed");
    }

    if (isPalindrome(1234)) {
        throw runtime_error("non-palindrome failed");
    }

    if (!isPrime(2) || !isPrime(97) || isPrime(100)) {
        throw runtime_error("prime detection failed");
    }

    const auto fib = fibonacci(8);

    const vector<unsigned long long> expectedFib = {
        0, 1, 1, 2, 3, 5, 8, 13
    };

    if (fib != expectedFib) {
        throw runtime_error("Fibonacci failed");
    }

    const auto grid = multiplicationGrid(3);

    if (
        grid.size() != 3 ||
        grid[0][0] != 1 ||
        grid[2][2] != 9
    ) {
        throw runtime_error("multiplication grid failed");
    }

    const vector<Transaction> transactions = {
        {"TX001", 100.0, TransactionStatus::SUCCESS, "food"},
        {"TX002", 250.0, TransactionStatus::FAILED, "travel"},
        {"TX003", 300.0, TransactionStatus::SUCCESS, "travel"}
    };

    const TransactionMonitor monitor(transactions);

    if (monitor.successfulTotal() != 400.0) {
        throw runtime_error("transaction total failed");
    }

    const auto failed = monitor.failedTransactionIds();

    if (failed.size() != 1 || failed.front() != "TX002") {
        throw runtime_error("failed transaction test failed");
    }

    const auto found = monitor.findTransaction("TX003");

    if (!found.has_value() || found->amount != 300.0) {
        throw runtime_error("transaction lookup failed");
    }

    if (linearWork(10) != 10) {
        throw runtime_error("linear complexity test failed");
    }

    if (quadraticWork(4) != 16) {
        throw runtime_error("quadratic complexity test failed");
    }

    if (triangularWork(4) != 10) {
        throw runtime_error("triangular complexity test failed");
    }

    const vector<vector<int>> matrix = {
        {1, 2, 3},
        {4, 5, 6}
    };

    if (rowSums(matrix) != vector<int>({6, 15})) {
        throw runtime_error("row sums failed");
    }

    if (columnSums(matrix) != vector<int>({5, 7, 9})) {
        throw runtime_error("column sums failed");
    }

    cout << "All tests passed.\n";
}


// ============================================================================
// MAIN CASE STUDY
// ============================================================================

int main() {
    try {
        cout << "DAY 4 — LOOPS\n";
        cout << "Transaction Monitoring and Algorithmic Loop Case Study\n";

        demonstrateForLoop();
        demonstrateWhileLoop();
        demonstrateDoWhileLoop();
        demonstrateBreakAndContinue();

        cout << "\n=== NUMBER ALGORITHMS ===\n";

        cout << "Sum 1..100: "
             << sumNumbers(100)
             << '\n';

        cout << "5!: "
             << factorial(5)
             << '\n';

        cout << "Digits in 987654: "
             << countDigits(987654)
             << '\n';

        cout << "Reverse of 123456: "
             << reverseNumber(123456)
             << '\n';

        cout << "1221 palindrome: "
             << boolalpha
             << isPalindrome(1221)
             << '\n';

        cout << "Primes through 50:\n";

        const auto primes = generatePrimes(50);

        for (const int prime : primes) {
            cout << prime << ' ';
        }

        cout << "\n\nFibonacci sequence:\n";

        const auto fibonacciValues = fibonacci(12);

        for (const auto value : fibonacciValues) {
            cout << value << ' ';
        }

        cout << "\n\n=== PATTERN ===\n";
        printTriangle(5);

        cout << "\n=== MULTIPLICATION GRID ===\n";

        const auto grid = multiplicationGrid(5);
        printMultiplicationGrid(grid);

        cout << "\n=== VALIDATION ===\n";

        const vector<string> simulatedInputs = {
            "hello",
            "-5",
            "0",
            "42"
        };

        const int validatedValue =
            readPositiveIntegerFromValues(simulatedInputs);

        cout << "Accepted value: "
             << validatedValue
             << '\n';

        cout << "\n=== MATRIX PROCESSING ===\n";

        const vector<vector<int>> matrix = {
            {10, 20, 30},
            {40, 50, 60},
            {70, 80, 90}
        };

        cout << "Row sums: ";

        for (const int value : rowSums(matrix)) {
            cout << value << ' ';
        }

        cout << "\nColumn sums: ";

        for (const int value : columnSums(matrix)) {
            cout << value << ' ';
        }

        cout << "\n";

        cout << "\n=== COMPLEXITY ===\n";

        for (const int size : {5, 10, 100}) {
            cout << "n=" << size
                 << " linear=" << linearWork(size)
                 << " quadratic=" << quadraticWork(size)
                 << " triangular=" << triangularWork(size)
                 << '\n';
        }

        cout << "\n=== TRANSACTION MONITORING CASE STUDY ===\n";

        vector<Transaction> transactions = {
            {"TX001", 1250.00, TransactionStatus::SUCCESS, "food"},
            {"TX002", 5000.00, TransactionStatus::SUCCESS, "travel"},
            {"TX003", 800.00, TransactionStatus::FAILED, "food"},
            {"TX004", 2200.00, TransactionStatus::SUCCESS, "utilities"},
            {"TX005", 750.00, TransactionStatus::FAILED, "travel"},
            {"TX006", 15000.00, TransactionStatus::PENDING, "investment"},
            {"TX007", 7500.00, TransactionStatus::SUCCESS, "investment"}
        };

        TransactionMonitor monitor(move(transactions));

        monitor.printReport();

        cout << "\nHigh-value successful transactions above 4000:\n";

        const auto highValue =
            monitor.highValueSuccessfulTransactions(4000.0);

        for (const string& id : highValue) {
            cout << id << ' ';
        }

        cout << "\n";

        cout << "\nLookup TX004:\n";

        const auto transaction =
            monitor.findTransaction("TX004");

        if (transaction.has_value()) {
            cout << transaction->id
                 << " amount=" << transaction->amount
                 << " status=" << statusToString(transaction->status)
                 << " category=" << transaction->category
                 << '\n';
        }

        runTests();

        cout << "\nDAY 4 COMPLETE\n";
    }
    catch (const exception& error) {
        cerr << "Program error: "
             << error.what()
             << '\n';

        return 1;
    }

    return 0;
}
