/*
 * Day 15 — Two Pointers
 *
 * C++17 technical case study:
 * "Order-aware transaction analytics and allocation engine"
 *
 * The program demonstrates two-pointer techniques in an industry-style
 * data-processing scenario:
 *
 * 1. Sorted transaction amounts and target pair detection.
 * 2. In-place normalization of sorted transaction IDs.
 * 3. Reverse processing of transaction records.
 * 4. Maximum capacity allocation using a container-style calculation.
 * 5. Three-value risk combinations.
 * 6. Partitioning transactions around a risk threshold.
 * 7. Dutch National Flag-style classification.
 * 8. Validation, exceptions, invariants, testing, and complexity.
 *
 * Standard: C++17
 */

#include <algorithm>
#include <cassert>
#include <cstddef>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

using namespace std;

// -----------------------------------------------------------------------------
// 1. DOMAIN MODEL
// -----------------------------------------------------------------------------

struct Transaction {
    int id;
    double amount;
    int riskLevel;

    bool operator==(const Transaction& other) const {
        return id == other.id &&
               amount == other.amount &&
               riskLevel == other.riskLevel;
    }
};

ostream& operator<<(ostream& output, const Transaction& transaction) {
    output << "{id=" << transaction.id
           << ", amount=" << fixed << setprecision(2)
           << transaction.amount
           << ", risk=" << transaction.riskLevel
           << "}";
    return output;
}

// -----------------------------------------------------------------------------
// 2. BASIC VALIDATION
// -----------------------------------------------------------------------------

void validateSortedNonDecreasing(const vector<int>& values) {
    if (!is_sorted(values.begin(), values.end())) {
        throw invalid_argument(
            "Input must be sorted in nondecreasing order."
        );
    }
}

void validateTransactionAmounts(const vector<double>& amounts) {
    for (double amount : amounts) {
        if (!isfinite(amount)) {
            throw invalid_argument(
                "Transaction amounts must be finite."
            );
        }

        if (amount < 0.0) {
            throw invalid_argument(
                "Transaction amounts cannot be negative."
            );
        }
    }
}

// -----------------------------------------------------------------------------
// 3. OPPOSITE-DIRECTION PAIR SUM
// -----------------------------------------------------------------------------

pair<size_t, size_t> pairSumSorted(
    const vector<int>& values,
    int target
) {
    validateSortedNonDecreasing(values);

    size_t left = 0;
    size_t right = values.size();

    if (right < 2) {
        throw runtime_error(
            "At least two values are required for pair search."
        );
    }

    --right;

    while (left < right) {
        /*
         * Because the array is sorted:
         *
         * sum < target:
         *   moving right leftward would only decrease the sum,
         *   so left must move right.
         *
         * sum > target:
         *   moving left rightward would only increase the sum,
         *   so right must move left.
         */
        const long long currentSum =
            static_cast<long long>(values[left]) +
            static_cast<long long>(values[right]);

        if (currentSum == target) {
            return {left, right};
        }

        if (currentSum < target) {
            ++left;
        } else {
            --right;
        }
    }

    throw runtime_error("No pair satisfies the requested target.");
}

// -----------------------------------------------------------------------------
// 4. SAME-DIRECTION READ/WRITE POINTER
// -----------------------------------------------------------------------------

size_t removeDuplicateTransactionIds(
    vector<Transaction>& transactions
) {
    if (transactions.empty()) {
        return 0;
    }

    /*
     * The input must be sorted by ID.
     *
     * read scans the source.
     * write marks the next position in the compacted result.
     *
     * The prefix [0, write) is always a valid duplicate-free result.
     */
    size_t write = 1;

    for (size_t read = 1; read < transactions.size(); ++read) {
        if (transactions[read].id != transactions[write - 1].id) {
            transactions[write] = transactions[read];
            ++write;
        }
    }

    return write;
}

// -----------------------------------------------------------------------------
// 5. IN-PLACE REVERSAL
// -----------------------------------------------------------------------------

