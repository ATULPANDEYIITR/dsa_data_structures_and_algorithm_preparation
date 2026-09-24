/*
 * Day 11 — Complexity Practice
 *
 * C++ technical case study:
 * A small algorithm-analysis toolkit for processing a collection of product
 * records. The program demonstrates how the same business requirement can be
 * implemented with different algorithms and data structures, then analyzed
 * using time and space complexity.
 *
 * Requirements:
 *     C++17 or later
 *
 * Compile:
 *     g++ -std=c++17 -O2 day11_complexity_practice.cpp -o complexity_practice
 */

#include <algorithm>
#include <chrono>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

// ============================================================================
// 1. DOMAIN MODEL
// ============================================================================

struct Product {
    int id;
    string name;
    double price;
    int stock;
};

// ============================================================================
// 2. COMPLEXITY REPORT
// ============================================================================

struct ComplexityReport {
    string approach;
    string time;
    string space;
    string optimization;
};

void printReport(const string& title, const ComplexityReport& report) {
    cout << "\n=== " << title << " ===\n";
    cout << "Approach: " << report.approach << '\n';
    cout << "Time Complexity: " << report.time << '\n';
    cout << "Space Complexity: " << report.space << '\n';
    cout << "Possible Optimization: " << report.optimization << '\n';
}

// ============================================================================
// 3. LINEAR SEARCH
// ============================================================================

int findProductLinear(const vector<Product>& products, int productId) {
    /*
     * Each product may need to be inspected.
     *
     * Time:
     *     O(n) worst case
     *
     * Space:
     *     O(1) auxiliary space
     */
    for (size_t index = 0; index < products.size(); ++index) {
        if (products[index].id == productId) {
            return static_cast<int>(index);
        }
    }

    return -1;
}

// ============================================================================
// 4. BINARY SEARCH
// ============================================================================

