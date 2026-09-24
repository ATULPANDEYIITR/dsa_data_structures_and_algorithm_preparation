#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <optional>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

/*
 * Day 14 — Prefix Sums
 *
 * Industry-style case study:
 *
 * A retail analytics system receives a sequence of daily net transaction
 * changes. Analysts need to perform:
 *
 *   1. Fast historical range-sum queries.
 *   2. Detection of equilibrium periods.
 *   3. Counting of contiguous periods with a target total.
 *   4. Longest contiguous period with a target total.
 *   5. Detection of zero-sum periods.
 *   6. Multiple interval updates.
 *
 * The implementation develops these features progressively.
 *
 * C++17 or later.
 */


// -----------------------------------------------------------------------------
// 1. BASIC PREFIX-SUM DATA STRUCTURE
// -----------------------------------------------------------------------------

class PrefixSumArray {
private:
    vector<long long> prefix;

public:
    explicit PrefixSumArray(const vector<long long>& values) {
        prefix.resize(values.size() + 1, 0);

        for (size_t index = 0; index < values.size(); ++index) {
            prefix[index + 1] =
                prefix[index] + values[index];
        }
    }

    size_t size() const {
        return prefix.size() - 1;
    }

    long long rangeSum(size_t left, size_t right) const {
        if (left > right) {
            throw invalid_argument(
                "left cannot be greater than right"
            );
        }

        if (right >= size()) {
            throw out_of_range(
                "range endpoint is outside the array"
            );
        }

        return prefix[right + 1] - prefix[left];
    }

    long long totalSum() const {
        return prefix.back();
    }

    const vector<long long>& data() const {
        return prefix;
    }
};


// -----------------------------------------------------------------------------
// 2. NAIVE REFERENCE IMPLEMENTATION
// -----------------------------------------------------------------------------

long long naiveRangeSum(
    const vector<long long>& values,
    size_t left,
    size_t right
) {
    if (left > right || right >= values.size()) {
        throw out_of_range("Invalid range.");
    }

    long long total = 0;

    for (size_t index = left; index <= right; ++index) {
        total += values[index];
    }

    return total;
}


// -----------------------------------------------------------------------------
// 3. RANGE QUERY SERVICE
// -----------------------------------------------------------------------------

class TransactionAnalytics {
private:
    vector<long long> dailyChanges;
    PrefixSumArray prefix;

public:
    explicit TransactionAnalytics(
        vector<long long> values
    )
        : dailyChanges(std::move(values)),
          prefix(dailyChanges) {}

    long long queryRange(
        size_t left,
        size_t right
    ) const {
        return prefix.rangeSum(left, right);
    }

    long long totalChange() const {
        return prefix.totalSum();
    }

    const vector<long long>& values() const {
        return dailyChanges;
    }
};


// -----------------------------------------------------------------------------
// 4. EQUILIBRIUM INDEX
// -----------------------------------------------------------------------------

vector<size_t> equilibriumIndices(
    const vector<long long>& values
) {
    long long total =
        accumulate(values.begin(), values.end(), 0LL);

    long long leftSum = 0;
    vector<size_t> result;

    for (size_t index = 0; index < values.size(); ++index) {
        long long rightSum =
            total - leftSum - values[index];

        if (leftSum == rightSum) {
            result.push_back(index);
        }

        leftSum += values[index];
    }

    return result;
}


// -----------------------------------------------------------------------------
// 5. COUNT SUBARRAYS WITH SUM K
// -----------------------------------------------------------------------------

