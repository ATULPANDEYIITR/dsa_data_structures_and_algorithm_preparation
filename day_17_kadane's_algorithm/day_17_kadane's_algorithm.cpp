/*
    Day 17 — Kadane's Algorithm
    ============================

    Industry-style case study:
    Real-time infrastructure health analysis.

    Scenario
    --------
    A distributed service records a sequence of normalized changes in a
    health/performance score. Positive values represent improvements and
    negative values represent deterioration.

    The operations team wants to identify:

        1. The strongest contiguous improvement interval.
        2. The exact interval responsible for that result.
        3. The worst deterioration interval.
        4. The strongest circular interval when monitoring periods wrap.
        5. The strongest interval when one anomalous observation can be
           discarded.
        6. Streaming analysis without storing the complete history.
        7. Validation and consistency checks.

    This program uses C++17 and only the standard library.

    Compile:
        g++ -std=c++17 -O2 -Wall -Wextra -pedantic day17.cpp -o day17

    Run:
        ./day17
*/

#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

using namespace std;

// -----------------------------------------------------------------------------
// 1. Domain model
// -----------------------------------------------------------------------------

struct SubarrayResult {
    long long sum{};
    size_t start{};
    size_t end{};

    size_t length() const {
        return end >= start ? end - start + 1 : 0;
    }
};

// -----------------------------------------------------------------------------
// 2. Validation
// -----------------------------------------------------------------------------

void validateNonEmpty(const vector<long long>& values) {
    if (values.empty()) {
        throw invalid_argument(
            "The input sequence must not be empty."
        );
    }
}

// -----------------------------------------------------------------------------
// 3. O(n^3) reference implementation
// -----------------------------------------------------------------------------

SubarrayResult maximumSubarrayCubic(
    const vector<long long>& values
) {
    validateNonEmpty(values);

    SubarrayResult best{
        values[0],
        0,
        0
    };

    for (size_t start = 0; start < values.size(); ++start) {
        for (size_t end = start; end < values.size(); ++end) {
            long long currentSum = 0;

            for (size_t index = start; index <= end; ++index) {
                currentSum += values[index];
            }

            if (currentSum > best.sum) {
                best = {
                    currentSum,
                    start,
                    end
                };
            }
        }
    }

    return best;
}

// -----------------------------------------------------------------------------
// 4. O(n^2) running-sum implementation
// -----------------------------------------------------------------------------

SubarrayResult maximumSubarrayQuadratic(
    const vector<long long>& values
) {
    validateNonEmpty(values);

    SubarrayResult best{
        values[0],
        0,
        0
    };

    for (size_t start = 0; start < values.size(); ++start) {
        long long currentSum = 0;

        for (size_t end = start; end < values.size(); ++end) {
            currentSum += values[end];

            if (currentSum > best.sum) {
                best = {
                    currentSum,
                    start,
                    end
                };
            }
        }
    }

    return best;
}

// -----------------------------------------------------------------------------
// 5. Standard Kadane implementation
// -----------------------------------------------------------------------------