int findProductBinary(const vector<Product>& sortedProducts, int productId) {
    /*
     * Binary search requires the vector to be sorted by id.
     *
     * Each iteration discards approximately half of the remaining elements.
     *
     * Time: O(log n)
     * Space: O(1)
     */
    int left = 0;
    int right = static_cast<int>(sortedProducts.size()) - 1;

    while (left <= right) {
        const int middle = left + (right - left) / 2;
        const int currentId = sortedProducts[middle].id;

        if (currentId == productId) {
            return middle;
        }

        if (currentId < productId) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return -1;
}

// ============================================================================
// 5. HASH-BASED INDEX
// ============================================================================

class ProductIndex {
private:
    unordered_map<int, size_t> positions;

public:
    explicit ProductIndex(const vector<Product>& products) {
        /*
         * Building the index requires one insertion per product.
         *
         * Average construction time: O(n)
         * Additional memory: O(n)
         */
        positions.reserve(products.size());

        for (size_t index = 0; index < products.size(); ++index) {
            positions[products[index].id] = index;
        }
    }

    int find(int productId) const {
        /*
         * Average hash-table lookup: O(1)
         *
         * Worst-case behavior can degrade if many keys collide, so the usual
         * O(1) classification is an average-case statement.
         */
        const auto iterator = positions.find(productId);

        if (iterator == positions.end()) {
            return -1;
        }

        return static_cast<int>(iterator->second);
    }
};

// ============================================================================
// 6. STOCK VALUE CALCULATION
// ============================================================================

double calculateTotalInventoryValue(const vector<Product>& products) {
    /*
     * Every product contributes price * stock.
     *
     * Time: O(n)
     * Space: O(1)
     */
    double total = 0.0;

    for (const Product& product : products) {
        total += product.price * static_cast<double>(product.stock);
    }

    return total;
}

// ============================================================================
// 7. LOW-STOCK FILTER
// ============================================================================

vector<Product> findLowStockProducts(
    const vector<Product>& products,
    int threshold
) {
    /*
     * Every product is inspected.
     *
     * Time: O(n)
     * Output space: O(k), where k is the number of returned products.
     * Worst case: O(n)
     */
    if (threshold < 0) {
        throw invalid_argument("threshold cannot be negative");
    }

    vector<Product> result;

    for (const Product& product : products) {
        if (product.stock <= threshold) {
            result.push_back(product);
        }
    }

    return result;
}

// ============================================================================
// 8. DUPLICATE ID DETECTION
// ============================================================================

bool containsDuplicateIds(const vector<Product>& products) {
    /*
     * A hash set gives average O(1) membership checks.
     *
     * Time: O(n) average
     * Space: O(n)
     */
    unordered_set<int> seen;
    seen.reserve(products.size());

    for (const Product& product : products) {
        if (!seen.insert(product.id).second) {
            return true;
        }
    }

    return false;
}

// ============================================================================
// 9. SORTING FOR BINARY SEARCH
// ============================================================================

vector<Product> sortProductsById(vector<Product> products) {
    /*
     * The argument is intentionally passed by value.
     *
     * This preserves the original collection but creates a copy.
     *
     * Copy: O(n)
     * Sorting: O(n log n)
     *
     * Total: O(n log n)
     *
     * Additional memory: O(n) for the copied vector.
     */
    sort(
        products.begin(),
        products.end(),
        [](const Product& first, const Product& second) {
            return first.id < second.id;
        }
    );

    return products;
}

// ============================================================================
// 10. TOP-LEVEL PRODUCT PRICE SEARCH
// ============================================================================

vector<Product> findProductsBelowPrice(
    const vector<Product>& products,
    double maximumPrice
) {
    /*
     * A full scan is necessary when the collection is not ordered by price.
     *
     * Time: O(n)
     * Output space: O(k), worst case O(n)
     */
    if (maximumPrice < 0.0) {
        throw invalid_argument("maximumPrice cannot be negative");
    }

    vector<Product> result;

    for (const Product& product : products) {
        if (product.price <= maximumPrice) {
            result.push_back(product);
        }
    }

    return result;
}

// ============================================================================
// 11. BRUTE-FORCE PAIR ANALYSIS
// ============================================================================

size_t countPairsWithTargetPrice(
    const vector<Product>& products,
    double target
) {
    /*
     * Every pair is examined.
     *
     * Number of iterations:
     *
     *     n(n - 1) / 2
     *
     * Therefore:
     *
     *     O(n^2)
     *
     * Only a counter is stored, so auxiliary space is O(1).
     */
    size_t count = 0;

    for (size_t first = 0; first < products.size(); ++first) {
        for (size_t second = first + 1; second < products.size(); ++second) {
            if (products[first].price + products[second].price == target) {
                ++count;
            }
        }
    }

    return count;
}

// ============================================================================
// 12. HASH-BASED PAIR ANALYSIS
// ============================================================================

size_t countPairsWithTargetPriceRounded(
    const vector<Product>& products,
    int targetCents
) {
    /*
     * Floating-point values should not normally be compared for exact
     * financial equality. This implementation converts prices to cents.
     *
     * For each price p, we need targetCents - p.
     *
     * Average:
     *     O(n) time
     *     O(n) auxiliary space
     */
    unordered_map<int, size_t> frequencies;
    frequencies.reserve(products.size());

    size_t count = 0;

    for (const Product& product : products) {
        const int cents = static_cast<int>(product.price * 100.0 + 0.5);
        const int required = targetCents - cents;

        auto iterator = frequencies.find(required);

        if (iterator != frequencies.end()) {
            count += iterator->second;
        }

        ++frequencies[cents];
    }

    return count;
}

// ============================================================================
// 13. FIBONACCI COMPLEXITY DEMONSTRATION
// ============================================================================

long long fibonacciNaive(int n) {
    /*
     * The recursion tree repeatedly recalculates the same subproblems.
     *
     * Time:
     *     exponential, commonly described as O(2^n) for introductory analysis
     *
     * Stack:
     *     O(n)
     */
    if (n < 0) {
        throw invalid_argument("n cannot be negative");
    }

    if (n <= 1) {
        return n;
    }

    return fibonacciNaive(n - 1) + fibonacciNaive(n - 2);
}

long long fibonacciIterative(int n) {
    /*
     * Time: O(n)
     * Auxiliary space: O(1)
     */
    if (n < 0) {
        throw invalid_argument("n cannot be negative");
    }

    long long previous = 0;
    long long current = 1;

    for (int index = 0; index < n; ++index) {
        const long long next = previous + current;
        previous = current;
        current = next;
    }

    return previous;
}

// ============================================================================
// 14. GENERIC BENCHMARK HELPER
// ============================================================================

template <typename Function>
long long benchmarkMilliseconds(Function function) {
    /*
     * Benchmarking provides empirical timing, not proof of asymptotic
     * complexity. Compiler optimization, cache behavior, CPU load, and
     * allocation can all affect the measured result.
     */
    const auto start = chrono::steady_clock::now();

    function();

    const auto end = chrono::steady_clock::now();

    return chrono::duration_cast<chrono::milliseconds>(
        end - start
    ).count();
}

// ============================================================================
// 15. SAMPLE DATA
// ============================================================================

vector<Product> createSampleProducts() {
    return {
        {101, "Keyboard", 49.99, 30},
        {205, "Mouse", 24.50, 8},
        {309, "Monitor", 249.99, 4},
        {412, "Webcam", 79.95, 18},
        {518, "Headset", 89.90, 6},
        {623, "USB Hub", 29.99, 40},
        {734, "SSD", 119.00, 12},
        {845, "Microphone", 149.50, 3},
        {956, "Laptop Stand", 39.99, 22},
        {1067, "Dock", 199.00, 5}
    };
}

// ============================================================================
// 16. DISPLAY
// ============================================================================

void printProducts(const vector<Product>& products) {
    cout << fixed << setprecision(2);

    for (const Product& product : products) {
        cout
            << "ID=" << product.id
            << " | " << product.name
            << " | Price=" << product.price
            << " | Stock=" << product.stock
            << '\n';
    }
}

// ============================================================================
// 17. INPUT VALIDATION
// ============================================================================

int readNonNegativeInteger(const string& prompt) {
    /*
     * This function demonstrates that validation is also part of a production
     * algorithm's behavior. Complexity analysis usually assumes valid input,
     * but production systems must handle invalid input explicitly.
     */
    int value;

    cout << prompt;

    if (!(cin >> value)) {
        throw invalid_argument("input must be an integer");
    }

    if (value < 0) {
        throw invalid_argument("value cannot be negative");
    }

    return value;
}

// ============================================================================
// 18. CASE STUDY
// ============================================================================

void runCaseStudy() {
    cout << "\n============================================================\n";
    cout << "C++ CASE STUDY: PRODUCT INVENTORY ANALYSIS\n";
    cout << "============================================================\n";

    vector<Product> products = createSampleProducts();

    cout << "\nInitial inventory:\n";
    printProducts(products);

    // ------------------------------------------------------------------------
    // Requirement 1: calculate total inventory value
    // ------------------------------------------------------------------------

    const double totalValue = calculateTotalInventoryValue(products);

    cout << fixed << setprecision(2);
    cout << "\nTotal inventory value: " << totalValue << '\n';

    printReport(
        "Inventory Value",
        {
            "Scan every product and add price * stock.",
            "O(n)",
            "O(1) auxiliary space.",
            "No asymptotic improvement is available when every product contributes to the total."
        }
    );

    // ------------------------------------------------------------------------
    // Requirement 2: low-stock products
    // ------------------------------------------------------------------------

    const vector<Product> lowStock = findLowStockProducts(products, 6);

    cout << "\nLow-stock products:\n";
    printProducts(lowStock);

    printReport(
        "Low-Stock Search",
        {
            "Scan all products and collect records at or below the threshold.",
            "O(n)",
            "O(k) output space, worst case O(n).",
            "An index organized by stock could help repeated threshold queries, but would add memory and maintenance cost."
        }
    );

    // ------------------------------------------------------------------------
    // Requirement 3: linear search
    // ------------------------------------------------------------------------

    const int linearPosition = findProductLinear(products, 734);

    cout << "\nLinear search for product 734: "
         << linearPosition << '\n';

    printReport(
        "Linear Product Search",
        {
            "Inspect product IDs from left to right.",
            "O(n) worst case.",
            "O(1) auxiliary space.",
            "Use sorted data with binary search or a hash index for repeated lookups."
        }
    );

    // ------------------------------------------------------------------------
    // Requirement 4: binary search after sorting
    // ------------------------------------------------------------------------

    const vector<Product> sortedProducts = sortProductsById(products);
    const int binaryPosition = findProductBinary(sortedProducts, 734);

    cout << "\nBinary search for product 734 after sorting: "
         << binaryPosition << '\n';

    printReport(
        "Sort Plus Binary Search",
        {
            "Sort once by product ID and then use binary search.",
            "O(n log n) preprocessing plus O(log n) per lookup.",
            "O(n) here because this implementation creates a sorted copy.",
            "For many repeated lookups, preprocessing can be worthwhile."
        }
    );

    // ------------------------------------------------------------------------
    // Requirement 5: hash index
    // ------------------------------------------------------------------------

    const ProductIndex index(products);

    cout << "\nHash index search for product 734: "
         << index.find(734) << '\n';

    printReport(
        "Hash Index",
        {
            "Build a hash table mapping product ID to its position.",
            "O(n) average construction and O(1) average lookup.",
            "O(n) auxiliary space.",
            "Useful for frequent ID lookups, but memory and hash-table behavior must be considered."
        }
    );

    // ------------------------------------------------------------------------
    // Requirement 6: pair analysis
    // ------------------------------------------------------------------------

    const size_t bruteForcePairs =
        countPairsWithTargetPrice(products, 99.49);

    cout << "\nBrute-force matching price pairs: "
         << bruteForcePairs << '\n';

    printReport(
        "Brute-Force Pair Search",
        {
            "Compare every unique pair of products.",
            "O(n^2)",
            "O(1) auxiliary space.",
            "Hashing can reduce the average computation to O(n) when the problem can be transformed into complement lookups."
        }
    );

    const size_t optimizedPairs =
        countPairsWithTargetPriceRounded(products, 99.49);

    cout << "Hash-based matching price pairs: "
         << optimizedPairs << '\n';

    printReport(
        "Hash-Based Pair Search",
        {
            "Store previously seen prices and look up the required complement.",
            "O(n) average.",
            "O(n) auxiliary space.",
            "Use this when memory is available and fast repeated matching is more important than minimizing auxiliary space."
        }
    );
}

// ============================================================================
// 19. COMPLEXITY READING EXAMPLES
// ============================================================================

void printCodeReadingLessons() {
    cout << R"(
============================================================
CODE-READING COMPLEXITY PRACTICE
============================================================

Pattern 1:

    for (int i = 0; i < n; ++i) {
        operation();
    }

Time: O(n)

Pattern 2:

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            operation();
        }
    }

