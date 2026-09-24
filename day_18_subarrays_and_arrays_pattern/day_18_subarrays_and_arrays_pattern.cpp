/*
 * Day 18 — Subarrays and Array Patterns
 *
 * C++17 industry-style case study:
 * A transaction analytics engine that analyzes contiguous periods
 * of account activity.
 *
 * Demonstrates:
 * - Subarray enumeration
 * - Prefix sums
 * - Hashing
 * - Two pointers
 * - Sliding windows
 * - Sorting-based techniques
 * - Kadane's algorithm
 * - Minimum and maximum subarrays
 * - Circular maximum subarray
 * - Validation
 * - Complexity and architectural trade-offs
 */

#include <algorithm>
#include <cassert>
#include <chrono>
#include <cstddef>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

// ============================================================
// DOMAIN MODEL
// ============================================================

struct SubarrayResult {
    size_t start{};
    size_t end{};
    long long value{};

    size_t length() const {
        return end - start + 1;
    }
};

struct Transaction {
    string id;
    long long amount{};
};

// ============================================================
// VALIDATION
// ============================================================

void validateNonNegative(const vector<long long>& values,
                         const string& description) {
    for (long long value : values) {
        if (value < 0) {
            throw invalid_argument(description + " must be non-negative.");
        }
    }
}

// ============================================================
// BASIC SUBARRAY ENUMERATION
// ============================================================

long long countSubarrays(size_t n) {
    return static_cast<long long>(n) *
           static_cast<long long>(n + 1) / 2;
}

vector<SubarrayResult> enumerateSubarraySums(
    const vector<long long>& values) {

    vector<SubarrayResult> result;

    for (size_t start = 0; start < values.size(); ++start) {
        long long currentSum = 0;

        for (size_t end = start; end < values.size(); ++end) {
            currentSum += values[end];

            result.push_back({
                start,
                end,
                currentSum
            });
        }
    }

    return result;
}

// ============================================================
// PREFIX SUM DATA STRUCTURE
// ============================================================

class PrefixSumIndex {
private:
    vector<long long> prefix;

public:
    explicit PrefixSumIndex(const vector<long long>& values) {
        prefix.resize(values.size() + 1, 0);

        for (size_t i = 0; i < values.size(); ++i) {
            prefix[i + 1] = prefix[i] + values[i];
        }
    }

    long long rangeSum(size_t left, size_t right) const {
        if (left > right || right + 1 >= prefix.size()) {
            throw out_of_range("Invalid inclusive range.");
        }

        return prefix[right + 1] - prefix[left];
    }

    const vector<long long>& values() const {
        return prefix;
    }
};

// ============================================================
// HASHING WITH PREFIX SUMS
// ============================================================

long long countSubarraysWithSum(
    const vector<long long>& values,
    long long target) {

    /*
     * Let P(j) be the prefix sum through j.
     *
     * A subarray has target sum when:
     *
     *     P(j) - P(i) = target
     *
     * Therefore:
     *
     *     P(i) = P(j) - target
     *
     * The hash table counts how often the required previous
     * prefix sum has appeared.
     *
     * Average complexity: O(n)
     * Space: O(n)
     */
    unordered_map<long long, long long> frequency;
    frequency.reserve(values.size() * 2 + 1);

    frequency[0] = 1;

    long long prefix = 0;
    long long count = 0;

    for (long long value : values) {
        prefix += value;

        auto iterator = frequency.find(prefix - target);

        if (iterator != frequency.end()) {
            count += iterator->second;
        }

        ++frequency[prefix];
    }

    return count;
}

optional<SubarrayResult> longestSubarrayWithSum(
    const vector<long long>& values,
    long long target) {

    unordered_map<long long, long long> earliest;
    earliest.reserve(values.size() * 2 + 1);

    // Prefix sum zero occurs before index zero.
    earliest[0] = -1;

    long long prefix = 0;
    optional<SubarrayResult> best;

    for (long long index = 0;
         index < static_cast<long long>(values.size());
         ++index) {

        prefix += values[index];

        auto iterator = earliest.find(prefix - target);

        if (iterator != earliest.end()) {
            long long start = iterator->second + 1;
            long long length = index - iterator->second;

            if (!best.has_value() ||
                length > static_cast<long long>(best->length())) {

                best = SubarrayResult{
                    static_cast<size_t>(start),
                    static_cast<size_t>(index),
                    target
                };
            }
        }

        // Earliest index is retained intentionally.
        // It produces the longest future subarray.
        if (earliest.find(prefix) == earliest.end()) {
            earliest[prefix] = index;
        }
    }

    return best;
}

