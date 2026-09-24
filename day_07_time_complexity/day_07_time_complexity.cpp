/*
 * Day 7 — Time Complexity
 *
 * Detailed C++17 case study:
 * A scalable transaction-search and analytics engine for a fictional
 * financial operations system.
 *
 * The program demonstrates:
 *   O(1), O(log n), O(n), O(n log n), O(n²), and O(n³)
 *   sequential operations
 *   nested loops
 *   halving and doubling
 *   linear and binary search
 *   merge sort
 *   recursive algorithms
 *   validation
 *   edge cases
 *   algorithm selection
 *   timing
 *   time-space trade-offs
 *
 * Compile:
 *   g++ -std=c++17 -O2 day7_time_complexity.cpp -o day7
 *
 * Run:
 *   ./day7
 */

#include <algorithm>
#include <chrono>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

// ============================================================================
// 1. DATA MODEL
// ============================================================================

struct Transaction {
    long long id{};
    string accountId;
    double amount{};
    bool completed{};

    Transaction() = default;

    Transaction(
        long long transactionId,
        string account,
        double transactionAmount,
        bool transactionCompleted
    )
        : id(transactionId),
          accountId(std::move(account)),
          amount(transactionAmount),
          completed(transactionCompleted) {}
};

// ============================================================================
// 2. VALIDATION
// ============================================================================

void validateTransaction(const Transaction& transaction) {
    if (transaction.id <= 0) {
        throw invalid_argument("Transaction ID must be positive.");
    }

    if (transaction.accountId.empty()) {
        throw invalid_argument("Account ID cannot be empty.");
    }

    if (!isfinite(transaction.amount)) {
        throw invalid_argument("Transaction amount must be finite.");
    }

    if (transaction.amount < 0.0) {
        throw invalid_argument("Transaction amount cannot be negative.");
    }
}

// ============================================================================
// 3. O(1): CONSTANT-TIME OPERATION
// ============================================================================

Transaction getTransactionAt(
    const vector<Transaction>& transactions,
    size_t index
) {
    /*
     * vector indexing is O(1) under the standard random-access array model.
     *
     * The index is used directly to calculate the memory location.
     */
    if (index >= transactions.size()) {
        throw out_of_range("Transaction index is outside the vector.");
    }

    return transactions[index];
}

// ============================================================================
// 4. O(n): LINEAR SEARCH
// ============================================================================

int linearSearchById(
    const vector<Transaction>& transactions,
    long long transactionId
) {
    /*
     * Worst case:
     *   every transaction is inspected -> O(n)
     *
     * Best case:
     *   first transaction matches -> O(1)
     */
    for (size_t index = 0; index < transactions.size(); ++index) {
        if (transactions[index].id == transactionId) {
            return static_cast<int>(index);
        }
    }

    return -1;
}

// ============================================================================
// 5. O(log n): BINARY SEARCH
// ============================================================================

int binarySearchById(
    const vector<Transaction>& transactions,
    long long transactionId
) {
    /*
     * Binary search requires the vector to be sorted by transaction ID.
     *
     * Each comparison eliminates roughly half of the remaining search space.
     *
     * Time:  O(log n)
     * Space: O(1)
     */
    size_t left = 0;
    size_t right = transactions.size();

    while (left < right) {
        const size_t middle = left + (right - left) / 2;
        const long long middleId = transactions[middle].id;

        if (middleId == transactionId) {
            return static_cast<int>(middle);
        }

        if (middleId < transactionId) {
            left = middle + 1;
        } else {
            right = middle;
        }
    }

    return -1;
}

// ============================================================================
// 6. O(n): LINEAR ANALYTICS
// ============================================================================

double totalCompletedAmount(const vector<Transaction>& transactions) {
    /*
     * Every transaction must be inspected.
     *
     * Time: O(n)
     * Extra space: O(1)
     */
    double total = 0.0;

    for (const Transaction& transaction : transactions) {
        if (transaction.completed) {
            total += transaction.amount;
        }
    }

    return total;
}

size_t countCompletedTransactions(
    const vector<Transaction>& transactions
) {
    /*
     * Time: O(n)
     */
    size_t count = 0;

    for (const Transaction& transaction : transactions) {
        if (transaction.completed) {
            ++count;
        }
    }

    return count;
}