Time: O(n^2)

Pattern 3:

    int value = 1;

    while (value < n) {
        value *= 2;
    }

Time: O(log n)

Pattern 4:

    for (int i = 0; i < n; ++i) {
        linearSearch(values, target);
    }

If linearSearch is O(n), the total is O(n^2).

Pattern 5:

    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            operation();
        }
    }

The total number of operations is:

    n(n - 1) / 2

Therefore:

    O(n^2)

Pattern 6:

    for (int i = 0; i < n; ++i) {
        doLogarithmicWork();
    }

If doLogarithmicWork() is O(log n):

    O(n log n)

)" << '\n';
}

// ============================================================================
// 20. EDGE CASE TESTS
// ============================================================================

void runEdgeCaseTests() {
    cout << "\n============================================================\n";
    cout << "EDGE CASES\n";
    cout << "============================================================\n";

    const vector<Product> emptyProducts;
    const vector<Product> oneProduct = {
        {1, "Single", 10.00, 1}
    };

    cout << "Empty linear search: "
         << findProductLinear(emptyProducts, 1) << '\n';

    cout << "Single-product search: "
         << findProductLinear(oneProduct, 1) << '\n';

    cout << "Empty inventory value: "
         << calculateTotalInventoryValue(emptyProducts) << '\n';

    cout << "Single inventory value: "
         << calculateTotalInventoryValue(oneProduct) << '\n';

    try {
        findLowStockProducts(oneProduct, -1);
    } catch (const exception& error) {
        cout << "Invalid threshold handled: "
             << error.what() << '\n';
    }

    try {
        fibonacciIterative(-1);
    } catch (const exception& error) {
        cout << "Invalid Fibonacci input handled: "
             << error.what() << '\n';
    }
}