// ============================================================
// TWO POINTERS
// ============================================================

optional<pair<long long, long long>> twoPointerPairSumSorted(
    const vector<long long>& values,
    long long target) {

    if (!is_sorted(values.begin(), values.end())) {
        throw invalid_argument(
            "Two-pointer sorted search requires sorted input.");
    }

    if (values.size() < 2) {
        return nullopt;
    }

    size_t left = 0;
    size_t right = values.size() - 1;

    while (left < right) {
        long long sum = values[left] + values[right];

        if (sum == target) {
            return make_pair(values[left], values[right]);
        }

        if (sum < target) {
            ++left;
        } else {
            --right;
        }
    }

    return nullopt;
}

optional<pair<long long, long long>> sortedPairSum(
    vector<long long> values,
    long long target) {

    sort(values.begin(), values.end());

    return twoPointerPairSumSorted(values, target);
}

// ============================================================
// SLIDING WINDOW
// ============================================================

long long maximumFixedWindowSum(
    const vector<long long>& values,
    size_t windowSize) {

    if (windowSize == 0) {
        throw invalid_argument("Window size must be positive.");
    }

    if (windowSize > values.size()) {
        throw invalid_argument(
            "Window size cannot exceed array size.");
    }

    long long currentSum =
        accumulate(
            values.begin(),
            values.begin() + static_cast<ptrdiff_t>(windowSize),
            0LL
        );

    long long best = currentSum;

    for (size_t right = windowSize;
         right < values.size();
         ++right) {

        currentSum += values[right];
        currentSum -= values[right - windowSize];

        best = max(best, currentSum);
    }

    return best;
}

size_t minimumPositiveWindow(
    const vector<long long>& values,
    long long target) {

    if (target <= 0) {
        throw invalid_argument("Target must be positive.");
    }

    validateNonNegative(
        values,
        "Values"
    );

    for (long long value : values) {
        if (value == 0) {
            throw invalid_argument(
                "This implementation requires strictly positive values.");
        }
    }

    size_t left = 0;
    long long currentSum = 0;

    size_t best = numeric_limits<size_t>::max();

    for (size_t right = 0; right < values.size(); ++right) {
        currentSum += values[right];

        while (currentSum >= target && left <= right) {
            best = min(best, right - left + 1);
            currentSum -= values[left];
            ++left;
        }
    }

    return best == numeric_limits<size_t>::max() ? 0 : best;
}

// ============================================================
// KADANE'S ALGORITHM
// ============================================================

optional<SubarrayResult> maximumSubarray(
    const vector<long long>& values) {

    if (values.empty()) {
        return nullopt;
    }

    long long currentSum = values[0];
    long long bestSum = values[0];

    size_t currentStart = 0;
    size_t bestStart = 0;
    size_t bestEnd = 0;

    for (size_t i = 1; i < values.size(); ++i) {
        long long value = values[i];

        if (currentSum + value < value) {
            currentSum = value;
            currentStart = i;
        } else {
            currentSum += value;
        }

        if (currentSum > bestSum) {
            bestSum = currentSum;
            bestStart = currentStart;
            bestEnd = i;
        }
    }

    return SubarrayResult{
        bestStart,
        bestEnd,
        bestSum
    };
}

optional<SubarrayResult> minimumSubarray(
    const vector<long long>& values) {

    if (values.empty()) {
        return nullopt;
    }

    long long currentSum = values[0];
    long long bestSum = values[0];

    size_t currentStart = 0;
    size_t bestStart = 0;
    size_t bestEnd = 0;

    for (size_t i = 1; i < values.size(); ++i) {
        long long value = values[i];

        if (currentSum + value > value) {
            currentSum = value;
            currentStart = i;
        } else {
            currentSum += value;
        }

        if (currentSum < bestSum) {
            bestSum = currentSum;
            bestStart = currentStart;
            bestEnd = i;
        }
    }

    return SubarrayResult{
        bestStart,
        bestEnd,
        bestSum
    };
}