// ============================================================================
// 7. O(n²): DUPLICATE ACCOUNT PAIR DETECTION
// ============================================================================

vector<pair<string, string>> findAccountPairsQuadratic(
    const vector<Transaction>& transactions
) {
    /*
     * The system wants to identify transaction pairs that belong to the
     * same account.
     *
     * This deliberately simple implementation compares every pair.
     *
     * Number of comparisons:
     *   n(n-1)/2
     *
     * Therefore:
     *   O(n²)
     *
     * This is acceptable for small datasets but can become expensive as
     * n grows.
     */
    vector<pair<string, string>> matchingPairs;

    for (size_t i = 0; i < transactions.size(); ++i) {
        for (size_t j = i + 1; j < transactions.size(); ++j) {
            if (transactions[i].accountId == transactions[j].accountId) {
                matchingPairs.emplace_back(
                    transactions[i].accountId,
                    transactions[j].accountId
                );
            }
        }
    }

    return matchingPairs;
}

// ============================================================================
// 8. IMPROVED ACCOUNT COUNTING
// ============================================================================

unordered_map<string, size_t> countTransactionsByAccount(
    const vector<Transaction>& transactions
) {
    /*
     * Average-case hash-table insertion/lookup is approximately O(1).
     *
     * Therefore n insertions are approximately O(n) average time.
     *
     * This changes the problem from repeated pair comparisons to direct
     * aggregation, at the cost of O(k) additional storage where k is the
     * number of distinct accounts.
     */
    unordered_map<string, size_t> counts;

    for (const Transaction& transaction : transactions) {
        ++counts[transaction.accountId];
    }

    return counts;
}

// ============================================================================
// 9. O(n³): THREE-DIMENSIONAL RISK SCAN
// ============================================================================

long long cubicRiskScan(int dimensions) {
    /*
     * This models an intentionally expensive analysis across three
     * independent dimensions.
     *
     * If dimensions = n:
     *
     *   n * n * n = n³
     *
     * The function counts combinations instead of performing expensive
     * business calculations, making the growth pattern easy to observe.
     */
    if (dimensions < 0) {
        throw invalid_argument("dimensions cannot be negative.");
    }

    long long combinations = 0;

    for (int account = 0; account < dimensions; ++account) {
        for (int category = 0; category < dimensions; ++category) {
            for (int period = 0; period < dimensions; ++period) {
                ++combinations;
            }
        }
    }

    return combinations;
}

// ============================================================================
// 10. O(log n): HALVING AND DOUBLING
// ============================================================================

int halvingSteps(long long value) {
    /*
     * Repeated division by two produces logarithmic growth.
     *
     * Time: O(log n)
     */
    if (value <= 1) {
        return 0;
    }

    int steps = 0;

    while (value > 1) {
        value /= 2;
        ++steps;
    }

    return steps;
}

int doublingSteps(long long target) {
    /*
     * Repeated multiplication by two also requires O(log n) iterations.
     */
    if (target <= 1) {
        return 0;
    }

    long long value = 1;
    int steps = 0;

    while (value < target) {
        /*
         * Prevent signed overflow from turning an educational example into
         * undefined behavior.
         */
        if (value > numeric_limits<long long>::max() / 2) {
            ++steps;
            break;
        }

        value *= 2;
        ++steps;
    }

    return steps;
}

// ============================================================================
// 11. MERGE SORT: O(n log n)
// ============================================================================

void mergeRanges(
    vector<Transaction>& transactions,
    vector<Transaction>& temporary,
    size_t left,
    size_t middle,
    size_t right
) {
    /*
     * Merging two sorted ranges takes linear work relative to the number of
     * elements being merged.
     */
    size_t leftIndex = left;
    size_t rightIndex = middle;
    size_t outputIndex = left;

    while (leftIndex < middle && rightIndex < right) {
        if (transactions[leftIndex].id <= transactions[rightIndex].id) {
            temporary[outputIndex++] = transactions[leftIndex++];
        } else {
            temporary[outputIndex++] = transactions[rightIndex++];
        }
    }

    while (leftIndex < middle) {
        temporary[outputIndex++] = transactions[leftIndex++];
    }

    while (rightIndex < right) {
        temporary[outputIndex++] = transactions[rightIndex++];
    }

    for (size_t index = left; index < right; ++index) {
        transactions[index] = temporary[index];
    }
}