// ============================================================================
// 21. BENCHMARK DEMONSTRATION
// ============================================================================

vector<Product> createBenchmarkProducts(size_t count) {
    vector<Product> products;
    products.reserve(count);

    for (size_t index = 0; index < count; ++index) {
        products.push_back(
            Product{
                static_cast<int>(index + 1),
                "Product-" + to_string(index + 1),
                static_cast<double>((index % 1000) + 1) / 3.0,
                static_cast<int>(index % 50) + 1
            }
        );
    }

    return products;
}

void runBenchmark() {
    /*
     * The quadratic example is deliberately kept moderate. The point is to
     * observe growth without producing an unnecessarily large allocation.
     */
    const vector<Product> products = createBenchmarkProducts(1500);

    volatile double linearResult = 0.0;
    volatile size_t quadraticResult = 0;

    const long long linearMilliseconds = benchmarkMilliseconds([&]() {
        linearResult = calculateTotalInventoryValue(products);
    });

    const long long quadraticMilliseconds = benchmarkMilliseconds([&]() {
        quadraticResult = countPairsWithTargetPrice(products, 100.0);
    });

    cout << "\n============================================================\n";
    cout << "SMALL BENCHMARK\n";
    cout << "============================================================\n";

    cout << "Linear operation: "
         << linearMilliseconds << " ms\n";

    cout << "Quadratic operation: "
         << quadraticMilliseconds << " ms\n";

    /*
     * Prevent the compiler from treating the calculated results as unused.
     */
    cout << "Benchmark guard values: "
         << linearResult << ", "
         << quadraticResult << '\n';

    cout
        << "Measured timing is environment-dependent and does not replace "
        << "asymptotic analysis.\n";
}

// ============================================================================
// 22. MAIN
// ============================================================================

int main() {
    try {
        cout << "DAY 11 — COMPLEXITY PRACTICE\n";

        runCaseStudy();
        printCodeReadingLessons();
        runEdgeCaseTests();
        runBenchmark();

        cout << R"(
============================================================
PHASE CHECKPOINT
============================================================

A strong complexity analysis should answer:

1. What is the input size?
2. What operation dominates the running time?
3. How many times does that operation execute?
4. Are loops sequential or nested?
5. Does the problem size shrink by a constant factor?
6. Are expensive functions called inside loops?
7. Does recursion create repeated subproblems?
8. How much additional memory is allocated?
9. Is the stated complexity worst-case or average-case?
10. Can a data structure or algorithm change the growth rate?

The central Day 11 skill is estimating approximate time and space complexity
from unfamiliar code without executing it first.
)" << '\n';

        return 0;
    } catch (const exception& error) {
        cerr << "Program error: " << error.what() << '\n';
        return 1;
    }
}