void reverseTransactions(vector<Transaction>& transactions) {
    if (transactions.empty()) {
        return;
    }

    size_t left = 0;
    size_t right = transactions.size() - 1;

    while (left < right) {
        swap(transactions[left], transactions[right]);
        ++left;
        --right;
    }
}

// -----------------------------------------------------------------------------
// 6. CONTAINER-STYLE CAPACITY ANALYSIS
// -----------------------------------------------------------------------------

struct CapacityResult {
    size_t leftIndex;
    size_t rightIndex;
    double capacity;
};

CapacityResult maximumContainerCapacity(
    const vector<double>& heights
) {
    validateTransactionAmounts(heights);

    if (heights.size() < 2) {
        return {0, 0, 0.0};
    }

    size_t left = 0;
    size_t right = heights.size() - 1;

    double bestCapacity = 0.0;
    size_t bestLeft = 0;
    size_t bestRight = 0;

    while (left < right) {
        const double limitingHeight =
            min(heights[left], heights[right]);

        const double width =
            static_cast<double>(right - left);

        const double capacity =
            limitingHeight * width;

        if (capacity > bestCapacity) {
            bestCapacity = capacity;
            bestLeft = left;
            bestRight = right;
        }

        /*
         * The shorter side is the limiting factor.
         * Moving the taller side while keeping the shorter side fixed
         * cannot increase the limiting height.
         */
        if (heights[left] <= heights[right]) {
            ++left;
        } else {
            --right;
        }
    }

    return {bestLeft, bestRight, bestCapacity};
}

// -----------------------------------------------------------------------------
// 7. THREE-SUM RISK COMBINATIONS
// -----------------------------------------------------------------------------

struct RiskTriple {
    int first;
    int second;
    int third;

    bool operator<(const RiskTriple& other) const {
        return tie(first, second, third) <
               tie(other.first, other.second, other.third);
    }

    bool operator==(const RiskTriple& other) const {
        return tie(first, second, third) ==
               tie(other.first, other.second, other.third);
    }
};

vector<RiskTriple> threeSum(
    vector<int> values,
    int target
) {
    sort(values.begin(), values.end());

    vector<RiskTriple> result;

    if (values.size() < 3) {
        return result;
    }

    for (size_t i = 0; i + 2 < values.size(); ++i) {
        if (i > 0 && values[i] == values[i - 1]) {
            continue;
        }

        size_t left = i + 1;
        size_t right = values.size() - 1;

        while (left < right) {
            const long long currentSum =
                static_cast<long long>(values[i]) +
                static_cast<long long>(values[left]) +
                static_cast<long long>(values[right]);

            if (currentSum == target) {
                result.push_back({
                    values[i],
                    values[left],
                    values[right]
                });

                const int leftValue = values[left];
                const int rightValue = values[right];

                while (
                    left < right &&
                    values[left] == leftValue
                ) {
                    ++left;
                }

                while (
                    left < right &&
                    values[right] == rightValue
                ) {
                    --right;
                }
            } else if (currentSum < target) {
                ++left;
            } else {
                --right;
            }
        }
    }

    return result;
}

// -----------------------------------------------------------------------------
// 8. PARTITION-STYLE RISK CLASSIFICATION
// -----------------------------------------------------------------------------

size_t partitionRiskLevels(
    vector<Transaction>& transactions,
    int threshold
) {
    /*
     * Unstable partition:
     *
     * [0, boundary) contains risk < threshold.
     * [boundary, end) contains risk >= threshold.
     *
     * Time: O(n)
     * Extra space: O(1)
     */
    size_t boundary = 0;

    for (size_t current = 0;
         current < transactions.size();
         ++current) {

        if (transactions[current].riskLevel < threshold) {
            swap(
                transactions[boundary],
                transactions[current]
            );

            ++boundary;
        }
    }

    return boundary;
}

// -----------------------------------------------------------------------------
// 9. THREE-WAY CLASSIFICATION
// -----------------------------------------------------------------------------