void mergeSortRecursive(
    vector<Transaction>& transactions,
    vector<Transaction>& temporary,
    size_t left,
    size_t right
) {
    /*
     * Each recursive level processes all n elements.
     *
     * Number of levels: O(log n)
     * Work per level: O(n)
     * Total: O(n log n)
     */
    if (right - left <= 1) {
        return;
    }

    const size_t middle = left + (right - left) / 2;

    mergeSortRecursive(
        transactions,
        temporary,
        left,
        middle
    );

    mergeSortRecursive(
        transactions,
        temporary,
        middle,
        right
    );

    mergeRanges(
        transactions,
        temporary,
        left,
        middle,
        right
    );
}

void mergeSortById(vector<Transaction>& transactions) {
    /*
     * The temporary vector creates O(n) auxiliary space.
     */
    if (transactions.size() <= 1) {
        return;
    }

    vector<Transaction> temporary(transactions.size());

    mergeSortRecursive(
        transactions,
        temporary,
        0,
        transactions.size()
    );
}

// ============================================================================
// 12. RECURSIVE COUNTDOWN: O(n)
// ============================================================================

int recursiveCountdown(int n) {
    /*
     * Recurrence:
     *
     *   T(n) = T(n-1) + O(1)
     *
     * Therefore:
     *
     *   T(n) = O(n)
     *
     * Recursive call stack:
     *
     *   O(n)
     */
    if (n <= 0) {
        return 0;
    }

    return 1 + recursiveCountdown(n - 1);
}

// ============================================================================
// 13. NAIVE FIBONACCI: EXPONENTIAL
// ============================================================================

long long naiveFibonacci(int n) {
    /*
     * Each call can create two more recursive calls.
     *
     * This produces exponential growth.
     *
     * The function is included as a complexity demonstration, not as a
     * production implementation.
     */
    if (n <= 1) {
        return n;
    }

    return naiveFibonacci(n - 1) + naiveFibonacci(n - 2);
}

// ============================================================================
// 14. ITERATIVE FIBONACCI: O(n)
// ============================================================================

long long dynamicFibonacci(int n) {
    /*
     * Each Fibonacci value is generated exactly once.
     *
     * Time: O(n)
     * Space: O(1)
     */
    if (n < 0) {
        throw invalid_argument("n must be non-negative.");
    }

    if (n <= 1) {
        return n;
    }

    long long previous = 0;
    long long current = 1;

    for (int i = 2; i <= n; ++i) {
        if (current > numeric_limits<long long>::max() - previous) {
            throw overflow_error(
                "Fibonacci result exceeds long long capacity."
            );
        }

        const long long next = previous + current;
        previous = current;
        current = next;
    }

    return current;
}

// ============================================================================
// 15. SEQUENTIAL COMPLEXITY
// ============================================================================

long long sequentialLinearWork(const vector<int>& values) {
    /*
     * Two O(n) loops are sequential:
     *
     *   O(n) + O(n)
     *   = O(2n)
     *   = O(n)
     */
    long long result = 0;

    for (int value : values) {
        result += value;
    }

    for (int value : values) {
        result += static_cast<long long>(value) * 2;
    }

    return result;
}

long long linearThenQuadratic(const vector<int>& values) {
    /*
     * O(n) + O(n²) = O(n²).
     */
    long long result = 0;

    for (int value : values) {
        result += value;
    }

    for (int first : values) {
        for (int second : values) {
            result += static_cast<long long>(first) * second;
        }
    }

    return result;
}

// ============================================================================
// 16. DATA GENERATION
// ============================================================================

vector<Transaction> generateTransactions(
    size_t count,
    unsigned int seed = 7
) {
    /*
     * Generating n records takes O(n) time.
     */
    vector<Transaction> transactions;
    transactions.reserve(count);

    mt19937 generator(seed);
    uniform_real_distribution<double> amountDistribution(10.0, 10000.0);
    uniform_int_distribution<int> accountDistribution(1, 20);
    bernoulli_distribution completionDistribution(0.75);

    for (size_t index = 0; index < count; ++index) {
        const int accountNumber = accountDistribution(generator);

        transactions.emplace_back(
            static_cast<long long>(index + 1),
            "ACC-" + to_string(accountNumber),
            amountDistribution(generator),
            completionDistribution(generator)
        );
    }

    return transactions;
}