long long countSubarraysWithSumK(
    const vector<long long>& values,
    long long target
) {
    /*
     * If:
     *
     *     prefix[j] - prefix[i] = target
     *
     * then:
     *
     *     prefix[i] = prefix[j] - target
     *
     * A hash map stores how frequently each previous prefix sum appeared.
     *
     * The initial prefix 0 is stored once so subarrays beginning at
     * index 0 are included.
     */
    unordered_map<long long, long long> frequency;

    frequency[0] = 1;

    long long runningSum = 0;
    long long count = 0;

    for (long long value : values) {
        runningSum += value;

        long long requiredPrefix =
            runningSum - target;

        auto iterator = frequency.find(requiredPrefix);

        if (iterator != frequency.end()) {
            count += iterator->second;
        }

        ++frequency[runningSum];
    }

    return count;
}


// -----------------------------------------------------------------------------
// 6. LONGEST SUBARRAY WITH SUM K
// -----------------------------------------------------------------------------

struct SubarrayResult {
    long long length;
    optional<pair<size_t, size_t>> range;
};

SubarrayResult longestSubarrayWithSumK(
    const vector<long long>& values,
    long long target
) {
    /*
     * For the longest subarray, retain only the earliest occurrence of
     * each prefix sum. The earliest compatible prefix produces the
     * largest possible distance.
     */
    unordered_map<long long, long long> firstOccurrence;

    firstOccurrence[0] = -1;

    long long runningSum = 0;
    long long bestLength = 0;
    optional<pair<size_t, size_t>> bestRange;

    for (size_t index = 0; index < values.size(); ++index) {
        runningSum += values[index];

        long long requiredPrefix =
            runningSum - target;

        auto iterator =
            firstOccurrence.find(requiredPrefix);

        if (iterator != firstOccurrence.end()) {
            long long previousIndex = iterator->second;
            long long length =
                static_cast<long long>(index)
                - previousIndex;

            if (length > bestLength) {
                bestLength = length;

                bestRange = make_pair(
                    static_cast<size_t>(previousIndex + 1),
                    index
                );
            }
        }

        // Do not overwrite an earlier occurrence.
        if (!firstOccurrence.contains(runningSum)) {
            firstOccurrence[runningSum] =
                static_cast<long long>(index);
        }
    }

    return {bestLength, bestRange};
}


// -----------------------------------------------------------------------------
// 7. ZERO-SUM SUBARRAYS
// -----------------------------------------------------------------------------

long long countZeroSumSubarrays(
    const vector<long long>& values
) {
    /*
     * Two equal prefix sums define a zero-sum subarray between them.
     */
    unordered_map<long long, long long> frequency;

    frequency[0] = 1;

    long long runningSum = 0;
    long long result = 0;

    for (long long value : values) {
        runningSum += value;

        result += frequency[runningSum];
        ++frequency[runningSum];
    }

    return result;
}


// -----------------------------------------------------------------------------
// 8. PREFIX-FREQUENCY ANALYTICS
// -----------------------------------------------------------------------------

map<long long, long long> prefixFrequency(
    const vector<long long>& values
) {
    map<long long, long long> frequency;

    long long runningSum = 0;
    ++frequency[0];

    for (long long value : values) {
        runningSum += value;
        ++frequency[runningSum];
    }

    return frequency;
}


// -----------------------------------------------------------------------------
// 9. SUBARRAYS DIVISIBLE BY K
// -----------------------------------------------------------------------------

long long countSubarraysDivisibleByK(
    const vector<long long>& values,
    long long k
) {
    if (k == 0) {
        throw invalid_argument(
            "Divisor k cannot be zero."
        );
    }

    k = llabs(k);

    unordered_map<long long, long long> frequency;
    frequency[0] = 1;

    long long runningSum = 0;
    long long result = 0;

    for (long long value : values) {
        runningSum += value;

        long long remainder =
            ((runningSum % k) + k) % k;

        result += frequency[remainder];
        ++frequency[remainder];
    }

    return result;
}


// -----------------------------------------------------------------------------
// 10. PREFIX XOR
// -----------------------------------------------------------------------------