void classifyRiskLevels(vector<int>& riskLevels) {
    /*
     * Valid values:
     *   0 = low
     *   1 = medium
     *   2 = high
     *
     * Invariant:
     *
     * [0, low)       => 0
     * [low, mid)     => 1
     * [mid, high]    => unknown
     * (high, end)    => 2
     */
    if (riskLevels.empty()) {
        return;
    }

    size_t low = 0;
    size_t mid = 0;
    size_t high = riskLevels.size() - 1;

    while (mid <= high) {
        if (riskLevels[mid] == 0) {
            swap(riskLevels[low], riskLevels[mid]);
            ++low;
            ++mid;
        } else if (riskLevels[mid] == 1) {
            ++mid;
        } else if (riskLevels[mid] == 2) {
            swap(riskLevels[mid], riskLevels[high]);

            if (high == 0) {
                break;
            }

            --high;
        } else {
            throw invalid_argument(
                "Risk level must be 0, 1, or 2."
            );
        }
    }
}

// -----------------------------------------------------------------------------
// 10. CLOSEST PAIR USING SORTING + TWO POINTERS
// -----------------------------------------------------------------------------

struct ClosestPair {
    int first;
    int second;
    long long difference;
};

ClosestPair closestPairToTarget(
    vector<int> values,
    int target
) {
    if (values.size() < 2) {
        throw invalid_argument(
            "At least two values are required."
        );
    }

    sort(values.begin(), values.end());

    size_t left = 0;
    size_t right = values.size() - 1;

    ClosestPair best{
        values[left],
        values[right],
        numeric_limits<long long>::max()
    };

    while (left < right) {
        const long long sum =
            static_cast<long long>(values[left]) +
            static_cast<long long>(values[right]);

        const long long difference =
            llabs(sum - static_cast<long long>(target));

        if (difference < best.difference) {
            best = {
                values[left],
                values[right],
                difference
            };
        }

        if (sum == target) {
            return best;
        }

        if (sum < target) {
            ++left;
        } else {
            --right;
        }
    }

    return best;
}

// -----------------------------------------------------------------------------
// 11. BUSINESS-STYLE REPORTING
// -----------------------------------------------------------------------------

void printTransactions(
    const vector<Transaction>& transactions,
    size_t logicalLength
) {
    const size_t length =
        min(logicalLength, transactions.size());

    for (size_t index = 0; index < length; ++index) {
        cout << "  " << transactions[index] << '\n';
    }
}

void printRiskTriples(
    const vector<RiskTriple>& triples
) {
    for (const auto& triple : triples) {
        cout << "  ("
             << triple.first << ", "
             << triple.second << ", "
             << triple.third << ")\n";
    }
}

// -----------------------------------------------------------------------------
// 12. RANDOMIZED VALIDATION
// -----------------------------------------------------------------------------

bool bruteForcePairExists(
    const vector<int>& values,
    int target
) {
    for (size_t i = 0; i < values.size(); ++i) {
        for (size_t j = i + 1; j < values.size(); ++j) {
            if (
                static_cast<long long>(values[i]) +
                static_cast<long long>(values[j]) ==
                target
            ) {
                return true;
            }
        }
    }

    return false;
}

bool twoPointerPairExists(
    const vector<int>& values,
    int target
) {
    if (values.size() < 2) {
        return false;
    }

    size_t left = 0;
    size_t right = values.size() - 1;

    while (left < right) {
        const long long sum =
            static_cast<long long>(values[left]) +
            static_cast<long long>(values[right]);

        if (sum == target) {
            return true;
        }

        if (sum < target) {
            ++left;
        } else {
            --right;
        }
    }

    return false;
}

void randomizedPairTest() {
    mt19937 generator(42);
    uniform_int_distribution<int> valueDistribution(-20, 20);
    uniform_int_distribution<int> targetDistribution(-30, 30);
    uniform_int_distribution<int> lengthDistribution(0, 15);

    for (int test = 0; test < 500; ++test) {
        const int length = lengthDistribution(generator);

        vector<int> values;
        values.reserve(static_cast<size_t>(length));

        for (int index = 0; index < length; ++index) {
            values.push_back(valueDistribution(generator));
        }

        sort(values.begin(), values.end());

        const int target = targetDistribution(generator);

        const bool expected =
            bruteForcePairExists(values, target);

        const bool actual =
            twoPointerPairExists(values, target);

        assert(expected == actual);
    }

    cout << "Randomized pair-sum validation: 500 cases passed.\n";
}

