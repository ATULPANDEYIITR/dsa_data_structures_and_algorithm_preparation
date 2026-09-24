/*
 * Day 19 — Array Assessment
 * ==========================
 *
 * Industry-style C++ case study:
 * An Array Assessment Engine evaluates a collection of array problems,
 * executes reference implementations, validates results, records algorithmic
 * metadata, and reports complexity and common mistakes.
 *
 * Problems:
 *
 * Easy:
 *   1. Find Pivot Index
 *   2. Move Zeroes
 *   3. Maximum Subarray
 *
 * Medium:
 *   4. Maximum Sum Subarray of Size K
 *   5. Two Sum II — Input Array Is Sorted
 *   6. Subarray Sum Equals K
 *   7. Product of Array Except Self
 *
 * Difficult:
 *   8. Trapping Rain Water
 *
 * Standard:
 *   C++17 or later
 *
 * External dependencies:
 *   None.
 */

#include <algorithm>
#include <chrono>
#include <exception>
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


// ============================================================================
// Common types
// ============================================================================

struct SubarrayResult {
    long long sum;
    int start;
    int end;

    bool operator==(const SubarrayResult& other) const {
        return sum == other.sum &&
               start == other.start &&
               end == other.end;
    }
};

struct ProblemMetadata {
    string name;
    string difficulty;
    string pattern;
    string approach;
    string timeComplexity;
    string spaceComplexity;
    string mistake;
    string improvement;
};

struct AssessmentResult {
    string problemName;
    bool passed;
    string details;
};


// ============================================================================
// Utility functions
// ============================================================================

void printSection(const string& title) {
    cout << "\n" << string(78, '=') << "\n";
    cout << title << "\n";
    cout << string(78, '=') << "\n";
}

void printSubsection(const string& title) {
    cout << "\n" << string(78, '-') << "\n";
    cout << title << "\n";
    cout << string(78, '-') << "\n";
}

string formatVector(const vector<int>& values) {
    string result = "[";

    for (size_t index = 0; index < values.size(); ++index) {
        result += to_string(values[index]);

        if (index + 1 < values.size()) {
            result += ", ";
        }
    }

    result += "]";
    return result;
}

void requireValidK(const vector<int>& numbers, int k) {
    if (k <= 0 || k > static_cast<int>(numbers.size())) {
        throw invalid_argument(
            "k must satisfy 1 <= k <= array size."
        );
    }
}


// ============================================================================
// EASY 1 — Find Pivot Index
// ============================================================================

int findPivotIndex(const vector<int>& numbers) {
    /*
     * The total sum allows the right side to be derived:
     *
     * right = total - left - current
     *
     * This changes the repeated-summing brute force approach from O(n²)
     * to O(n).
     */
    long long totalSum =
        accumulate(numbers.begin(), numbers.end(), 0LL);

    long long leftSum = 0;

    for (int index = 0; index < static_cast<int>(numbers.size()); ++index) {
        long long rightSum =
            totalSum - leftSum - numbers[index];

        if (leftSum == rightSum) {
            return index;
        }

        leftSum += numbers[index];
    }

    return -1;
}


// ============================================================================
// EASY 2 — Move Zeroes
// ============================================================================

void moveZeroes(vector<int>& numbers) {
    /*
     * writeIndex identifies the next position that should contain a
     * non-zero value.
     *
     * The read index scans every element exactly once.
     */
    size_t writeIndex = 0;

    for (size_t readIndex = 0;
         readIndex < numbers.size();
         ++readIndex) {

        if (numbers[readIndex] != 0) {
            swap(numbers[writeIndex], numbers[readIndex]);
            ++writeIndex;
        }
    }
}


// ============================================================================
// EASY 3 — Maximum Subarray
// ============================================================================

SubarrayResult maximumSubarray(const vector<int>& numbers) {
    if (numbers.empty()) {
        throw invalid_argument(
            "maximumSubarray requires a non-empty array."
        );
    }

    long long currentSum = numbers[0];
    long long bestSum = numbers[0];

    int currentStart = 0;
    int bestStart = 0;
    int bestEnd = 0;

    for (int index = 1;
         index < static_cast<int>(numbers.size());
         ++index) {

        const long long value = numbers[index];

        if (value > currentSum + value) {
            currentSum = value;
            currentStart = index;
        } else {
            currentSum += value;
        }

        if (currentSum > bestSum) {
            bestSum = currentSum;
            bestStart = currentStart;
            bestEnd = index;
        }
    }

    return {bestSum, bestStart, bestEnd};
}