// ============================================================
// CIRCULAR MAXIMUM SUBARRAY
// ============================================================

optional<long long> maximumCircularSubarray(
    const vector<long long>& values) {

    if (values.empty()) {
        return nullopt;
    }

    auto normal = maximumSubarray(values);
    auto minimum = minimumSubarray(values);

    if (!normal || !minimum) {
        return nullopt;
    }

    // If all values are negative, total - minimum would
    // incorrectly represent an empty subarray.
    if (normal->value < 0) {
        return normal->value;
    }

    long long total =
        accumulate(values.begin(), values.end(), 0LL);

    long long wrapped = total - minimum->value;

    return max(normal->value, wrapped);
}

// ============================================================
// SORTING-BASED INTERVAL PROCESSING
// ============================================================

vector<pair<long long, long long>> mergeIntervals(
    vector<pair<long long, long long>> intervals) {

    for (const auto& interval : intervals) {
        if (interval.first > interval.second) {
            throw invalid_argument(
                "Interval start cannot exceed interval end.");
        }
    }

    if (intervals.empty()) {
        return {};
    }

    sort(intervals.begin(), intervals.end());

    vector<pair<long long, long long>> merged;
    merged.push_back(intervals[0]);

    for (size_t i = 1; i < intervals.size(); ++i) {
        auto& previous = merged.back();
        const auto& current = intervals[i];

        if (current.first <= previous.second) {
            previous.second =
                max(previous.second, current.second);
        } else {
            merged.push_back(current);
        }
    }

    return merged;
}

// ============================================================
// DOMAIN SERVICE
// ============================================================

class TransactionAnalytics {
private:
    vector<Transaction> transactions;

public:
    explicit TransactionAnalytics(vector<Transaction> input)
        : transactions(move(input)) {}

    vector<long long> amounts() const {
        vector<long long> result;
        result.reserve(transactions.size());

        for (const auto& transaction : transactions) {
            result.push_back(transaction.amount);
        }

        return result;
    }

    optional<SubarrayResult> bestGrowthPeriod() const {
        return maximumSubarray(amounts());
    }

    optional<SubarrayResult> worstDeclinePeriod() const {
        return minimumSubarray(amounts());
    }

    long long numberOfPeriodsWithNetChange(
        long long target) const {

        return countSubarraysWithSum(
            amounts(),
            target
        );
    }

    long long bestFixedPeriod(
        size_t numberOfDays) const {

        return maximumFixedWindowSum(
            amounts(),
            numberOfDays
        );
    }
};

// ============================================================
// OUTPUT HELPERS
// ============================================================

void printResult(
    const string& label,
    const optional<SubarrayResult>& result,
    const vector<long long>& values) {

    cout << label << ": ";

    if (!result) {
        cout << "none\n";
        return;
    }

    cout << "sum=" << result->value
         << ", range=[" << result->start
         << ", " << result->end << "]"
         << ", values=[";

    for (size_t i = result->start;
         i <= result->end;
         ++i) {

        if (i > result->start) {
            cout << ", ";
        }

        cout << values[i];
    }

    cout << "]\n";
}

// ============================================================
// TESTS
// ============================================================

void runTests() {
    assert(countSubarrays(4) == 10);

    vector<long long> values{
        -2, 1, -3, 4, -1, 2, 1, -5, 4
    };

    auto maximum = maximumSubarray(values);
    assert(maximum.has_value());
    assert(maximum->value == 6);
    assert(maximum->start == 3);
    assert(maximum->end == 6);

    auto minimum = minimumSubarray(values);
    assert(minimum.has_value());
    assert(minimum->value == -5);

    assert(
        countSubarraysWithSum(
            {1, 2, 3, -2, 2, 1},
            3
        ) == 4
    );

    auto pair = sortedPairSum({8, 1, 6, 10, 4}, 14);
    assert(pair.has_value());
    assert(pair->first + pair->second == 14);

    assert(
        maximumFixedWindowSum(
            {2, 1, 5, 1, 3, 2},
            3
        ) == 9
    );

    assert(
        minimumPositiveWindow(
            {2, 3, 1, 2, 4, 3},
            7
        ) == 2
    );

    assert(
        maximumCircularSubarray(
            {5, -3, 5}
        ).value() == 10
    );

    auto merged = mergeIntervals({
        {1, 3},
        {2, 6},
        {8, 10},
        {9, 12}
    });

    assert(
        merged == vector<pair<long long, long long>>{
            {1, 6},
            {8, 12}
        }
    );

    cout << "All C++ tests passed.\n";
}