long long countSubarraysWithXorK(
    const vector<long long>& values,
    long long target
) {
    /*
     * XOR has an analogous identity:
     *
     * A XOR B = K
     * B = A XOR K
     *
     * Prefix XOR therefore supports the same frequency-map strategy.
     */
    unordered_map<long long, long long> frequency;
    frequency[0] = 1;

    long long runningXor = 0;
    long long result = 0;

    for (long long value : values) {
        runningXor ^= value;

        long long requiredPrefix =
            runningXor ^ target;

        result += frequency[requiredPrefix];
        ++frequency[runningXor];
    }

    return result;
}


// -----------------------------------------------------------------------------
// 11. TWO-DIMENSIONAL PREFIX SUM
// -----------------------------------------------------------------------------

class MatrixPrefixSum {
private:
    vector<vector<long long>> prefix;

public:
    explicit MatrixPrefixSum(
        const vector<vector<long long>>& matrix
    ) {
        if (matrix.empty()) {
            prefix = {{0}};
            return;
        }

        const size_t columns = matrix.front().size();

        for (const auto& row : matrix) {
            if (row.size() != columns) {
                throw invalid_argument(
                    "Matrix rows must have equal lengths."
                );
            }
        }

        prefix.assign(
            matrix.size() + 1,
            vector<long long>(columns + 1, 0)
        );

        for (size_t row = 1;
             row <= matrix.size();
             ++row) {

            for (size_t column = 1;
                 column <= columns;
                 ++column) {

                prefix[row][column] =
                    matrix[row - 1][column - 1]
                    + prefix[row - 1][column]
                    + prefix[row][column - 1]
                    - prefix[row - 1][column - 1];
            }
        }
    }

    long long rectangleSum(
        size_t top,
        size_t left,
        size_t bottom,
        size_t right
    ) const {
        if (top > bottom || left > right) {
            throw invalid_argument(
                "Invalid rectangle."
            );
        }

        if (bottom + 1 >= prefix.size() ||
            right + 1 >= prefix.front().size()) {
            throw out_of_range(
                "Rectangle lies outside matrix."
            );
        }

        return
            prefix[bottom + 1][right + 1]
            - prefix[top][right + 1]
            - prefix[bottom + 1][left]
            + prefix[top][left];
    }

    const auto& data() const {
        return prefix;
    }
};


// -----------------------------------------------------------------------------
// 12. DIFFERENCE ARRAY FOR RANGE UPDATES
// -----------------------------------------------------------------------------

vector<long long> applyRangeUpdates(
    size_t size,
    const vector<tuple<size_t, size_t, long long>>& updates
) {
    /*
     * Instead of modifying every position in each range:
     *
     *     difference[left] += delta
     *     difference[right + 1] -= delta
     *
     * One final prefix accumulation reconstructs the values.
     */
    vector<long long> difference(size + 1, 0);

    for (const auto& [left, right, delta] : updates) {
        if (left > right || right >= size) {
            throw out_of_range(
                "Invalid range update."
            );
        }

        difference[left] += delta;
        difference[right + 1] -= delta;
    }

    vector<long long> result(size);
    long long runningValue = 0;

    for (size_t index = 0; index < size; ++index) {
        runningValue += difference[index];
        result[index] = runningValue;
    }

    return result;
}


// -----------------------------------------------------------------------------
// 13. SLIDING-WINDOW COMPARISON
// -----------------------------------------------------------------------------

long long countPositiveSubarraysWithSumAtMostK(
    const vector<long long>& values,
    long long k
) {
    /*
     * This is deliberately not a general replacement for prefix sums.
     *
     * It relies on all values being strictly positive. Under that
     * condition, increasing the right edge increases the sum and moving
     * the left edge forward decreases it.
     */
    for (long long value : values) {
        if (value <= 0) {
            throw invalid_argument(
                "Sliding-window method requires positive values."
            );
        }
    }

    size_t left = 0;
    long long runningSum = 0;
    long long result = 0;

    for (size_t right = 0;
         right < values.size();
         ++right) {

        runningSum += values[right];

        while (runningSum > k && left <= right) {
            runningSum -= values[left];
            ++left;
        }

        result += static_cast<long long>(
            right - left + 1
        );
    }

    return result;
}


