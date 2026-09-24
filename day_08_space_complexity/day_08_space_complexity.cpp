/*
 * Day 8 — Space Complexity
 *
 * C++17 case study:
 * A memory-aware telemetry processing system.
 *
 * The program demonstrates:
 *   - input space vs auxiliary space
 *   - scalar variables
 *   - arrays/vectors
 *   - in-place processing
 *   - recursion stack
 *   - strings
 *   - unordered_set and unordered_map
 *   - time-space trade-offs
 *   - streaming-style processing
 *   - bounded memory
 *   - space-optimized dynamic programming
 *   - validation and failure conditions
 *
 * Compile:
 *   g++ -std=c++17 -O2 -Wall -Wextra -pedantic day8_space_complexity.cpp -o day8
 */

#include <algorithm>
#include <cstddef>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using std::cout;
using std::size_t;
using std::string;
using std::unordered_map;
using std::unordered_set;
using std::vector;


// ============================================================================
// 1. DOMAIN MODEL
// ============================================================================

struct SensorReading {
    int sensorId;
    double temperature;
};

struct SensorSummary {
    int sensorId;
    double minimum;
    double maximum;
    double average;
    size_t readingCount;
};


// ============================================================================
// 2. INPUT VALIDATION
// ============================================================================

void validateReading(const SensorReading& reading) {
    if (reading.sensorId < 0) {
        throw std::invalid_argument("Sensor ID cannot be negative.");
    }

    if (!std::isfinite(reading.temperature)) {
        throw std::invalid_argument("Temperature must be finite.");
    }
}

void validateReadings(const vector<SensorReading>& readings) {
    for (const auto& reading : readings) {
        validateReading(reading);
    }
}


// ============================================================================
// 3. CONSTANT-SPACE SCANNING
// ============================================================================

double maximumTemperature(const vector<SensorReading>& readings) {
    if (readings.empty()) {
        throw std::invalid_argument(
            "Cannot calculate maximum of an empty collection."
        );
    }

    // Only a fixed number of scalar variables are used.
    // Auxiliary space: O(1).
    double maximum = readings.front().temperature;

    for (const auto& reading : readings) {
        if (reading.temperature > maximum) {
            maximum = reading.temperature;
        }
    }

    return maximum;
}

double minimumTemperature(const vector<SensorReading>& readings) {
    if (readings.empty()) {
        throw std::invalid_argument(
            "Cannot calculate minimum of an empty collection."
        );
    }

    double minimum = readings.front().temperature;

    for (const auto& reading : readings) {
        if (reading.temperature < minimum) {
            minimum = reading.temperature;
        }
    }

    return minimum;
}

double averageTemperature(const vector<SensorReading>& readings) {
    if (readings.empty()) {
        throw std::invalid_argument(
            "Cannot calculate average of an empty collection."
        );
    }

    // No second array is created.
    // Auxiliary space: O(1).
    double total = 0.0;

    for (const auto& reading : readings) {
        total += reading.temperature;
    }

    return total / static_cast<double>(readings.size());
}


// ============================================================================
// 4. IN-PLACE TRANSFORMATION
// ============================================================================

void normalizeTemperaturesInPlace(
    vector<SensorReading>& readings,
    double offset
) {
    /*
     * The existing vector is modified.
     *
     * Auxiliary space:
     *     O(1)
     *
     * The vector itself is input storage, not newly created working storage.
     */
    for (auto& reading : readings) {
        reading.temperature -= offset;
    }
}

vector<SensorReading> normalizeTemperaturesWithCopy(
    const vector<SensorReading>& readings,
    double offset
) {
    /*
     * A complete copy of the input is created.
     *
     * Additional storage:
     *     O(n)
     */
    vector<SensorReading> result = readings;

    for (auto& reading : result) {
        reading.temperature -= offset;
    }

    return result;
}


// ============================================================================
// 5. SET-BASED DUPLICATE DETECTION
// ============================================================================

bool hasDuplicateSensors(const vector<SensorReading>& readings) {
    /*
     * The set stores sensor IDs encountered so far.
     *
     * Space:
     *     O(k)
     *
     * where k is the number of distinct sensor IDs encountered.
     *
     * Worst case:
     *     O(n)
     */
    unordered_set<int> seen;

    for (const auto& reading : readings) {
        if (!seen.insert(reading.sensorId).second) {
            return true;
        }
    }

    return false;
}


// ============================================================================
// 6. CONSTANT-SPACE DUPLICATE DETECTION
// ============================================================================

bool hasDuplicateSensorsBruteForce(
    const vector<SensorReading>& readings
) {
    /*
     * No set or map is allocated.
     *
     * Auxiliary space:
     *     O(1)
     *
     * Time:
     *     O(n^2)
     */
    for (size_t first = 0; first < readings.size(); ++first) {
        for (size_t second = first + 1;
             second < readings.size();
             ++second) {

            if (readings[first].sensorId == readings[second].sensorId) {
                return true;
            }
        }
    }

    return false;
}