// ============================================================================
// 17. ALGORITHM TIMING
// ============================================================================

template <typename Function>
double measureMilliseconds(Function&& function) {
    /*
     * This measures observed execution time.
     *
     * It does not prove Big O. Timing varies with CPU speed, compiler
     * optimizations, cache behavior, operating-system scheduling, and
     * implementation details.
     */
    const auto start = chrono::steady_clock::now();

    function();

    const auto end = chrono::steady_clock::now();

    const chrono::duration<double, milli> elapsed = end - start;
    return elapsed.count();
}

// ============================================================================
// 18. COMPLEXITY REPORT
// ============================================================================

void printComplexityReport() {
    cout << "\n" << string(78, '=') << "\n";
    cout << "COMPLEXITY REFERENCE\n";
    cout << string(78, '=') << "\n";

    struct ComplexityExample {
        string operation;
        string complexity;
        string reason;
    };

    const vector<ComplexityExample> examples = {
        {
            "Vector index access",
            "O(1)",
            "Direct random access."
        },
        {
            "Binary search",
            "O(log n)",
            "Search range is halved."
        },
        {
            "Linear scan",
            "O(n)",
            "Each element can be inspected."
        },
        {
            "Merge sort",
            "O(n log n)",
            "Logarithmic levels with linear work per level."
        },
        {
            "Two nested loops",
            "O(n^2)",
            "n times n combinations."
        },
        {
            "Three nested loops",
            "O(n^3)",
            "Three independent dimensions."
        }
    };

    for (const auto& example : examples) {
        cout << left
             << setw(25) << example.operation
             << setw(12) << example.complexity
             << example.reason
             << "\n";
    }
}

// ============================================================================
// 19. CORRECTNESS TESTS
// ============================================================================

void require(bool condition, const string& message) {
    if (!condition) {
        throw runtime_error("Test failed: " + message);
    }
}

void runTests() {
    cout << "\n" << string(78, '=') << "\n";
    cout << "CORRECTNESS TESTS\n";
    cout << string(78, '=') << "\n";

    vector<Transaction> transactions = {
        {1, "ACC-1", 100.0, true},
        {2, "ACC-2", 200.0, false},
        {3, "ACC-1", 300.0, true},
        {4, "ACC-3", 400.0, true}
    };

    require(getTransactionAt(transactions, 0).id == 1, "O(1) access");
    require(linearSearchById(transactions, 3) == 2, "linear search");
    require(linearSearchById(transactions, 99) == -1, "missing linear search");

    require(totalCompletedAmount(transactions) == 800.0, "completed total");
    require(countCompletedTransactions(transactions) == 3, "completed count");

    const auto accountCounts = countTransactionsByAccount(transactions);

    require(accountCounts.at("ACC-1") == 2, "account aggregation");
    require(accountCounts.at("ACC-2") == 1, "account aggregation 2");

    require(cubicRiskScan(3) == 27, "cubic scan");
    require(halvingSteps(8) == 3, "halving");
    require(doublingSteps(8) == 3, "doubling");

    vector<Transaction> searchable = {
        {5, "ACC-5", 500.0, true},
        {1, "ACC-1", 100.0, true},
        {4, "ACC-4", 400.0, true},
        {2, "ACC-2", 200.0, true},
        {3, "ACC-3", 300.0, true}
    };

    mergeSortById(searchable);

    require(searchable[0].id == 1, "merge sort first");
    require(searchable[4].id == 5, "merge sort last");

    require(binarySearchById(searchable, 3) == 2, "binary search");
    require(binarySearchById(searchable, 99) == -1, "missing binary search");

    require(recursiveCountdown(5) == 5, "recursive countdown");
    require(naiveFibonacci(10) == 55, "naive Fibonacci");

    for (int n = 0; n <= 20; ++n) {
        require(
            dynamicFibonacci(n) == naiveFibonacci(n),
            "Fibonacci consistency"
        );
    }

    require(
        sequentialLinearWork({1, 2, 3}) == 12,
        "sequential linear work"
    );

    cout << "All correctness tests passed.\n";
}

// ============================================================================
// 20. EDGE-CASE TESTING
// ============================================================================

