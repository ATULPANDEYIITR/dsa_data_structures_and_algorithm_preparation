/*
 * Day 16 — Sliding Window
 *
 * C++17 case study: real-time network traffic anomaly monitoring.
 *
 * The program progressively demonstrates:
 *   1. Fixed-size windows
 *   2. Variable-size windows
 *   3. Frequency-based windows
 *   4. Distinct-element constraints
 *   5. Monotonic deques
 *   6. A realistic traffic-monitoring system
 *   7. Validation and error handling
 *   8. Complexity and design trade-offs
 *
 * Compile:
 *   g++ -std=c++17 -O2 -Wall -Wextra -pedantic sliding_window.cpp -o sliding_window
 */

#include <algorithm>
#include <deque>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;


// -----------------------------------------------------------------------------
// General validation
// -----------------------------------------------------------------------------

void validateNonEmpty(const vector<int>& values,
                      const string& name = "values") {
    if (values.empty()) {
        throw invalid_argument(name + " must not be empty.");
    }
}

void validatePositiveK(int k) {
    if (k <= 0) {
        throw invalid_argument("k must be greater than zero.");
    }
}


// -----------------------------------------------------------------------------
// Fixed-size sliding window
// -----------------------------------------------------------------------------

long long maximumSumBruteForce(
    const vector<int>& values,
    int k
) {
    validateNonEmpty(values);
    validatePositiveK(k);

    if (k > static_cast<int>(values.size())) {
        throw invalid_argument(
            "k cannot exceed the array length."
        );
    }

    long long best = numeric_limits<long long>::lowest();

    for (int left = 0;
         left <= static_cast<int>(values.size()) - k;
         ++left) {

        long long currentSum = 0;

        for (int index = left;
             index < left + k;
             ++index) {

            currentSum += values[index];
        }

        best = max(best, currentSum);
    }

    return best;
}

long long maximumSumSlidingWindow(
    const vector<int>& values,
    int k
) {
    validateNonEmpty(values);
    validatePositiveK(k);

    if (k > static_cast<int>(values.size())) {
        throw invalid_argument(
            "k cannot exceed the array length."
        );
    }

    long long windowSum = 0;

    for (int index = 0; index < k; ++index) {
        windowSum += values[index];
    }

    long long best = windowSum;

    /*
     * Each iteration performs exactly two state updates:
     * remove the value leaving the window and add the value entering it.
     *
     * This changes the time complexity from O(n*k) to O(n).
     */
    for (int right = k;
         right < static_cast<int>(values.size());
         ++right) {

        windowSum += values[right];
        windowSum -= values[right - k];

        best = max(best, windowSum);
    }

    return best;
}


// -----------------------------------------------------------------------------
// Minimum-size variable window
// -----------------------------------------------------------------------------

int minimumSizeSubarraySum(
    const vector<int>& values,
    long long target
) {
    validateNonEmpty(values);

    if (target <= 0) {
        throw invalid_argument(
            "target must be positive."
        );
    }

    /*
     * The algorithm depends on non-negative values.
     *
     * When the right pointer expands, the sum cannot decrease.
     * When the left pointer contracts, the sum cannot increase.
     *
     * Negative values destroy this monotonic property.
     */
    for (int value : values) {
        if (value < 0) {
            throw invalid_argument(
                "This implementation requires non-negative values."
            );
        }
    }

    int left = 0;
    long long windowSum = 0;
    int best = numeric_limits<int>::max();

    for (int right = 0;
         right < static_cast<int>(values.size());
         ++right) {

        windowSum += values[right];

        while (windowSum >= target) {
            best = min(
                best,
                right - left + 1
            );

            windowSum -= values[left];
            ++left;
        }
    }

    return best == numeric_limits<int>::max()
        ? 0
        : best;
}


// -----------------------------------------------------------------------------
// Longest window with at most k distinct values
// -----------------------------------------------------------------------------

int longestAtMostKDistinct(
    const vector<int>& values,
    int k
) {
    validateNonEmpty(values);

    if (k <= 0) {
        return 0;
    }

    unordered_map<int, int> frequency;

    int left = 0;
    int best = 0;

    for (int right = 0;
         right < static_cast<int>(values.size());
         ++right) {

        ++frequency[values[right]];

        /*
         * The window is invalid when it contains more than k distinct
         * values. Contract until the invariant is restored.
         */
        while (static_cast<int>(frequency.size()) > k) {
            int outgoing = values[left];

            --frequency[outgoing];

            if (frequency[outgoing] == 0) {
                frequency.erase(outgoing);
            }

            ++left;
        }

        best = max(
            best,
            right - left + 1
        );
    }

    return best;
}