// -----------------------------------------------------------------------------
// 13. UNIT-STYLE TESTS
// -----------------------------------------------------------------------------

void runTests() {
    cout << "\n=== TESTS ===\n";

    {
        vector<int> values{1, 2, 4, 7, 11};
        const auto result = pairSumSorted(values, 9);
        assert(result.first == 1);
        assert(result.second == 3);
    }

    {
        vector<int> transactionsIds{1, 1, 2, 2, 3};

        vector<Transaction> transactions{
            {1, 10.0, 0},
            {1, 11.0, 1},
            {2, 20.0, 0},
            {2, 21.0, 2},
            {3, 30.0, 1}
        };

        const size_t length =
            removeDuplicateTransactionIds(transactions);

        assert(length == 3);
        assert(transactions[0].id == 1);
        assert(transactions[1].id == 2);
        assert(transactions[2].id == 3);

        (void)transactionsIds;
    }

    {
        vector<Transaction> transactions{
            {1, 10.0, 0},
            {2, 20.0, 1},
            {3, 30.0, 2}
        };

        reverseTransactions(transactions);

        assert(transactions[0].id == 3);
        assert(transactions[2].id == 1);
    }

    {
        const vector<double> heights{
            1, 8, 6, 2, 5, 4, 8, 3, 7
        };

        const CapacityResult result =
            maximumContainerCapacity(heights);

        assert(result.capacity == 49.0);
    }

    {
        const vector<RiskTriple> expected{
            {-1, -1, 2},
            {-1, 0, 1}
        };

        const vector<RiskTriple> actual =
            threeSum({-1, 0, 1, 2, -1, -4}, 0);

        assert(actual == expected);
    }

    {
        vector<int> riskLevels{2, 0, 2, 1, 1, 0};
        classifyRiskLevels(riskLevels);

        const vector<int> expected{0, 0, 1, 1, 2, 2};

        assert(riskLevels == expected);
    }

    {
        const ClosestPair result =
            closestPairToTarget({1, 4, 7, 10}, 11);

        assert(result.difference == 0);
        assert(result.first + result.second == 11);
    }

    {
        bool threw = false;

        try {
            validateSortedNonDecreasing({1, 5, 3});
        } catch (const invalid_argument&) {
            threw = true;
        }

        assert(threw);
    }

    randomizedPairTest();

    cout << "All tests passed.\n";
}

// -----------------------------------------------------------------------------
// 14. CASE STUDY
// -----------------------------------------------------------------------------