void demonstrateEdgeCases() {
    cout << "\n" << string(78, '=') << "\n";
    cout << "EDGE CASES\n";
    cout << string(78, '=') << "\n";

    vector<Transaction> emptyTransactions;

    cout << "Empty linear search: "
         << linearSearchById(emptyTransactions, 1)
         << "\n";

    cout << "Halving 1: "
         << halvingSteps(1)
         << "\n";

    cout << "Doubling 1: "
         << doublingSteps(1)
         << "\n";

    try {
        getTransactionAt(emptyTransactions, 0);
    } catch (const exception& error) {
        cout << "Invalid vector access: "
             << error.what()
             << "\n";
    }

    try {
        validateTransaction(
            Transaction(0, "ACC-1", 100.0, true)
        );
    } catch (const exception& error) {
        cout << "Invalid transaction: "
             << error.what()
             << "\n";
    }

    try {
        dynamicFibonacci(-1);
    } catch (const exception& error) {
        cout << "Invalid Fibonacci input: "
             << error.what()
             << "\n";
    }
}

// ============================================================================
// 21. CASE STUDY REPORT
// ============================================================================

void printCaseStudyReport(
    const vector<Transaction>& transactions
) {
    cout << "\n" << string(78, '=') << "\n";
    cout << "FINANCIAL TRANSACTION ANALYTICS CASE STUDY\n";
    cout << string(78, '=') << "\n";

    cout << fixed << setprecision(2);

    cout << "Transactions: "
         << transactions.size()
         << "\n";

    cout << "Completed transactions: "
         << countCompletedTransactions(transactions)
         << "\n";

    cout << "Completed transaction value: "
         << totalCompletedAmount(transactions)
         << "\n";

    const auto counts = countTransactionsByAccount(transactions);

    cout << "Distinct accounts: "
         << counts.size()
         << "\n";

    /*
     * A quadratic pairwise scan is deliberately shown as a baseline.
     * A hash-table aggregation avoids comparing every pair.
     */
    const auto pairs = findAccountPairsQuadratic(transactions);

    cout << "Matching-account pairs found by quadratic scan: "
         << pairs.size()
         << "\n";

    vector<Transaction> sortedTransactions = transactions;

    const double sortingTime = measureMilliseconds(
        [&]() {
            mergeSortById(sortedTransactions);
        }
    );

    cout << "Merge sort time: "
         << sortingTime
         << " ms\n";

    if (!sortedTransactions.empty()) {
        const long long searchId = sortedTransactions.back().id;

        const double linearTime = measureMilliseconds(
            [&]() {
                volatile int result = linearSearchById(
                    sortedTransactions,
                    searchId
                );
                (void)result;
            }
        );

        const double binaryTime = measureMilliseconds(
            [&]() {
                volatile int result = binarySearchById(
                    sortedTransactions,
                    searchId
                );
                (void)result;
            }
        );

        cout << "Linear search time: "
             << linearTime
             << " ms\n";

        cout << "Binary search time: "
             << binaryTime
             << " ms\n";
    }
}

// ============================================================================
// 22. SCALING EXAMPLES
// ============================================================================

void printScalingExamples() {
    cout << "\n" << string(78, '=') << "\n";
    cout << "MATHEMATICAL SCALING\n";
    cout << string(78, '=') << "\n";

    const vector<long long> sizes = {
        10,
        100,
        1000,
        10000
    };

    cout << right
         << setw(8) << "n"
         << setw(14) << "log2(n)"
         << setw(14) << "n"
         << setw(18) << "n log2(n)"
         << setw(18) << "n²"
         << setw(22) << "n³"
         << "\n";

    for (long long n : sizes) {
        const double logN = log2(static_cast<double>(n));
        const double nLogN = n * logN;
        const long long nSquared = n * n;
        const long long nCubed = n * n * n;

        cout << setw(8) << n
             << setw(14) << fixed << setprecision(2) << logN
             << setw(14) << n
             << setw(18) << nLogN
             << setw(18) << nSquared
             << setw(22) << nCubed
             << "\n";
    }
}

// ============================================================================
// 23. MAIN
// ============================================================================