// -----------------------------------------------------------------------------
// Longest substring without repeating characters
// -----------------------------------------------------------------------------

int longestSubstringWithoutRepeating(
    const string& text
) {
    unordered_map<char, int> lastSeen;

    int left = 0;
    int best = 0;

    for (int right = 0;
         right < static_cast<int>(text.size());
         ++right) {

        char current = text[right];

        auto iterator = lastSeen.find(current);

        if (
            iterator != lastSeen.end() &&
            iterator->second >= left
        ) {
            /*
             * Jumping left is safe because the repeated character's old
             * position can no longer belong to a valid window.
             */
            left = iterator->second + 1;
        }

        lastSeen[current] = right;

        best = max(
            best,
            right - left + 1
        );
    }

    return best;
}


// -----------------------------------------------------------------------------
// Fixed-size distinct-count windows
// -----------------------------------------------------------------------------

vector<int> distinctCountEveryWindow(
    const vector<int>& values,
    int k
) {
    validateNonEmpty(values);
    validatePositiveK(k);

    if (k > static_cast<int>(values.size())) {
        throw invalid_argument(
            "k cannot exceed the array length."
        );
    }

    unordered_map<int, int> frequency;
    vector<int> result;

    for (int index = 0; index < k; ++index) {
        ++frequency[values[index]];
    }

    result.push_back(
        static_cast<int>(frequency.size())
    );

    for (int right = k;
         right < static_cast<int>(values.size());
         ++right) {

        int outgoing = values[right - k];

        --frequency[outgoing];

        if (frequency[outgoing] == 0) {
            frequency.erase(outgoing);
        }

        ++frequency[values[right]];

        result.push_back(
            static_cast<int>(frequency.size())
        );
    }

    return result;
}


// -----------------------------------------------------------------------------
// Binary window
// -----------------------------------------------------------------------------

int longestOnesAfterFlippingKZeros(
    const vector<int>& values,
    int k
) {
    validateNonEmpty(values);

    if (k < 0) {
        throw invalid_argument(
            "k cannot be negative."
        );
    }

    int left = 0;
    int zeroCount = 0;
    int best = 0;

    for (int right = 0;
         right < static_cast<int>(values.size());
         ++right) {

        if (values[right] != 0 &&
            values[right] != 1) {

            throw invalid_argument(
                "Binary window requires only 0 and 1."
            );
        }

        if (values[right] == 0) {
            ++zeroCount;
        }

        while (zeroCount > k) {
            if (values[left] == 0) {
                --zeroCount;
            }

            ++left;
        }

        best = max(
            best,
            right - left + 1
        );
    }

    return best;
}


// -----------------------------------------------------------------------------
// Monotonic deque
// -----------------------------------------------------------------------------

vector<int> slidingWindowMaximum(
    const vector<int>& values,
    int k
) {
    validateNonEmpty(values);
    validatePositiveK(k);

    if (k > static_cast<int>(values.size())) {
        throw invalid_argument(
            "k cannot exceed the array length."
        );
    }

    /*
     * The deque stores indices.
     *
     * The corresponding values are kept in decreasing order:
     *
     * values[dq[0]] >= values[dq[1]] >= ...
     *
     * Therefore dq.front() is always the maximum candidate.
     */
    deque<int> candidates;
    vector<int> result;

    for (int right = 0;
         right < static_cast<int>(values.size());
         ++right) {

        // Remove indices outside the active window.
        while (
            !candidates.empty() &&
            candidates.front() <= right - k
        ) {
            candidates.pop_front();
        }

        /*
         * If a new value is greater than an older candidate, that older
         * candidate can never become a maximum again while the new value
         * remains inside the window.
         */
        while (
            !candidates.empty() &&
            values[candidates.back()] <= values[right]
        ) {
            candidates.pop_back();
        }

        candidates.push_back(right);

        if (right >= k - 1) {
            result.push_back(
                values[candidates.front()]
            );
        }
    }

    return result;
}


// -----------------------------------------------------------------------------
// Longest window where max - min <= limit
// -----------------------------------------------------------------------------