// ============================================================================
// MEDIUM 1 — Maximum Sum Subarray of Size K
// ============================================================================

long long maximumSumSubarrayOfSizeK(
    const vector<int>& numbers,
    int k
) {
    requireValidK(numbers, k);

    long long windowSum = 0;

    for (int index = 0; index < k; ++index) {
        windowSum += numbers[index];
    }

    long long maximumSum = windowSum;

    for (int right = k;
         right < static_cast<int>(numbers.size());
         ++right) {

        int left = right - k;

        windowSum += numbers[right];
        windowSum -= numbers[left];

        maximumSum = max(maximumSum, windowSum);
    }

    return maximumSum;
}


// ============================================================================
// MEDIUM 2 — Two Sum II
// ============================================================================

pair<int, int> twoSumSorted(
    const vector<int>& numbers,
    long long target
) {
    int left = 0;
    int right = static_cast<int>(numbers.size()) - 1;

    while (left < right) {
        long long currentSum =
            static_cast<long long>(numbers[left]) +
            numbers[right];

        if (currentSum == target) {
            /*
             * Return 1-based positions to match the conventional problem
             * specification.
             */
            return {left + 1, right + 1};
        }

        if (currentSum < target) {
            ++left;
        } else {
            --right;
        }
    }

    return {-1, -1};
}


// ============================================================================
// MEDIUM 3 — Subarray Sum Equals K
// ============================================================================

long long subarraySumEqualsK(
    const vector<int>& numbers,
    long long target
) {
    /*
     * The frequency map is important.
     *
     * If the current prefix sum is P, a previous prefix sum of P-target
     * creates a subarray whose sum is target.
     */
    unordered_map<long long, long long> prefixFrequency;

    prefixFrequency[0] = 1;

    long long prefixSum = 0;
    long long count = 0;

    for (int value : numbers) {
        prefixSum += value;

        long long requiredPrefix = prefixSum - target;

        auto iterator = prefixFrequency.find(requiredPrefix);

        if (iterator != prefixFrequency.end()) {
            count += iterator->second;
        }

        ++prefixFrequency[prefixSum];
    }

    return count;
}


// ============================================================================
// MEDIUM 4 — Product of Array Except Self
// ============================================================================

vector<long long> productExceptSelf(
    const vector<int>& numbers
) {
    vector<long long> result(numbers.size(), 1);

    long long prefixProduct = 1;

    for (size_t index = 0;
         index < numbers.size();
         ++index) {

        result[index] = prefixProduct;
        prefixProduct *= numbers[index];
    }

    long long suffixProduct = 1;

    for (int index = static_cast<int>(numbers.size()) - 1;
         index >= 0;
         --index) {

        result[index] *= suffixProduct;
        suffixProduct *= numbers[index];
    }

    return result;
}


// ============================================================================
// HARD — Trapping Rain Water
// ============================================================================

long long trapRainWater(const vector<int>& heights) {
    if (heights.size() < 3) {
        return 0;
    }

    int left = 0;
    int right = static_cast<int>(heights.size()) - 1;

    int leftMax = 0;
    int rightMax = 0;

    long long trappedWater = 0;

    /*
     * If height[left] <= height[right], the left boundary is the limiting
     * side. The right boundary is already at least as high as the current
     * left boundary.
     *
     * This invariant permits constant auxiliary space.
     */
    while (left < right) {
        if (heights[left] <= heights[right]) {
            if (heights[left] >= leftMax) {
                leftMax = heights[left];
            } else {
                trappedWater +=
                    static_cast<long long>(leftMax) -
                    heights[left];
            }

            ++left;
        } else {
            if (heights[right] >= rightMax) {
                rightMax = heights[right];
            } else {
                trappedWater +=
                    static_cast<long long>(rightMax) -
                    heights[right];
            }

            --right;
        }
    }

    return trappedWater;
}