// ============================================================================
// 7. FREQUENCY MAP
// ============================================================================

unordered_map<int, size_t> countReadingsBySensor(
    const vector<SensorReading>& readings
) {
    /*
     * One map entry is stored per distinct sensor.
     *
     * Auxiliary space:
     *     O(k), where k = number of distinct sensors.
     *
     * Worst case:
     *     O(n)
     */
    unordered_map<int, size_t> counts;

    for (const auto& reading : readings) {
        ++counts[reading.sensorId];
    }

    return counts;
}


// ============================================================================
// 8. STRING SPACE
// ============================================================================

bool isPalindrome(const string& text) {
    /*
     * Two indexes scan inward.
     *
     * No reversed copy is constructed.
     *
     * Auxiliary space: O(1)
     */
    if (text.empty()) {
        return true;
    }

    size_t left = 0;
    size_t right = text.size() - 1;

    while (left < right) {
        if (text[left] != text[right]) {
            return false;
        }

        ++left;
        --right;
    }

    return true;
}

string reverseWithCopy(const string& text) {
    /*
     * The result is another string.
     *
     * Additional space: O(n).
     */
    string result = text;
    std::reverse(result.begin(), result.end());
    return result;
}


// ============================================================================
// 9. RECURSIVE CALL STACK
// ============================================================================

long long factorialRecursive(int n) {
    if (n < 0) {
        throw std::invalid_argument(
            "Factorial requires a non-negative integer."
        );
    }

    if (n <= 1) {
        return 1;
    }

    /*
     * Each invocation remains active until the deeper call returns.
     *
     * Maximum stack depth:
     *     O(n)
     *
     * Therefore auxiliary stack space:
     *     O(n)
     */
    return static_cast<long long>(n) * factorialRecursive(n - 1);
}

long long factorialIterative(int n) {
    if (n < 0) {
        throw std::invalid_argument(
            "Factorial requires a non-negative integer."
        );
    }

    /*
     * The iterative version does not accumulate n active stack frames.
     *
     * Auxiliary space: O(1)
     */
    long long result = 1;

    for (int value = 2; value <= n; ++value) {
        result *= value;
    }

    return result;
}


// ============================================================================
// 10. STREAMING-STYLE SUMMARY
// ============================================================================

SensorSummary summarizeSensor(
    const vector<SensorReading>& readings,
    int sensorId
) {
    /*
     * This function scans the input and retains only aggregate state.
     *
     * Auxiliary space: O(1)
     *
     * It does not construct a separate vector containing matching readings.
     */
    bool found = false;
    double minimum = 0.0;
    double maximum = 0.0;
    double total = 0.0;
    size_t count = 0;

    for (const auto& reading : readings) {
        if (reading.sensorId != sensorId) {
            continue;
        }

        if (!found) {
            minimum = reading.temperature;
            maximum = reading.temperature;
            found = true;
        } else {
            minimum = std::min(minimum, reading.temperature);
            maximum = std::max(maximum, reading.temperature);
        }

        total += reading.temperature;
        ++count;
    }

    if (!found) {
        throw std::out_of_range("Requested sensor has no readings.");
    }

    return SensorSummary{
        sensorId,
        minimum,
        maximum,
        total / static_cast<double>(count),
        count
    };
}


// ============================================================================
// 11. BOUNDED-MEMORY SLIDING WINDOW
// ============================================================================

std::optional<double> maximumWindowAverage(
    const vector<double>& values,
    size_t windowSize
) {
    /*
     * Only the current sum and indexes are stored.
     *
     * Auxiliary space:
     *     O(1)
     *
     * The input vector is not copied.
     */
    if (windowSize == 0 || windowSize > values.size()) {
        return std::nullopt;
    }

    double currentSum = 0.0;

    for (size_t index = 0; index < windowSize; ++index) {
        currentSum += values[index];
    }

    double maximumSum = currentSum;

    for (size_t index = windowSize;
         index < values.size();
         ++index) {

        currentSum += values[index];
        currentSum -= values[index - windowSize];

        maximumSum = std::max(maximumSum, currentSum);
    }

    return maximumSum / static_cast<double>(windowSize);
}


// ============================================================================
// 12. SPACE-OPTIMIZED DYNAMIC PROGRAMMING
// ============================================================================