int longestAbsoluteDifferenceWindow(
    const vector<int>& values,
    int limit
) {
    validateNonEmpty(values);

    if (limit < 0) {
        return 0;
    }

    /*
     * One deque maintains decreasing values for the maximum.
     * Another maintains increasing values for the minimum.
     */
    deque<int> maximums;
    deque<int> minimums;

    int left = 0;
    int best = 0;

    for (int right = 0;
         right < static_cast<int>(values.size());
         ++right) {

        while (
            !maximums.empty() &&
            values[maximums.back()] <= values[right]
        ) {
            maximums.pop_back();
        }

        maximums.push_back(right);

        while (
            !minimums.empty() &&
            values[minimums.back()] >= values[right]
        ) {
            minimums.pop_back();
        }

        minimums.push_back(right);

        while (
            values[maximums.front()] -
            values[minimums.front()] >
            limit
        ) {
            if (maximums.front() == left) {
                maximums.pop_front();
            }

            if (minimums.front() == left) {
                minimums.pop_front();
            }

            ++left;
        }

        best = max(
            best,
            right - left + 1
        );
    }

    return best;
}


// -----------------------------------------------------------------------------
// Traffic-monitoring domain model
// -----------------------------------------------------------------------------

struct TrafficAlert {
    int startIndex;
    int endIndex;
    long long totalPackets;
    double averagePackets;
};

class TrafficMonitor {
private:
    int windowSize;
    long long alertThreshold;

public:
    TrafficMonitor(
        int windowSize,
        long long alertThreshold
    )
        : windowSize(windowSize),
          alertThreshold(alertThreshold) {

        if (windowSize <= 0) {
            throw invalid_argument(
                "windowSize must be positive."
            );
        }

        if (alertThreshold < 0) {
            throw invalid_argument(
                "alertThreshold cannot be negative."
            );
        }
    }

    vector<TrafficAlert> analyze(
        const vector<int>& packetCounts
    ) const {

        validateNonEmpty(packetCounts);

        if (
            windowSize >
            static_cast<int>(packetCounts.size())
        ) {
            throw invalid_argument(
                "windowSize exceeds packet stream length."
            );
        }

        vector<TrafficAlert> alerts;

        long long windowSum = 0;

        for (int index = 0;
             index < windowSize;
             ++index) {

            if (packetCounts[index] < 0) {
                throw invalid_argument(
                    "Packet counts cannot be negative."
                );
            }

            windowSum += packetCounts[index];
        }

        for (
            int right = windowSize - 1;
            right < static_cast<int>(packetCounts.size());
            ++right
        ) {
            if (right >= windowSize) {
                if (packetCounts[right] < 0) {
                    throw invalid_argument(
                        "Packet counts cannot be negative."
                    );
                }

                windowSum += packetCounts[right];
                windowSum -= packetCounts[right - windowSize];
            }

            int left = right - windowSize + 1;

            if (windowSum >= alertThreshold) {
                alerts.push_back({
                    left,
                    right,
                    windowSum,
                    static_cast<double>(windowSum) /
                        windowSize
                });
            }
        }

        return alerts;
    }
};


// -----------------------------------------------------------------------------
// Output helpers
// -----------------------------------------------------------------------------

void printVector(const vector<int>& values) {
    cout << "[";

    for (size_t index = 0;
         index < values.size();
         ++index) {

        cout << values[index];

        if (index + 1 < values.size()) {
            cout << ", ";
        }
    }

    cout << "]";
}

void printSection(const string& title) {
    cout << "\n"
         << string(78, '=')
         << "\n"
         << title
         << "\n"
         << string(78, '=')
         << "\n";
}


// -----------------------------------------------------------------------------
// Case-study report
// -----------------------------------------------------------------------------

void printTrafficAlerts(
    const vector<TrafficAlert>& alerts
) {
    cout << left
         << setw(12) << "Start"
         << setw(12) << "End"
         << setw(18) << "Total"
         << setw(18) << "Average"
         << "\n";

    cout << string(60, '-')
         << "\n";

    cout << fixed << setprecision(2);

    for (const auto& alert : alerts) {
        cout << left
             << setw(12) << alert.startIndex
             << setw(12) << alert.endIndex
             << setw(18) << alert.totalPackets
             << setw(18) << alert.averagePackets
             << "\n";
    }
}


// -----------------------------------------------------------------------------
// Deterministic tests
// -----------------------------------------------------------------------------