// ============================================================================
// Reference implementation for the difficult problem
// ============================================================================

long long trapRainWaterWithArrays(
    const vector<int>& heights
) {
    if (heights.size() < 3) {
        return 0;
    }

    const size_t n = heights.size();

    vector<int> leftMax(n);
    vector<int> rightMax(n);

    leftMax[0] = heights[0];

    for (size_t index = 1; index < n; ++index) {
        leftMax[index] =
            max(leftMax[index - 1], heights[index]);
    }

    rightMax[n - 1] = heights[n - 1];

    for (size_t index = n - 1; index-- > 0;) {
        rightMax[index] =
            max(rightMax[index + 1], heights[index]);
    }

    long long water = 0;

    for (size_t index = 0; index < n; ++index) {
        water +=
            min(leftMax[index], rightMax[index]) -
            heights[index];
    }

    return water;
}


// ============================================================================
// Assessment engine
// ============================================================================

class ArrayAssessmentEngine {
private:
    vector<ProblemMetadata> metadata;
    vector<AssessmentResult> results;

    void record(
        const string& name,
        bool passed,
        const string& details
    ) {
        results.push_back({name, passed, details});
    }

public:
    ArrayAssessmentEngine()
        : metadata{
              {
                  "Find Pivot Index",
                  "Easy",
                  "Prefix-sum reasoning",
                  "Total sum plus running left sum.",
                  "O(n)",
                  "O(1) auxiliary",
                  "Repeatedly calculate both sides.",
                  "Derive right sum from the total.",
              },
              {
                  "Move Zeroes",
                  "Easy",
                  "Two pointers / stable compaction",
                  "Read pointer plus write pointer.",
                  "O(n)",
                  "O(1)",
                  "Remove elements while traversing.",
                  "Modify the array in place.",
              },
              {
                  "Maximum Subarray",
                  "Easy",
                  "Kadane's algorithm",
                  "Track the best sum ending at each position.",
                  "O(n)",
                  "O(1)",
                  "Initialize the best answer to zero.",
                  "Initialize from the first element.",
              },
              {
                  "Maximum Sum Subarray of Size K",
                  "Medium",
                  "Fixed-size sliding window",
                  "Reuse the previous window sum.",
                  "O(n)",
                  "O(1)",
                  "Recompute every window.",
                  "Subtract outgoing and add incoming values.",
              },
              {
                  "Two Sum II",
                  "Medium",
                  "Opposite-direction two pointers",
                  "Exploit sorted order.",
                  "O(n)",
                  "O(1)",
                  "Ignore the sorted constraint.",
                  "Move the pointer that can correct the sum.",
              },
              {
                  "Subarray Sum Equals K",
                  "Medium",
                  "Prefix sum + frequency map",
                  "Count previous prefix sums equal to current-target.",
                  "O(n) expected",
                  "O(n)",
                  "Use sliding window with negative values.",
                  "Use prefix sums and frequencies.",
              },
              {
                  "Product of Array Except Self",
                  "Medium",
                  "Prefix and suffix products",
                  "Two passes using the output array.",
                  "O(n)",
                  "O(1) auxiliary",
                  "Use division without zero handling.",
                  "Avoid division and reuse output storage.",
              },
              {
                  "Trapping Rain Water",
                  "Hard",
                  "Two pointers + boundary maxima",
                  "Process the lower boundary.",
                  "O(n)",
                  "O(1)",
                  "Scan both sides independently per position.",
                  "Maintain running boundary maxima.",
              },
          } {}

    {}