int main() {
    try {
        cout << string(78, '=') << "\n";
        cout << "DAY 7 — TIME COMPLEXITY\n";
        cout << string(78, '=') << "\n";

        cout << R"(
Time complexity describes how computational work grows as input size n
increases.

Important growth classes:

    O(1)       constant
    O(log n)   logarithmic
    O(n)       linear
    O(n log n) linearithmic
    O(n²)      quadratic
    O(n³)      cubic

The case study models a transaction-processing system and uses increasingly
scalable algorithms to demonstrate why complexity matters in production.
)";

        // --------------------------------------------------------------------
        // Basic O(1), O(n), O(n²), O(n³)
        // --------------------------------------------------------------------

        vector<Transaction> sample = {
            {1, "ACC-1", 100.0, true},
            {2, "ACC-2", 250.0, true},
            {3, "ACC-1", 150.0, false},
            {4, "ACC-3", 400.0, true}
        };

        cout << "\nConstant-time access, O(1): "
             << getTransactionAt(sample, 2).id
             << "\n";

        cout << "Linear completed amount, O(n): "
             << totalCompletedAmount(sample)
             << "\n";

        cout << "Quadratic pair comparisons, O(n²): "
             << findAccountPairsQuadratic(sample).size()
             << " matching pairs\n";

        cout << "Cubic combinations for n=4, O(n³): "
             << cubicRiskScan(4)
             << "\n";

        // --------------------------------------------------------------------
        // O(log n)
        // --------------------------------------------------------------------

        cout << "\nHalving 64: "
             << halvingSteps(64)
             << " steps\n";

        cout << "Doubling to 64: "
             << doublingSteps(64)
             << " steps\n";

        // --------------------------------------------------------------------
        // O(n log n)
        // --------------------------------------------------------------------

        vector<Transaction> unsorted = generateTransactions(15);

        cout << "\nFirst transaction ID before sorting: "
             << unsorted.front().id
             << "\n";

        reverse(unsorted.begin(), unsorted.end());

        cout << "First transaction ID after reversing: "
             << unsorted.front().id
             << "\n";

        mergeSortById(unsorted);

        cout << "First transaction ID after merge sort: "
             << unsorted.front().id
             << "\n";

        // --------------------------------------------------------------------
        // Binary search after sorting
        // --------------------------------------------------------------------

        const int foundIndex = binarySearchById(unsorted, 10);

        cout << "Binary search for transaction 10: "
             << foundIndex
             << "\n";

        // --------------------------------------------------------------------
        // Sequential operations
        // --------------------------------------------------------------------

        const vector<int> smallValues = {1, 2, 3, 4, 5};

        cout << "\nTwo sequential O(n) loops: "
             << sequentialLinearWork(smallValues)
             << "\n";

        cout << "O(n) followed by O(n²): "
             << linearThenQuadratic(smallValues)
             << "\n";

        // --------------------------------------------------------------------
        // Recursion
        // --------------------------------------------------------------------

        cout << "\nRecursive countdown, O(n): "
             << recursiveCountdown(5)
             << "\n";

        cout << "Naive Fibonacci, exponential time, n=10: "
             << naiveFibonacci(10)
             << "\n";

        cout << "Iterative Fibonacci, O(n), n=10: "
             << dynamicFibonacci(10)
             << "\n";

        // --------------------------------------------------------------------
        // Reports and tests
        // --------------------------------------------------------------------

        printComplexityReport();
        printScalingExamples();
        demonstrateEdgeCases();
        runTests();

        // --------------------------------------------------------------------
        // Larger industry-style dataset
        // --------------------------------------------------------------------

        vector<Transaction> productionLikeDataset =
            generateTransactions(5000);

        printCaseStudyReport(productionLikeDataset);

        cout << "\n" << string(78, '=') << "\n";
        cout << "CASE STUDY COMPLETE\n";
        cout << string(78, '=') << "\n";

        cout << R"(
The implementation demonstrates a central engineering principle:

An algorithm that works correctly on a small dataset may still be unsuitable
for a large production dataset if its work grows too quickly.

For example:
    O(n)       scales linearly.
    O(log n)   grows very slowly.
    O(n log n) is common for efficient comparison sorting.
    O(n²)      can become expensive quickly.
    O(n³)      becomes impractical much sooner for large n.

The appropriate algorithm depends on the input constraints, required output,
available memory, data organization, correctness requirements, and expected
workload.
)";

        return 0;
    }
    catch (const exception& error) {
        cerr << "\nFatal error: "
             << error.what()
             << "\n";

        return 1;
    }
}