void runTests() {
    printSection("Correctness tests");

    if (
        maximumSumSlidingWindow(
            {2, 1, 5, 1, 3, 2},
            3
        ) != 9
    ) {
        throw runtime_error(
            "Maximum-sum test failed."
        );
    }

    if (
        maximumSumSlidingWindow(
            {-5, -2, -8},
            2
        ) != -7
    ) {
        throw runtime_error(
            "Negative-value test failed."
        );
    }

    if (
        minimumSizeSubarraySum(
            {2, 3, 1, 2, 4, 3},
            7
        ) != 2
    ) {
        throw runtime_error(
            "Minimum-size test failed."
        );
    }

    if (
        longestAtMostKDistinct(
            {1, 2, 1, 2, 3},
            2
        ) != 4
    ) {
        throw runtime_error(
            "Distinct-element test failed."
        );
    }

    if (
        longestSubstringWithoutRepeating(
            "abcabcbb"
        ) != 3
    ) {
        throw runtime_error(
            "String-window test failed."
        );
    }

    vector<int> expectedMaximum{
        3, 3, 5, 5, 6, 7
    };

    if (
        slidingWindowMaximum(
            {1, 3, -1, -3, 5, 3, 6, 7},
            3
        ) != expectedMaximum
    ) {
        throw runtime_error(
            "Monotonic-deque maximum test failed."
        );
    }

    if (
        longestOnesAfterFlippingKZeros(
            {1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0},
            2
        ) != 6
    ) {
        throw runtime_error(
            "Binary-window test failed."
        );
    }

    if (
        longestAbsoluteDifferenceWindow(
            {8, 2, 4, 7},
            4
        ) != 2
    ) {
        throw runtime_error(
            "Maximum-minimum constraint test failed."
        );
    }

    cout << "All deterministic tests passed.\n";
}


// -----------------------------------------------------------------------------
// Main
// -----------------------------------------------------------------------------