unsigned long long fibonacciWithArray(int n) {
    if (n < 0) {
        throw std::invalid_argument(
            "Fibonacci index must be non-negative."
        );
    }

    if (n <= 1) {
        return static_cast<unsigned long long>(n);
    }

    /*
     * Stores every previous state.
     *
     * Auxiliary space: O(n)
     */
    vector<unsigned long long> dp(
        static_cast<size_t>(n) + 1
    );

    dp[0] = 0;
    dp[1] = 1;

    for (int index = 2; index <= n; ++index) {
        dp[index] = dp[index - 1] + dp[index - 2];
    }

    return dp[n];
}

unsigned long long fibonacciOptimized(int n) {
    if (n < 0) {
        throw std::invalid_argument(
            "Fibonacci index must be non-negative."
        );
    }

    if (n <= 1) {
        return static_cast<unsigned long long>(n);
    }

    /*
     * Fibonacci only requires the previous two states.
     *
     * Auxiliary space: O(1)
     */
    unsigned long long previousTwo = 0;
    unsigned long long previousOne = 1;

    for (int index = 2; index <= n; ++index) {
        const unsigned long long current =
            previousTwo + previousOne;

        previousTwo = previousOne;
        previousOne = current;
    }

    return previousOne;
}


// ============================================================================
// 13. CASE STUDY REPORT
// ============================================================================

void printCaseStudy() {
    cout << "\n";
    cout << "===============================================================================\n";
    cout << "CASE STUDY: MEMORY-AWARE SENSOR TELEMETRY PROCESSOR\n";
    cout << "===============================================================================\n";

    /*
     * The vector itself is input space.
     *
     * If there are n readings:
     *
     *     Input space = O(n)
     *
     * Algorithms operating on it can have very different auxiliary-space
     * requirements.
     */
    vector<SensorReading> readings = {
        {101, 24.5},
        {102, 28.1},
        {101, 25.0},
        {103, 31.2},
        {102, 27.7},
        {101, 26.4},
        {104, 29.8},
        {103, 30.5}
    };

    validateReadings(readings);

    cout << std::fixed << std::setprecision(2);

    cout << "Number of input readings: "
         << readings.size() << "\n";

    cout << "Maximum temperature: "
         << maximumTemperature(readings) << "\n";

    cout << "Minimum temperature: "
         << minimumTemperature(readings) << "\n";

    cout << "Average temperature: "
         << averageTemperature(readings) << "\n";

    cout << "\nDuplicate sensor IDs using a set: "
         << std::boolalpha
         << hasDuplicateSensors(readings)
         << "\n";

    cout << "Duplicate sensor IDs using brute force: "
         << hasDuplicateSensorsBruteForce(readings)
         << "\n";

    const auto counts = countReadingsBySensor(readings);

    cout << "\nReadings per sensor:\n";

    for (const auto& [sensorId, count] : counts) {
        cout << "  Sensor " << sensorId
             << ": " << count << "\n";
    }

    const SensorSummary summary =
        summarizeSensor(readings, 101);

    cout << "\nSensor 101 summary:\n";
    cout << "  Minimum: " << summary.minimum << "\n";
    cout << "  Maximum: " << summary.maximum << "\n";
    cout << "  Average: " << summary.average << "\n";
    cout << "  Count:   " << summary.readingCount << "\n";

    const vector<double> temperatures = {
        20.0, 22.0, 25.0, 24.0, 30.0, 28.0
    };

    const auto windowAverage =
        maximumWindowAverage(temperatures, 3);

    if (windowAverage.has_value()) {
        cout << "\nMaximum three-reading average: "
             << *windowAverage << "\n";
    }

    cout << "\nMemory-oriented transformation:\n";

    vector<SensorReading> normalized = readings;

    normalizeTemperaturesInPlace(normalized, 20.0);

    cout << "Normalized first reading: "
         << normalized.front().temperature
         << "\n";

    cout << "\nThe case study demonstrates several different memory profiles:\n";
    cout << "  Constant-space scans       -> O(1) auxiliary space\n";
    cout << "  In-place normalization     -> O(1) auxiliary space\n";
    cout << "  Set duplicate detection    -> O(k), worst O(n)\n";
    cout << "  Frequency map              -> O(k), worst O(n)\n";
    cout << "  Recursive factorial        -> O(n) stack space\n";
    cout << "  Sliding window             -> O(1) auxiliary space\n";
    cout << "  Array-based Fibonacci      -> O(n) auxiliary space\n";
    cout << "  Optimized Fibonacci        -> O(1) auxiliary space\n";
}


// ============================================================================
// 14. EDGE CASE TESTS
// ============================================================================