    void runAssessment() {
        results.clear();

        try {
            vector<int> input = {1, 7, 3, 6, 5, 6};

            record(
                "Find Pivot Index",
                findPivotIndex(input) == 3,
                "Expected pivot index 3."
            );
        } catch (const exception& error) {
            record(
                "Find Pivot Index",
                false,
                string("Exception: ") + error.what()
            );
        }

        try {
            vector<int> input = {0, 1, 0, 3, 12};

            moveZeroes(input);

            record(
                "Move Zeroes",
                input == vector<int>({1, 3, 12, 0, 0}),
                "Expected [1, 3, 12, 0, 0]."
            );
        } catch (const exception& error) {
            record(
                "Move Zeroes",
                false,
                string("Exception: ") + error.what()
            );
        }

        try {
            vector<int> input =
                {-2, 1, -3, 4, -1, 2, 1, -5, 4};

            SubarrayResult result = maximumSubarray(input);

            record(
                "Maximum Subarray",
                result == SubarrayResult{6, 3, 6},
                "Expected sum 6 from indices 3 through 6."
            );
        } catch (const exception& error) {
            record(
                "Maximum Subarray",
                false,
                string("Exception: ") + error.what()
            );
        }

        try {
            vector<int> input = {2, 1, 5, 1, 3, 2};

            record(
                "Maximum Sum Subarray of Size K",
                maximumSumSubarrayOfSizeK(input, 3) == 9,
                "Expected maximum window sum 9."
            );
        } catch (const exception& error) {
            record(
                "Maximum Sum Subarray of Size K",
                false,
                string("Exception: ") + error.what()
            );
        }

        try {
            vector<int> input = {2, 7, 11, 15};

            record(
                "Two Sum II",
                twoSumSorted(input, 9) == pair<int, int>{1, 2},
                "Expected 1-based positions [1, 2]."
            );
        } catch (const exception& error) {
            record(
                "Two Sum II",
                false,
                string("Exception: ") + error.what()
            );
        }

        try {
            vector<int> input = {1, 1, 1};

            record(
                "Subarray Sum Equals K",
                subarraySumEqualsK(input, 2) == 2,
                "Expected two subarrays."
            );
        } catch (const exception& error) {
            record(
                "Subarray Sum Equals K",
                false,
                string("Exception: ") + error.what()
            );
        }

        try {
            vector<int> input = {1, 2, 3, 4};

            record(
                "Product of Array Except Self",
                productExceptSelf(input) ==
                    vector<long long>({24, 12, 8, 6}),
                "Expected [24, 12, 8, 6]."
            );
        } catch (const exception& error) {
            record(
                "Product of Array Except Self",
                false,
                string("Exception: ") + error.what()
            );
        }

        try {
            vector<int> input =
                {0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1};

            record(
                "Trapping Rain Water",
                trapRainWater(input) == 6,
                "Expected six units of trapped water."
            );
        } catch (const exception& error) {
            record(
                "Trapping Rain Water",
                false,
                string("Exception: ") + error.what()
            );
        }
    }

    void printMetadata() const {
        printSection("PROBLEM DOCUMENTATION");

        for (size_t index = 0;
             index < metadata.size();
             ++index) {

            const auto& problem = metadata[index];

            cout << "\n"
                 << index + 1 << ". "
                 << problem.name
                 << " [" << problem.difficulty << "]\n";

            cout << "Pattern: "
                 << problem.pattern << "\n";

            cout << "Approach: "
                 << problem.approach << "\n";

            cout << "Time Complexity: "
                 << problem.timeComplexity << "\n";

            cout << "Space Complexity: "
                 << problem.spaceComplexity << "\n";

            cout << "Mistake: "
                 << problem.mistake << "\n";

            cout << "Improvement: "
                 << problem.improvement << "\n";
        }
    }

    void printResults() const {
        printSection("ASSESSMENT RESULTS");

        int passed = 0;

        for (const auto& result : results) {
            cout << left
                 << setw(42)
                 << result.problemName
                 << (result.passed ? "PASS" : "FAIL")
                 << "\n";

            cout << "  " << result.details << "\n";

            if (result.passed) {
                ++passed;
            }
        }

        cout << "\nScore: "
             << passed
             << "/"
             << results.size()
             << "\n";
    }
};


// ============================================================================
// Complexity and performance demonstration
// ============================================================================

template <typename Function>
double benchmarkMilliseconds(
    Function function,
    int repetitions
) {
    using Clock = chrono::high_resolution_clock;

    auto start = Clock::now();

    for (int iteration = 0;
         iteration < repetitions;
         ++iteration) {

        function();
    }

    auto end = Clock::now();

    chrono::duration<double, milli> elapsed =
        end - start;

    return elapsed.count() / repetitions;
}