int main() {
    try {
        printSection("Day 16 — Sliding Window");

        // ---------------------------------------------------------------------
        // Part 1: fixed-size window
        // ---------------------------------------------------------------------

        printSection("1. Fixed-size maximum sum");

        vector<int> values{
            2, 1, 5, 1, 3, 2
        };

        int k = 3;

        cout << "Input: ";
        printVector(values);
        cout << "\n";

        cout << "Brute-force result: "
             << maximumSumBruteForce(values, k)
             << "\n";

        cout << "Sliding-window result: "
             << maximumSumSlidingWindow(values, k)
             << "\n";

        cout << "The optimized algorithm updates one outgoing and "
                "one incoming value per window movement.\n";


        // ---------------------------------------------------------------------
        // Part 2: minimum-size variable window
        // ---------------------------------------------------------------------

        printSection("2. Minimum-size variable window");

        vector<int> positiveValues{
            2, 3, 1, 2, 4, 3
        };

        cout << "Input: ";
        printVector(positiveValues);
        cout << "\n";

        cout << "Minimum length with sum >= 7: "
             << minimumSizeSubarraySum(
                    positiveValues,
                    7
                )
             << "\n";


        // ---------------------------------------------------------------------
        // Part 3: frequency and distinct elements
        // ---------------------------------------------------------------------

        printSection("3. Frequency-based and distinct windows");

        vector<int> distinctValues{
            1, 2, 1, 2, 3, 2, 2
        };

        cout << "Longest subarray with at most 2 distinct values: "
             << longestAtMostKDistinct(
                    distinctValues,
                    2
                )
             << "\n";

        cout << "Distinct counts for windows of size 3: ";

        printVector(
            distinctCountEveryWindow(
                distinctValues,
                3
            )
        );

        cout << "\n";


        // ---------------------------------------------------------------------
        // Part 4: string window
        // ---------------------------------------------------------------------

        printSection("4. String sliding window");

        string text = "abcabcbb";

        cout << "Text: " << text << "\n";

        cout << "Longest substring without repetition: "
             << longestSubstringWithoutRepeating(text)
             << "\n";


        // ---------------------------------------------------------------------
        // Part 5: binary window
        // ---------------------------------------------------------------------

        printSection("5. Binary resource-constrained window");

        vector<int> binaryValues{
            1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0
        };

        cout << "Longest sequence after at most 2 zero flips: "
             << longestOnesAfterFlippingKZeros(
                    binaryValues,
                    2
                )
             << "\n";


        // ---------------------------------------------------------------------
        // Part 6: monotonic deque
        // ---------------------------------------------------------------------

        printSection("6. Monotonic deque");

        vector<int> dequeValues{
            1, 3, -1, -3, 5, 3, 6, 7
        };

        cout << "Window maximums: ";

        printVector(
            slidingWindowMaximum(
                dequeValues,
                3
            )
        );

        cout << "\n";


        // ---------------------------------------------------------------------
        // Part 7: constrained max-min window
        // ---------------------------------------------------------------------

        printSection("7. Maximum-minimum constrained window");

        vector<int> constrained{
            8, 2, 4, 7
        };

        cout << "Longest window where max - min <= 4: "
             << longestAbsoluteDifferenceWindow(
                    constrained,
                    4
                )
             << "\n";


        // ---------------------------------------------------------------------
        // Part 8: industry-style case study
        // ---------------------------------------------------------------------

        printSection(
            "8. Industry-style case study: network traffic monitoring"
        );

        /*
         * Each number represents packets observed during one sampling
         * interval. A rolling window detects sustained high traffic.
         *
         * A fixed-size window is appropriate because the monitoring policy
         * is defined over a fixed time interval.
         */
        vector<int> packetCounts{
            120, 130, 145, 300, 280, 290, 150, 140, 135
        };

        TrafficMonitor monitor(
            3,
            750
        );

        vector<TrafficAlert> alerts =
            monitor.analyze(packetCounts);

        cout << "Traffic samples: ";
        printVector(packetCounts);
        cout << "\n\n";

        cout << "Alert threshold: 750 packets per 3-sample window\n\n";

        printTrafficAlerts(alerts);


        // ---------------------------------------------------------------------
        // Part 9: error handling
        // ---------------------------------------------------------------------

        printSection("9. Failure conditions");

        try {
            maximumSumSlidingWindow(
                {1, 2, 3},
                4
            );
        }
        catch (const exception& error) {
            cout << "Handled invalid window size: "
                 << error.what()
                 << "\n";
        }

        try {
            minimumSizeSubarraySum(
                {2, -1, 4},
                5
            );
        }
        catch (const exception& error) {
            cout << "Handled unsupported negative-value case: "
                 << error.what()
                 << "\n";
        }

        try {
            longestOnesAfterFlippingKZeros(
                {1, 0, 2},
                1
            );
        }
        catch (const exception& error) {
            cout << "Handled invalid binary input: "
                 << error.what()
                 << "\n";
        }


        // ---------------------------------------------------------------------
        // Part 10: correctness verification
        // ---------------------------------------------------------------------

        runTests();


        // ---------------------------------------------------------------------
        // Complexity
        // ---------------------------------------------------------------------

        printSection("10. Complexity analysis");

        cout << left
             << setw(38) << "Technique"
             << setw(18) << "Time"
             << setw(18) << "Space"
             << "\n";

        cout << string(74, '-')
             << "\n";

        cout << setw(38)
             << "Fixed-size sum"
             << setw(18)
             << "O(n)"
             << setw(18)
             << "O(1)"
             << "\n";

        cout << setw(38)
             << "Minimum-size sum"
             << setw(18)
             << "O(n)"
             << setw(18)
             << "O(1)"
             << "\n";

        cout << setw(38)
             << "Frequency window"
             << setw(18)
             << "O(n) average"
             << setw(18)
             << "O(k)"
             << "\n";

        cout << setw(38)
             << "Monotonic deque"
             << setw(18)
             << "O(n)"
             << setw(18)
             << "O(k)"
             << "\n";

        cout << setw(38)
             << "Brute-force fixed window"
             << setw(18)
             << "O(n*k)"
             << setw(18)
             << "O(1)"
             << "\n";


        // ---------------------------------------------------------------------
        // Study checkpoints
        // ---------------------------------------------------------------------

        printSection("11. Study checkpoints");

        const vector<string> checkpoints{
            "Define the window before writing the loop.",
            "Decide what makes the window valid.",
            "Expand with the right pointer.",
            "Contract with the left pointer when required.",
            "Maintain state incrementally instead of recomputing it.",
            "Delete frequency-map keys when their counts reach zero.",
            "Use monotonic deques for O(n) sliding extrema.",
            "Check whether negative values invalidate sum-based assumptions.",
            "Ensure each pointer moves only forward for amortized O(n).",
            "Test boundary cases such as k=1 and k=n."
        };

        for (size_t index = 0;
             index < checkpoints.size();
             ++index) {

            cout << setw(3)
                 << index + 1
                 << ". "
                 << checkpoints[index]
                 << "\n";
        }

        cout << "\nSliding-window case study completed successfully.\n";

    }
    catch (const exception& error) {
        cerr << "Fatal error: "
             << error.what()
             << "\n";

        return 1;
    }

    return 0;
}