SubarrayResult kadane(
    const vector<long long>& values
) {
    validateNonEmpty(values);

    long long currentSum = values[0];
    long long bestSum = values[0];

    size_t currentStart = 0;
    size_t bestStart = 0;
    size_t bestEnd = 0;

    for (size_t index = 1; index < values.size(); ++index) {
        const long long value = values[index];

        /*
            The central reset decision:

                value > currentSum + value

            means the previous accumulated sum is harmful enough that the
            best subarray ending at this index should start here instead.
        */
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

    return {
        bestSum,
        bestStart,
        bestEnd
    };
}

// -----------------------------------------------------------------------------
// 6. Minimum subarray
// -----------------------------------------------------------------------------

SubarrayResult minimumSubarray(
    const vector<long long>& values
) {
    validateNonEmpty(values);

    long long currentSum = values[0];
    long long bestSum = values[0];

    size_t currentStart = 0;
    size_t bestStart = 0;
    size_t bestEnd = 0;

    for (size_t index = 1; index < values.size(); ++index) {
        const long long value = values[index];

        if (value < currentSum + value) {
            currentSum = value;
            currentStart = index;
        } else {
            currentSum += value;
        }

        if (currentSum < bestSum) {
            bestSum = currentSum;
            bestStart = currentStart;
            bestEnd = index;
        }
    }

    return {
        bestSum,
        bestStart,
        bestEnd
    };
}

// -----------------------------------------------------------------------------
// 7. Circular maximum subarray
// -----------------------------------------------------------------------------

struct CircularResult {
    long long sum{};
    vector<long long> values;
    bool wraps{};
};

CircularResult maximumCircularSubarray(
    const vector<long long>& values
) {
    validateNonEmpty(values);

    const SubarrayResult normal = kadane(values);

    /*
        If every value is negative, total - minimumSubarray would effectively
        remove the entire array. The problem requires a non-empty subarray,
        so the ordinary Kadane result is correct.
    */
    if (normal.sum < 0) {
        return {
            normal.sum,
            vector<long long>(
                values.begin() + static_cast<ptrdiff_t>(normal.start),
                values.begin() + static_cast<ptrdiff_t>(normal.end) + 1
            ),
            false
        };
    }

    const SubarrayResult minimum = minimumSubarray(values);

    const long long total = accumulate(
        values.begin(),
        values.end(),
        0LL
    );

    const long long wrappedSum = total - minimum.sum;

    if (wrappedSum <= normal.sum) {
        return {
            normal.sum,
            vector<long long>(
                values.begin() + static_cast<ptrdiff_t>(normal.start),
                values.begin() + static_cast<ptrdiff_t>(normal.end) + 1
            ),
            false
        };
    }

    vector<long long> wrappedValues;

    for (size_t index = minimum.end + 1;
         index < values.size();
         ++index) {
        wrappedValues.push_back(values[index]);
    }

    for (size_t index = 0;
         index < minimum.start;
         ++index) {
        wrappedValues.push_back(values[index]);
    }

    return {
        wrappedSum,
        wrappedValues,
        true
    };
}

// -----------------------------------------------------------------------------
// 8. Maximum subarray with one deletion
// -----------------------------------------------------------------------------

long long maximumSubarrayOneDeletion(
    const vector<long long>& values
) {
    validateNonEmpty(values);

    long long keep = values[0];
    long long deleted = numeric_limits<long long>::lowest() / 4;
    long long best = values[0];

    for (size_t index = 1; index < values.size(); ++index) {
        const long long value = values[index];

        /*
            newDeleted has two possibilities:

                1. A deletion happened earlier and the current value is kept.
                2. The current value is deleted, leaving the old keep state.
        */
        const long long newDeleted = max(
            deleted + value,
            keep
        );

        const long long newKeep = max(
            value,
            keep + value
        );

        keep = newKeep;
        deleted = newDeleted;

        best = max({
            best,
            keep,
            deleted
        });
    }

    return best;
}

// -----------------------------------------------------------------------------
// 9. Streaming Kadane
// -----------------------------------------------------------------------------

class StreamingKadane {
private:
    bool initialized_ = false;
    long long currentSum_ = 0;
    long long bestSum_ = 0;

    size_t currentStart_ = 0;
    size_t bestStart_ = 0;
    size_t bestEnd_ = 0;
    size_t position_ = 0;

public:
    void add(long long value) {
        if (!initialized_) {
            initialized_ = true;
            currentSum_ = value;
            bestSum_ = value;
            currentStart_ = 0;
            bestStart_ = 0;
            bestEnd_ = 0;
            position_ = 0;
            return;
        }

        ++position_;

        if (value > currentSum_ + value) {
            currentSum_ = value;
            currentStart_ = position_;
        } else {
            currentSum_ += value;
        }

        if (currentSum_ > bestSum_) {
            bestSum_ = currentSum_;
            bestStart_ = currentStart_;
            bestEnd_ = position_;
        }
    }

    bool empty() const {
        return !initialized_;
    }

    SubarrayResult result() const {
        if (!initialized_) {
            throw logic_error(
                "Cannot request a result before adding a value."
            );
        }

        return {
            bestSum_,
            bestStart_,
            bestEnd_
        };
    }
};

// -----------------------------------------------------------------------------
// 10. Maximum fixed-length subarray
// -----------------------------------------------------------------------------

SubarrayResult maximumFixedLengthSubarray(
    const vector<long long>& values,
    size_t length
) {
    validateNonEmpty(values);

    if (length == 0) {
        throw invalid_argument(
            "Window length must be positive."
        );
    }

    if (length > values.size()) {
        throw invalid_argument(
            "Window length exceeds the input size."
        );
    }

    long long currentSum = 0;

    for (size_t index = 0; index < length; ++index) {
        currentSum += values[index];
    }

    long long bestSum = currentSum;
    size_t bestStart = 0;

    for (
        size_t start = 1;
        start + length <= values.size();
        ++start
    ) {
        currentSum += values[start + length - 1];
        currentSum -= values[start - 1];

        if (currentSum > bestSum) {
            bestSum = currentSum;
            bestStart = start;
        }
    }

    return {
        bestSum,
        bestStart,
        bestStart + length - 1
    };
}

// -----------------------------------------------------------------------------
// 11. Prefix-sum formulation
// -----------------------------------------------------------------------------

long long maximumSubarrayPrefixSum(
    const vector<long long>& values
) {
    validateNonEmpty(values);

    long long prefixSum = 0;
    long long minimumPrefix = 0;
    long long best = values[0];

    for (const long long value : values) {
        prefixSum += value;

        best = max(
            best,
            prefixSum - minimumPrefix
        );

        minimumPrefix = min(
            minimumPrefix,
            prefixSum
        );
    }

    return best;
}

// -----------------------------------------------------------------------------
// 12. Utility functions
// -----------------------------------------------------------------------------

vector<long long> extract(
    const vector<long long>& values,
    const SubarrayResult& result
) {
    return vector<long long>(
        values.begin() +
            static_cast<ptrdiff_t>(result.start),
        values.begin() +
            static_cast<ptrdiff_t>(result.end) + 1
    );
}

void printVector(
    const vector<long long>& values
) {
    cout << "[";

    for (size_t index = 0; index < values.size(); ++index) {
        if (index > 0) {
            cout << ", ";
        }

        cout << values[index];
    }

    cout << "]";
}

void printResult(
    const string& label,
    const SubarrayResult& result
) {
    cout << left
         << setw(30)
         << label
         << " sum=" << result.sum
         << ", range=["
         << result.start
         << ", "
         << result.end
         << "]"
         << ", length="
         << result.length()
         << "\n";
}

// -----------------------------------------------------------------------------
// 13. Service-health case study
// -----------------------------------------------------------------------------

class ServiceHealthAnalyzer {
public:
    /*
        Analyze a sequence of normalized hourly changes.

        The domain model deliberately keeps the algorithm independent from
        infrastructure-specific concepts. A production application could
        populate the vector from logs, telemetry, metrics, or a database.
    */
    static SubarrayResult strongestImprovement(
        const vector<long long>& hourlyChanges
    ) {
        return kadane(hourlyChanges);
    }

    static SubarrayResult strongestDeterioration(
        const vector<long long>& hourlyChanges
    ) {
        return minimumSubarray(hourlyChanges);
    }

    static long long improvementScore(
        const vector<long long>& hourlyChanges
    ) {
        return maximumSubarrayPrefixSum(hourlyChanges);
    }
};

// -----------------------------------------------------------------------------
// 14. Test infrastructure
// -----------------------------------------------------------------------------

void expectEqual(
    long long actual,
    long long expected,
    const string& description
) {
    if (actual != expected) {
        throw runtime_error(
            "Test failed: " +
            description +
            ". Expected " +
            to_string(expected) +
            ", got " +
            to_string(actual)
        );
    }
}

void runDeterministicTests() {
    expectEqual(
        kadane({1, 2, 3}).sum,
        6,
        "positive array"
    );

    expectEqual(
        kadane({-5, -2, -9}).sum,
        -2,
        "all-negative array"
    );

    expectEqual(
        kadane({
            -2, 1, -3, 4,
            -1, 2, 1, -5, 4
        }).sum,
        6,
        "classic maximum subarray"
    );

    expectEqual(
        minimumSubarray({
            3, -4, 2, -3, -1, 7
        }).sum,
        -6,
        "minimum subarray"
    );

    expectEqual(
        maximumSubarrayOneDeletion({
            1, -2, 0, 3
        }),
        4,
        "one deletion"
    );

    expectEqual(
        maximumFixedLengthSubarray({
            2, -1, 5, -3, 4
        }, 3).sum,
        6,
        "fixed window"
    );

    expectEqual(
        maximumSubarrayPrefixSum({
            -2, 1, -3, 4,
            -1, 2, 1, -5, 4
        }),
        6,
        "prefix formulation"
    );

    bool threw = false;

    try {
        kadane({});
    } catch (const invalid_argument&) {
        threw = true;
    }

    assert(threw);

    cout << "Deterministic tests: PASSED\n";
}

// -----------------------------------------------------------------------------
// 15. Randomized differential testing
// -----------------------------------------------------------------------------

void runRandomizedVerification() {
    mt19937 generator(17);
    uniform_int_distribution<int> lengthDistribution(1, 20);
    uniform_int_distribution<int> valueDistribution(-20, 20);

    constexpr int trials = 500;

    for (int trial = 0; trial < trials; ++trial) {
        const int length = lengthDistribution(generator);

        vector<long long> values;
        values.reserve(static_cast<size_t>(length));

        for (int index = 0; index < length; ++index) {
            values.push_back(valueDistribution(generator));
        }

        const long long cubic =
            maximumSubarrayCubic(values).sum;

        const long long quadratic =
            maximumSubarrayQuadratic(values).sum;

        const long long linear =
            kadane(values).sum;

        const long long prefix =
            maximumSubarrayPrefixSum(values);

        if (
            cubic != quadratic ||
            quadratic != linear ||
            linear != prefix
        ) {
            cerr << "Randomized verification failed.\n";
            printVector(values);
            cerr << "\n";
            throw runtime_error(
                "Algorithm implementations disagree."
            );
        }
    }

    cout << "Randomized verification: "
         << trials
         << " trials PASSED\n";
}

// -----------------------------------------------------------------------------
// 16. Demonstrate reset decisions
// -----------------------------------------------------------------------------

void printKadaneTrace(
    const vector<long long>& values
) {
    validateNonEmpty(values);

    long long current = values[0];
    long long best = values[0];

    cout << left
         << setw(8) << "Index"
         << setw(10) << "Value"
         << setw(14) << "Current"
         << setw(14) << "Best"
         << "Decision\n";

    cout << string(60, '-') << "\n";

    cout << left
         << setw(8) << 0
         << setw(10) << values[0]
         << setw(14) << current
         << setw(14) << best
         << "start\n";

    for (size_t index = 1; index < values.size(); ++index) {
        const long long value = values[index];
        const long long extended = current + value;

        string decision;

        if (value > extended) {
            current = value;
            decision = "reset";
        } else {
            current = extended;
            decision = "extend";
        }

        best = max(best, current);

        cout << left
             << setw(8) << index
             << setw(10) << value
             << setw(14) << current
             << setw(14) << best
             << decision
             << "\n";
    }
}

// -----------------------------------------------------------------------------
// 17. Industry-style scenario
// -----------------------------------------------------------------------------

void runServiceHealthCaseStudy() {
    cout << "\nService-health monitoring case study\n";
    cout << "-----------------------------------\n";

    /*
        Each value is a normalized change in service health during one hour.

        Positive:
            recovery, performance improvement, capacity stabilization.

        Negative:
            latency increase, error-rate deterioration, capacity pressure.

        The values are intentionally abstract. A real monitoring pipeline
        would define the normalization and data quality rules separately.
    */
    const vector<long long> hourlyChanges = {
        -3, 4, -1, 2, 1,
        -8, 5, 2, -1, 3,
        -4, 6, 2, -10, 4
    };

    printVector(hourlyChanges);
    cout << "\n\n";

    const SubarrayResult improvement =
        ServiceHealthAnalyzer::strongestImprovement(
            hourlyChanges
        );

    const SubarrayResult deterioration =
        ServiceHealthAnalyzer::strongestDeterioration(
            hourlyChanges
        );

    printResult(
        "Strongest improvement interval",
        improvement
    );

    cout << "Improvement values: ";
    printVector(extract(hourlyChanges, improvement));
    cout << "\n";

    printResult(
        "Strongest deterioration interval",
        deterioration
    );

    cout << "Deterioration values: ";
    printVector(extract(hourlyChanges, deterioration));
    cout << "\n";

    cout << "Net maximum score: "
         << ServiceHealthAnalyzer::improvementScore(
                hourlyChanges
            )
         << "\n";
}

// -----------------------------------------------------------------------------
// 18. Main
// -----------------------------------------------------------------------------

int main() {
    try {
        cout << "Day 17 — Kadane's Algorithm\n";
        cout << "===========================\n";

        const vector<long long> values = {
            -2, 1, -3, 4,
            -1, 2, 1, -5, 4
        };

        cout << "\nBasic example\n";
        cout << "-------------\n";

        cout << "Input: ";
        printVector(values);
        cout << "\n";

        printResult(
            "Cubic reference",
            maximumSubarrayCubic(values)
        );

        printResult(
            "Quadratic running sum",
            maximumSubarrayQuadratic(values)
        );

        printResult(
            "Kadane",
            kadane(values)
        );

        cout << "Kadane values: ";
        printVector(
            extract(
                values,
                kadane(values)
            )
        );
        cout << "\n";

        cout << "\nKadane state trace\n";
        cout << "------------------\n";
        printKadaneTrace(values);

        cout << "\nNegative-value edge case\n";
        cout << "------------------------\n";

        const vector<long long> negative = {
            -8, -3, -10, -4
        };

        printResult(
            "All-negative input",
            kadane(negative)
        );

        cout << "\nCircular maximum\n";
        cout << "-----------------\n";

        const vector<vector<long long>> circularCases = {
            {5, -3, 5},
            {3, -2, 2, -3},
            {-3, -2, -1},
            {1, 2, 3, 4}
        };

        for (const auto& testCase : circularCases) {
            cout << "Input: ";
            printVector(testCase);
            cout << "\n";

            const CircularResult result =
                maximumCircularSubarray(testCase);

            cout << "Sum: "
                 << result.sum
                 << ", wraps: "
                 << boolalpha
                 << result.wraps
                 << ", values: ";

            printVector(result.values);
            cout << "\n\n";
        }

        cout << "One-deletion variant\n";
        cout << "--------------------\n";

        const vector<long long> deletionInput = {
            1, -2, 0, 3
        };

        cout << "Input: ";
        printVector(deletionInput);
        cout << "\n";

        cout << "Maximum with at most one deletion: "
             << maximumSubarrayOneDeletion(
                    deletionInput
                )
             << "\n";

        cout << "\nFixed-length variant\n";
        cout << "--------------------\n";

        const vector<long long> fixedInput = {
            2, -1, 5, -3, 4, 6, -2
        };

        const SubarrayResult fixedResult =
            maximumFixedLengthSubarray(
                fixedInput,
                3
            );

        printResult(
            "Best window of length 3",
            fixedResult
        );

        cout << "\nStreaming variant\n";
        cout << "-----------------\n";

        StreamingKadane stream;

        for (const long long value : values) {
            stream.add(value);

            const SubarrayResult partial =
                stream.result();

            cout << "Added "
                 << setw(3)
                 << value
                 << " -> current best = "
                 << partial.sum
                 << ", range ["
                 << partial.start
                 << ", "
                 << partial.end
                 << "]\n";
        }

        runServiceHealthCaseStudy();

        cout << "\nValidation tests\n";
        cout << "-----------------\n";
        runDeterministicTests();

        cout << "\nDifferential randomized testing\n";
        cout << "--------------------------------\n";
        runRandomizedVerification();

        cout << "\nComplexity\n";
        cout << "----------\n";
        cout << left
             << setw(32) << "Algorithm"
             << setw(12) << "Time"
             << "Auxiliary space\n";

        cout << string(60, '-') << "\n";

        cout << left
             << setw(32) << "Cubic brute force"
             << setw(12) << "O(n^3)"
             << "O(1)\n";

        cout << left
             << setw(32) << "Quadratic running sum"
             << setw(12) << "O(n^2)"
             << "O(1)\n";

        cout << left
             << setw(32) << "Kadane"
             << setw(12) << "O(n)"
             << "O(1)\n";

        cout << left
             << setw(32) << "Prefix-sum scan"
             << setw(12) << "O(n)"
             << "O(1)\n";

        cout << left
             << setw(32) << "Circular Kadane"
             << setw(12) << "O(n)"
             << "O(1)\n";

        cout << left
             << setw(32) << "One-deletion DP"
             << setw(12) << "O(n)"
             << "O(1)\n";

        cout << "\nProgram completed successfully.\n";
    }
    catch (const exception& error) {
        cerr << "Fatal error: "
             << error.what()
             << "\n";

        return 1;
    }

    return 0;
}