// ============================================================
// PERFORMANCE MEASUREMENT
// ============================================================

void performanceDemo() {
    vector<long long> values;
    values.reserve(100000);

    for (int i = 0; i < 100000; ++i) {
        values.push_back((i * 17LL) % 101 - 50);
    }

    auto start = chrono::high_resolution_clock::now();

    auto result = maximumSubarray(values);

    auto end = chrono::high_resolution_clock::now();

    chrono::duration<double, milli> elapsed = end - start;

    cout << "\nPerformance demonstration:\n";
    cout << "Elements: " << values.size() << "\n";
    cout << "Kadane result: "
         << (result ? result->value : 0)
         << "\n";
    cout << fixed << setprecision(3)
         << "Execution time: "
         << elapsed.count()
         << " ms\n";
}

// ============================================================
// MAIN CASE STUDY
// ============================================================

int main() {
    try {
        cout << string(72, '=') << '\n';
        cout << "DAY 18 — SUBARRAYS AND ARRAY PATTERNS\n";
        cout << string(72, '=') << "\n\n";

        // ----------------------------------------------------
        // Basic subarray enumeration
        // ----------------------------------------------------

        vector<long long> smallValues{2, -1, 3};

        cout << "=== BASIC SUBARRAY ENUMERATION ===\n";
        cout << "Array: [2, -1, 3]\n";
        cout << "Number of non-empty subarrays: "
             << countSubarrays(smallValues.size())
             << "\n";

        auto subarrays =
            enumerateSubarraySums(smallValues);

        for (const auto& subarray : subarrays) {
            cout << "[" << subarray.start
                 << ", " << subarray.end
                 << "] -> "
                 << subarray.value
                 << "\n";
        }

        // ----------------------------------------------------
        // Prefix sums
        // ----------------------------------------------------

        cout << "\n=== PREFIX SUM INDEX ===\n";

        vector<long long> values{
            3, -2, 5, 7, -4, 6
        };

        PrefixSumIndex prefix(values);

        cout << "Sum of range [1, 4]: "
             << prefix.rangeSum(1, 4)
             << "\n";

        // ----------------------------------------------------
        // Hashing + prefix sums
        // ----------------------------------------------------

        cout << "\n=== HASHING + PREFIX SUMS ===\n";

        vector<long long> targetValues{
            1, 2, 3, -2, 2, 1
        };

        cout << "Subarrays with sum 3: "
             << countSubarraysWithSum(
                    targetValues,
                    3
                )
             << "\n";

        auto longest =
            longestSubarrayWithSum(
                {10, 5, 2, 7, 1, 9},
                15
            );

        printResult(
            "Longest subarray with sum 15",
            longest,
            {10, 5, 2, 7, 1, 9}
        );

        // ----------------------------------------------------
        // Two pointers
        // ----------------------------------------------------

        cout << "\n=== TWO POINTERS ===\n";

        auto pair =
            sortedPairSum(
                {8, 1, 6, 10, 4},
                14
            );

        if (pair) {
            cout << "Pair summing to 14: "
                 << pair->first
                 << " + "
                 << pair->second
                 << "\n";
        } else {
            cout << "No pair found.\n";
        }

        // ----------------------------------------------------
        // Sliding windows
        // ----------------------------------------------------

        cout << "\n=== SLIDING WINDOWS ===\n";

        cout << "Maximum sum of 3-day window: "
             << maximumFixedWindowSum(
                    {2, 1, 5, 1, 3, 2},
                    3
                )
             << "\n";

        cout << "Minimum positive window with sum >= 7: "
             << minimumPositiveWindow(
                    {2, 3, 1, 2, 4, 3},
                    7
                )
             << "\n";

        // ----------------------------------------------------
        // Maximum and minimum subarray
        // ----------------------------------------------------

        cout << "\n=== KADANE'S ALGORITHM ===\n";

        vector<long long> dailyChanges{
            -2, 1, -3, 4, -1, 2, 1, -5, 4
        };

        auto best = maximumSubarray(dailyChanges);
        auto worst = minimumSubarray(dailyChanges);

        printResult(
            "Maximum contiguous period",
            best,
            dailyChanges
        );

        printResult(
            "Minimum contiguous period",
            worst,
            dailyChanges
        );

        // ----------------------------------------------------
        // Circular array
        // ----------------------------------------------------

        cout << "\n=== CIRCULAR MAXIMUM SUBARRAY ===\n";

        auto circular =
            maximumCircularSubarray(
                {5, -3, 5}
            );

        cout << "Circular maximum: "
             << circular.value()
             << "\n";

        // ----------------------------------------------------
        // Sorting-based technique
        // ----------------------------------------------------

        cout << "\n=== SORTING-BASED INTERVAL PROCESSING ===\n";

        auto merged =
            mergeIntervals({
                {1, 3},
                {2, 6},
                {8, 10},
                {9, 12}
            });

        cout << "Merged intervals: ";

        for (const auto& interval : merged) {
            cout << "["
                 << interval.first
                 << ", "
                 << interval.second
                 << "] ";
        }

        cout << "\n";

        // ----------------------------------------------------
        // Industry-style transaction analytics
        // ----------------------------------------------------

        cout << "\n=== TRANSACTION ANALYTICS CASE STUDY ===\n";

        vector<Transaction> transactions{
            {"TX001", 120},
            {"TX002", -40},
            {"TX003", 80},
            {"TX004", -150},
            {"TX005", 210},
            {"TX006", 90},
            {"TX007", -20},
            {"TX008", 60},
            {"TX009", -300},
            {"TX010", 140}
        };

        TransactionAnalytics analytics(
            transactions
        );

        const auto amounts =
            analytics.amounts();

        printResult(
            "Best growth period",
            analytics.bestGrowthPeriod(),
            amounts
        );

        printResult(
            "Worst decline period",
            analytics.worstDeclinePeriod(),
            amounts
        );

        cout << "Periods with net change 0: "
             << analytics.numberOfPeriodsWithNetChange(0)
             << "\n";

        cout << "Best 3-day period: "
             << analytics.bestFixedPeriod(3)
             << "\n";

        // ----------------------------------------------------
        // Edge cases
        // ----------------------------------------------------

        cout << "\n=== EDGE CASES ===\n";

        vector<vector<long long>> edgeCases{
            {},
            {42},
            {-5, -2, -9},
            {0, 0, 0},
            {5, 5, 5}
        };

        for (const auto& edgeCase : edgeCases) {
            auto result =
                maximumSubarray(edgeCase);

            cout << "Input size: "
                 << edgeCase.size()
                 << " -> ";

            if (result) {
                cout << "maximum = "
                     << result->value;
            } else {
                cout << "empty input";
            }

            cout << "\n";
        }

        // ----------------------------------------------------
        // Validation failure
        // ----------------------------------------------------

        cout << "\n=== VALIDATION ===\n";

        try {
            minimumPositiveWindow(
                {2, -1, 3},
                3
            );
        } catch (const invalid_argument& error) {
            cout << "Rejected invalid sliding-window input: "
                 << error.what()
                 << "\n";
        }

        // ----------------------------------------------------
        // Tests and performance
        // ----------------------------------------------------

        cout << "\n=== TEST SUITE ===\n";
        runTests();

        performanceDemo();

        cout << "\n" << string(72, '=') << '\n';
        cout << "END OF DAY 18 PRACTICE\n";
        cout << string(72, '=') << '\n';

    } catch (const exception& error) {
        cerr << "Fatal error: "
             << error.what()
             << '\n';

        return 1;
    }

    return 0;
}