void runEdgeCaseTests() {
    cout << "\n";
    cout << "===============================================================================\n";
    cout << "EDGE CASE TESTS\n";
    cout << "===============================================================================\n";

    vector<SensorReading> empty;

    try {
        maximumTemperature(empty);
        cout << "ERROR: empty input should have failed.\n";
    } catch (const std::invalid_argument& error) {
        cout << "Empty input correctly rejected: "
             << error.what() << "\n";
    }

    vector<SensorReading> single = {
        {500, 42.0}
    };

    cout << "Single reading maximum: "
         << maximumTemperature(single)
         << "\n";

    cout << "Palindrome empty string: "
         << std::boolalpha
         << isPalindrome("")
         << "\n";

    cout << "Palindrome 'level': "
         << isPalindrome("level")
         << "\n";

    cout << "Palindrome 'algorithm': "
         << isPalindrome("algorithm")
         << "\n";

    const auto invalidWindow =
        maximumWindowAverage(
            vector<double>{1.0, 2.0},
            0
        );

    cout << "Invalid window returns no value: "
         << std::boolalpha
         << !invalidWindow.has_value()
         << "\n";
}


// ============================================================================
// 15. SELF-TEST
// ============================================================================

void runSelfTest() {
    cout << "\n";
    cout << "===============================================================================\n";
    cout << "SELF-TEST\n";
    cout << "===============================================================================\n";

    if (factorialIterative(6) != 720) {
        throw std::runtime_error("Iterative factorial test failed.");
    }

    if (factorialRecursive(6) != 720) {
        throw std::runtime_error("Recursive factorial test failed.");
    }

    vector<SensorReading> readings = {
        {1, 10.0},
        {2, 20.0},
        {1, 15.0}
    };

    if (!hasDuplicateSensors(readings)) {
        throw std::runtime_error("Set duplicate test failed.");
    }

    if (!hasDuplicateSensorsBruteForce(readings)) {
        throw std::runtime_error("Brute-force duplicate test failed.");
    }

    if (maximumTemperature(readings) != 20.0) {
        throw std::runtime_error("Maximum test failed.");
    }

    if (minimumTemperature(readings) != 10.0) {
        throw std::runtime_error("Minimum test failed.");
    }

    if (std::abs(averageTemperature(readings) - 15.0) > 1e-9) {
        throw std::runtime_error("Average test failed.");
    }

    if (!isPalindrome("racecar")) {
        throw std::runtime_error("Palindrome test failed.");
    }

    if (isPalindrome("cpp")) {
        throw std::runtime_error("Non-palindrome test failed.");
    }

    if (fibonacciWithArray(10) != 55) {
        throw std::runtime_error("Array Fibonacci test failed.");
    }

    if (fibonacciOptimized(10) != 55) {
        throw std::runtime_error("Optimized Fibonacci test failed.");
    }

    cout << "All self-tests passed.\n";
}


// ============================================================================
// 16. MAIN
// ============================================================================

int main() {
    try {
        cout << "===============================================================================\n";
        cout << "DAY 8 — SPACE COMPLEXITY\n";
        cout << "C++ INDUSTRY-STYLE CASE STUDY\n";
        cout << "===============================================================================\n";

        cout << "\nCore model:\n";
        cout << "  Total space = input space + auxiliary space\n";
        cout << "  Input space and auxiliary space must be analyzed separately.\n";

        printCaseStudy();
        runEdgeCaseTests();

        cout << "\n";
        cout << "===============================================================================\n";
        cout << "IN-PLACE VS COPY-BASED PROCESSING\n";
        cout << "===============================================================================\n";

        vector<SensorReading> original = {
            {1, 21.0},
            {2, 25.0},
            {3, 30.0}
        };

        vector<SensorReading> copied =
            normalizeTemperaturesWithCopy(original, 20.0);

        cout << "Original first temperature: "
             << original.front().temperature << "\n";

        cout << "Copied result first temperature: "
             << copied.front().temperature << "\n";

        normalizeTemperaturesInPlace(original, 20.0);

        cout << "In-place result first temperature: "
             << original.front().temperature << "\n";

        cout << "\n";
        cout << "===============================================================================\n";
        cout << "RECURSION AND SPACE\n";
        cout << "===============================================================================\n";

        cout << "Iterative factorial(8): "
             << factorialIterative(8)
             << "\n";

        cout << "Recursive factorial(8): "
             << factorialRecursive(8)
             << "\n";

        cout << "\n";
        cout << "===============================================================================\n";
        cout << "DYNAMIC PROGRAMMING SPACE OPTIMIZATION\n";
        cout << "===============================================================================\n";

        cout << "Fibonacci array version: "
             << fibonacciWithArray(30)
             << "\n";

        cout << "Fibonacci optimized version: "
             << fibonacciOptimized(30)
             << "\n";

        runSelfTest();

        cout << "\n";
        cout << "===============================================================================\n";
        cout << "CASE STUDY COMPLETE\n";
        cout << "===============================================================================\n";

        return 0;
    }
    catch (const std::exception& error) {
        std::cerr << "Fatal error: "
                  << error.what()
                  << "\n";

        return 1;
    }
}