void runCaseStudy() {
    cout << "\n"
         << "======================================================================\n"
         << "INDUSTRY-STYLE CASE STUDY: TRANSACTION ANALYTICS ENGINE\n"
         << "======================================================================\n";

    /*
     * Scenario:
     *
     * A payment analytics component receives transaction amounts and risk
     * classifications. The component needs fast pair detection, duplicate
     * normalization, capacity-like range analysis, and risk partitioning.
     */

    vector<int> sortedAmounts{
        10, 20, 30, 40, 50, 60, 70, 80
    };

    const int targetAmount = 110;

    cout << "\n1. Pair settlement detection\n";

    try {
        const auto [left, right] =
            pairSumSorted(sortedAmounts, targetAmount);

        cout << "Target: " << targetAmount << '\n';
        cout << "Pair: "
             << sortedAmounts[left]
             << " + "
             << sortedAmounts[right]
             << '\n';
    } catch (const exception& error) {
        cout << "No matching pair: "
             << error.what() << '\n';
    }

    cout << "\n2. Duplicate transaction normalization\n";

    vector<Transaction> transactions{
        {1001, 1250.0, 0},
        {1001, 1250.0, 0},
        {1002, 2500.0, 1},
        {1002, 2500.0, 1},
        {1003, 4500.0, 2},
        {1004, 7000.0, 1},
        {1004, 7000.0, 1}
    };

    const size_t uniqueLength =
        removeDuplicateTransactionIds(transactions);

    cout << "Unique transaction records:\n";
    printTransactions(transactions, uniqueLength);

    cout << "\n3. Reverse audit processing order\n";

    vector<Transaction> auditRecords{
        {2001, 100.0, 0},
        {2002, 500.0, 1},
        {2003, 1000.0, 2},
        {2004, 250.0, 1}
    };

    reverseTransactions(auditRecords);

    printTransactions(
        auditRecords,
        auditRecords.size()
    );

    cout << "\n4. Maximum capacity-style analysis\n";

    vector<double> capacityProfile{
        1, 8, 6, 2, 5, 4, 8, 3, 7
    };

    const CapacityResult capacity =
        maximumContainerCapacity(capacityProfile);

    cout << "Best boundary indices: "
         << capacity.leftIndex
         << ", "
         << capacity.rightIndex
         << '\n';

    cout << "Maximum capacity: "
         << capacity.capacity
         << '\n';

    cout << "\n5. Three-risk combination detection\n";

    const vector<RiskTriple> riskCombinations =
        threeSum(
            {-1, 0, 1, 2, -1, -4},
            0
        );

    printRiskTriples(riskCombinations);

    cout << "\n6. Risk threshold partition\n";

    vector<Transaction> riskTransactions{
        {3001, 500.0, 2},
        {3002, 250.0, 0},
        {3003, 900.0, 1},
        {3004, 100.0, 0},
        {3005, 1500.0, 2}
    };

    const size_t lowRiskBoundary =
        partitionRiskLevels(riskTransactions, 1);

    cout << "Low-risk records:\n";
    printTransactions(
        riskTransactions,
        lowRiskBoundary
    );

    cout << "Records at or above threshold:\n";
    printTransactions(
        vector<Transaction>(
            riskTransactions.begin() + lowRiskBoundary,
            riskTransactions.end()
        ),
        riskTransactions.size() - lowRiskBoundary
    );

    cout << "\n7. Three-way risk classification\n";

    vector<int> classifications{
        2, 0, 1, 2, 1, 0, 2, 1
    };

    classifyRiskLevels(classifications);

    for (int risk : classifications) {
        cout << risk << ' ';
    }

    cout << "\n";

    cout << "\n8. Closest settlement pair\n";

    const ClosestPair closest =
        closestPairToTarget(
            {10, 25, 35, 50, 60, 75},
            72
        );

    cout << "Closest pair: "
         << closest.first
         << " + "
         << closest.second
         << ", absolute difference="
         << closest.difference
         << '\n';
}

// -----------------------------------------------------------------------------
// 15. MAIN
// -----------------------------------------------------------------------------

int main() {
    try {
        runCaseStudy();
        runTests();

        cout << "\n"
             << "======================================================================\n"
             << "COMPLEXITY NOTES\n"
             << "======================================================================\n"
             << "Sorted pair sum:                 O(n) time, O(1) extra space\n"
             << "Duplicate compaction:            O(n) time, O(1) extra space\n"
             << "In-place reversal:               O(n) time, O(1) extra space\n"
             << "Container capacity:              O(n) time, O(1) extra space\n"
             << "Three-sum after sorting:         O(n^2) time, O(n) copy space\n"
             << "Partitioning:                    O(n) time, O(1) extra space\n"
             << "Three-way classification:        O(n) time, O(1) extra space\n"
             << "Closest pair after sorting:      O(n log n) time, O(n) sort space\n";

        cout << "\n"
             << "The key design principle is not merely maintaining two indices.\n"
             << "A valid invariant must justify every pointer movement and prove\n"
             << "that discarded candidates can no longer produce a better answer.\n";

        return 0;
    } catch (const exception& error) {
        cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }
}