// -----------------------------------------------------------------------------
// 14. TESTING UTILITIES
// -----------------------------------------------------------------------------

void testRangeSum() {
    mt19937 generator(42);

    uniform_int_distribution<int> lengthDistribution(1, 30);
    uniform_int_distribution<int> valueDistribution(-20, 20);

    for (int trial = 0; trial < 100; ++trial) {
        int length = lengthDistribution(generator);

        vector<long long> values(length);

        for (auto& value : values) {
            value = valueDistribution(generator);
        }

        PrefixSumArray prefix(values);

        uniform_int_distribution<int> indexDistribution(
            0,
            length - 1
        );

        for (int query = 0; query < 30; ++query) {
            size_t left =
                static_cast<size_t>(
                    indexDistribution(generator)
                );

            uniform_int_distribution<int> rightDistribution(
                static_cast<int>(left),
                length - 1
            );

            size_t right =
                static_cast<size_t>(
                    rightDistribution(generator)
                );

            assert(
                prefix.rangeSum(left, right)
                ==
                naiveRangeSum(values, left, right)
            );
        }
    }

    cout << "Range-sum randomized validation: PASSED\n";
}


void testSubarraySumK() {
    mt19937 generator(7);

    uniform_int_distribution<int> lengthDistribution(0, 15);
    uniform_int_distribution<int> valueDistribution(-5, 5);
    uniform_int_distribution<int> targetDistribution(-5, 5);

    for (int trial = 0; trial < 100; ++trial) {
        int length = lengthDistribution(generator);

        vector<long long> values(length);

        for (auto& value : values) {
            value = valueDistribution(generator);
        }

        long long target =
            targetDistribution(generator);

        long long optimized =
            countSubarraysWithSumK(values, target);

        long long bruteForce = 0;

        for (size_t left = 0;
             left < values.size();
             ++left) {

            long long runningSum = 0;

            for (size_t right = left;
                 right < values.size();
                 ++right) {

                runningSum += values[right];

                if (runningSum == target) {
                    ++bruteForce;
                }
            }
        }

        assert(optimized == bruteForce);
    }

    cout << "Subarray-sum randomized validation: PASSED\n";
}


// -----------------------------------------------------------------------------
// 15. DISPLAY FUNCTIONS
// -----------------------------------------------------------------------------

void printVector(
    const vector<long long>& values,
    const string& label
) {
    cout << label << "[ ";

    for (long long value : values) {
        cout << value << ' ';
    }

    cout << "]\n";
}

void printIndices(
    const vector<size_t>& indices
) {
    cout << "[ ";

    for (size_t index : indices) {
        cout << index << ' ';
    }

    cout << "]\n";
}


// -----------------------------------------------------------------------------
// 16. INDUSTRY-STYLE CASE STUDY
// -----------------------------------------------------------------------------