void demonstratePerformance() {
    printSection("PERFORMANCE COMPARISON");

    vector<int> input(2000);

    iota(input.begin(), input.end(), 1);

    const int k = 100;

    /*
     * A brute-force implementation is intentionally included here only to
     * make the complexity difference concrete.
     */
    auto bruteForce = [&]() {
        long long best = numeric_limits<long long>::lowest();

        for (int start = 0;
             start <= static_cast<int>(input.size()) - k;
             ++start) {

            long long sum = 0;

            for (int index = start;
                 index < start + k;
                 ++index) {

                sum += input[index];
            }

            best = max(best, sum);
        }

        volatile long long preventOptimization = best;
        (void)preventOptimization;
    };

    auto optimized = [&]() {
        volatile long long result =
            maximumSumSubarrayOfSizeK(input, k);

        (void)result;
    };

    const double bruteTime =
        benchmarkMilliseconds(bruteForce, 3);

    const double optimizedTime =
        benchmarkMilliseconds(optimized, 100);

    cout << fixed << setprecision(6);

    cout << "Input size: "
         << input.size()
         << "\n";

    cout << "Window size: "
         << k
         << "\n";

    cout << "Brute force average: "
         << bruteTime
         << " ms\n";

    cout << "Sliding window average: "
         << optimizedTime
         << " ms\n";

    cout << "\nThe meaningful algorithmic comparison is O(n*k) "
            "versus O(n). Hardware-dependent timings are only "
            "illustrative.\n";
}


// ============================================================================
// Edge-case demonstration
// ============================================================================

void demonstrateEdgeCases() {
    printSection("EDGE CASES");

    const vector<vector<int>> cases = {
        {},
        {7},
        {0, 0, 0},
        {-5, -2, -9},
        {-3, 4, -1, 2, -6, 5},
        {1, 2, 3, 4, 5},
        {5, 4, 3, 2, 1},
        {2, 2, 2, 2},
    };

    const vector<string> names = {
        "Empty array",
        "Single element",
        "All zeroes",
        "All negative",
        "Mixed signs",
        "Sorted",
        "Reverse sorted",
        "Duplicates",
    };

    for (size_t index = 0;
         index < cases.size();
         ++index) {

        cout << left
             << setw(20)
             << names[index]
             << formatVector(cases[index])
             << "\n";
    }

    cout << "\nEdge cases are important because an algorithm that "
            "works only on positive, distinct, non-empty input is "
            "usually relying on an unstated assumption.\n";
}


// ============================================================================
// Architectural explanation
// ============================================================================

void explainArchitecture() {
    printSection("CASE STUDY ARCHITECTURE");

    cout
        << "The ArrayAssessmentEngine separates the system into four layers:\n\n"
        << "1. Algorithms\n"
        << "   Each array problem is implemented as an independent function.\n\n"
        << "2. Metadata\n"
        << "   Each problem records pattern, approach, complexity, mistake, "
           "and improvement.\n\n"
        << "3. Validation\n"
        << "   Deterministic test cases compare actual results against expected "
           "results.\n\n"
        << "4. Reporting\n"
        << "   The engine prints a structured assessment result and score.\n\n"
        << "This separation makes the code easier to test, replace, benchmark, "
           "and extend.\n";
}


// ============================================================================
// Main
// ============================================================================

int main() {
    try {
        printSection("DAY 19 — ARRAY ASSESSMENT");

        cout
            << "C++17 industry-style case study\n"
            << "3 Easy + 4 Medium + 1 Difficult\n"
            << "Focus: reusable array algorithms and assessment reporting\n";

        explainArchitecture();

        ArrayAssessmentEngine engine;

        engine.runAssessment();
        engine.printMetadata();
        engine.printResults();

        demonstrateEdgeCases();
        demonstratePerformance();

        printSection("ASSESSMENT COMPLETE");

        cout
            << "The eight array problems were implemented as reusable "
               "algorithms and evaluated through a structured C++ assessment "
               "engine.\n";

        return 0;
    }
    catch (const exception& error) {
        cerr << "Fatal error: "
             << error.what()
             << "\n";

        return 1;
    }
}