void runRetailAnalyticsCaseStudy() {
    /*
     * Each value represents the net daily transaction change:
     *
     * positive -> net inflow
     * negative -> net outflow
     *
     * The system is read-heavy, so preprocessing a prefix array makes
     * repeated historical queries inexpensive.
     */
    vector<long long> dailyChanges = {
        120, -20, 50, 80, -10, 60, 30
    };

    TransactionAnalytics analytics(dailyChanges);

    cout << "\n=== Retail transaction analytics ===\n";

    printVector(
        dailyChanges,
        "Daily changes: "
    );

    cout << "Total change: "
         << analytics.totalChange()
         << '\n';

    cout << "Range [2, 5]: "
         << analytics.queryRange(2, 5)
         << '\n';

    cout << "Range [0, 6]: "
         << analytics.queryRange(0, 6)
         << '\n';

    cout << "Equilibrium indices: ";
    printIndices(
        equilibriumIndices(dailyChanges)
    );

    const long long target = 100;

    cout << "Subarrays totaling "
         << target
         << ": "
         << countSubarraysWithSumK(
                dailyChanges,
                target
            )
         << '\n';

    auto longest =
        longestSubarrayWithSumK(
            dailyChanges,
            target
        );

    cout << "Longest subarray totaling "
         << target
         << ": length="
         << longest.length;

    if (longest.range.has_value()) {
        auto [left, right] =
            longest.range.value();

        cout << ", range=["
             << left
             << ", "
             << right
             << ']';
    }

    cout << '\n';

    cout << "Zero-sum subarrays: "
         << countZeroSumSubarrays(dailyChanges)
         << '\n';

    cout << "Subarrays divisible by 10: "
         << countSubarraysDivisibleByK(
                dailyChanges,
                10
            )
         << '\n';
}


// -----------------------------------------------------------------------------
// 17. EDGE CASES
// -----------------------------------------------------------------------------

void demonstrateEdgeCases() {
    cout << "\n=== Edge cases ===\n";

    vector<vector<long long>> cases = {
        {},
        {0},
        {5},
        {-5},
        {0, 0, 0},
        {-1, -2, -3},
        {
            1'000'000'000'000LL,
            -1'000'000'000'000LL
        }
    };

    for (const auto& values : cases) {
        PrefixSumArray prefix(values);

        cout << "Size=" << values.size()
             << ", total=" << prefix.totalSum()
             << ", zeroSumSubarrays="
             << countZeroSumSubarrays(values)
             << '\n';
    }
}


// -----------------------------------------------------------------------------
// 18. MAIN PROGRAM
// -----------------------------------------------------------------------------

int main() {
    try {
        cout << "Day 14 — Prefix Sums\n";
        cout << "===================\n";

        runRetailAnalyticsCaseStudy();

        cout << "\n=== Prefix-frequency example ===\n";

        vector<long long> sample = {
            2, -2, 3, -3, 3
        };

        for (const auto& [prefix, frequency]
             : prefixFrequency(sample)) {
            cout << "Prefix "
                 << prefix
                 << ": "
                 << frequency
                 << '\n';
        }

        cout << "\n=== Prefix XOR example ===\n";

        vector<long long> xorValues = {
            4, 2, 2, 6, 4
        };

        cout << "Subarrays with XOR 6: "
             << countSubarraysWithXorK(
                    xorValues,
                    6
                )
             << '\n';

        cout << "\n=== Two-dimensional prefix sum ===\n";

        vector<vector<long long>> matrix = {
            {3, 1, 2, 5},
            {4, 2, 0, 1},
            {7, 3, 6, 2}
        };

        MatrixPrefixSum matrixPrefix(matrix);

        cout << "Rectangle [0,1] to [2,3]: "
             << matrixPrefix.rectangleSum(
                    0, 1, 2, 3
                )
             << '\n';

        cout << "\n=== Difference-array range updates ===\n";

        vector<tuple<size_t, size_t, long long>> updates = {
            {1, 3, 5},
            {2, 5, 2},
            {0, 2, -1}
        };

        printVector(
            applyRangeUpdates(6, updates),
            "Updated values: "
        );

        cout << "\n=== Sliding-window comparison ===\n";

        vector<long long> positiveValues = {
            1, 2, 1, 1
        };

        cout << "Positive subarrays with sum <= 3: "
             << countPositiveSubarraysWithSumAtMostK(
                    positiveValues,
                    3
                )
             << '\n';

        testRangeSum();
        testSubarraySumK();

        demonstrateEdgeCases();

        cout << "\nProgram completed successfully.\n";
    }
    catch (const exception& error) {
        cerr << "Error: "
             << error.what()
             << '\n';

        return 1;
    }

    return 0;
}
