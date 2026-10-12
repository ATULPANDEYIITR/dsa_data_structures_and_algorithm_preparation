#include <algorithm>
#include <cstddef>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

/*
 * Case study: an industrial monitoring service must identify the next
 * higher or lower reading without scanning the entire future for each
 * measurement. A monotonic stack gives linear total processing time.
 *
 * Build:
 *   g++ -std=c++17 -O2 monotonic_stack.cpp -o monotonic_stack
 */

struct Reading {
    string sensor;
    int timestamp;
    int value;
};

struct Resolution {
    int sourceIndex;
    int sourceValue;
    optional<int> targetIndex;
    optional<int> targetValue;
};

class MonotonicQueryEngine {
public:
    static vector<optional<int>> nextGreaterRight(
        const vector<int>& values
    ) {
        vector<optional<int>> answer(values.size());
        vector<size_t> unresolved;
        unresolved.reserve(values.size());

        for (size_t i = 0; i < values.size(); ++i) {
            while (!unresolved.empty() &&
                   values[unresolved.back()] < values[i]) {
                answer[unresolved.back()] = values[i];
                unresolved.pop_back();
            }
            unresolved.push_back(i);
        }

        return answer;
    }

    static vector<optional<int>> nextSmallerRight(
        const vector<int>& values
    ) {
        vector<optional<int>> answer(values.size());
        vector<size_t> unresolved;
        unresolved.reserve(values.size());

        for (size_t i = 0; i < values.size(); ++i) {
            while (!unresolved.empty() &&
                   values[unresolved.back()] > values[i]) {
                answer[unresolved.back()] = values[i];
                unresolved.pop_back();
            }
            unresolved.push_back(i);
        }

        return answer;
    }

    static vector<optional<size_t>> nextGreaterIndexRight(
        const vector<int>& values
    ) {
        vector<optional<size_t>> answer(values.size());
        vector<size_t> unresolved;

        for (size_t i = 0; i < values.size(); ++i) {
            while (!unresolved.empty() &&
                   values[unresolved.back()] < values[i]) {
                answer[unresolved.back()] = i;
                unresolved.pop_back();
            }
            unresolved.push_back(i);
        }

        return answer;
    }

    static vector<optional<int>> nextGreaterCircular(
        const vector<int>& values
    ) {
        const size_t n = values.size();
        vector<optional<int>> answer(n);
        vector<size_t> unresolved;

        if (n == 0) {
            return answer;
        }

        for (size_t step = 0; step < 2 * n; ++step) {
            const size_t i = step % n;

            while (!unresolved.empty() &&
                   values[unresolved.back()] < values[i]) {
                answer[unresolved.back()] = values[i];
                unresolved.pop_back();
            }

            // Push each original position only once.
            if (step < n) {
                unresolved.push_back(i);
            }
        }

        return answer;
    }

    static vector<Resolution> analyzeReadings(
        const vector<Reading>& readings,
        bool findGreater
    ) {
        vector<Resolution> output;
        output.reserve(readings.size());
        vector<size_t> unresolved;
        unresolved.reserve(readings.size());

        for (size_t i = 0; i < readings.size(); ++i) {
            const int current = readings[i].value;

            while (!unresolved.empty()) {
                const size_t previousIndex = unresolved.back();
                const int previous = readings[previousIndex].value;

                const bool resolves = findGreater
                    ? previous < current
                    : previous > current;

                if (!resolves) {
                    break;
                }

                output.push_back({
                    static_cast<int>(previousIndex),
                    previous,
                    static_cast<int>(i),
                    current
                });

                unresolved.pop_back();
            }

            unresolved.push_back(i);
        }

        // Unresolved readings have no qualifying future reading.
        while (!unresolved.empty()) {
            const size_t i = unresolved.back();
            unresolved.pop_back();

            output.push_back({
                static_cast<int>(i),
                readings[i].value,
                nullopt,
                nullopt
            });
        }

        sort(output.begin(), output.end(),
             [](const Resolution& a, const Resolution& b) {
                 return a.sourceIndex < b.sourceIndex;
             });

        return output;
    }
};

static void printOptionalValues(
    const string& label,
    const vector<optional<int>>& values
) {
    cout << label << ": ";
    for (size_t i = 0; i < values.size(); ++i) {
        if (i > 0) {
            cout << ", ";
        }

        if (values[i].has_value()) {
            cout << *values[i];
        } else {
            cout << "none";
        }
    }
    cout << '\n';
}

static void printResolutions(
    const vector<Resolution>& resolutions,
    const vector<Reading>& readings,
    const string& title
) {
    cout << "\n" << title << '\n';

    for (const auto& resolution : resolutions) {
        const Reading& source = readings.at(
            static_cast<size_t>(resolution.sourceIndex)
        );

        cout << source.sensor
             << " at t=" << source.timestamp
             << ", value=" << resolution.sourceValue;

        if (resolution.targetIndex.has_value()) {
            const Reading& target = readings.at(
                static_cast<size_t>(*resolution.targetIndex)
            );

            cout << " -> next qualifying reading at t="
                 << target.timestamp
                 << ", value=" << *resolution.targetValue;
        } else {
            cout << " -> no qualifying future reading";
        }

        cout << '\n';
    }
}

static void require(bool condition, const string& message) {
    if (!condition) {
        throw runtime_error("Test failed: " + message);
    }
}

int main() {
    try {
        const vector<int> measurements = {42, 38, 38, 51, 45, 60, 33};

        cout << "Industrial sensor reading analysis\n";
        cout << "Readings: ";
        for (int value : measurements) {
            cout << value << ' ';
        }
        cout << '\n';

        printOptionalValues(
            "Next greater",
            MonotonicQueryEngine::nextGreaterRight(measurements)
        );
        printOptionalValues(
            "Next smaller",
            MonotonicQueryEngine::nextSmallerRight(measurements)
        );
        printOptionalValues(
            "Circular next greater",
            MonotonicQueryEngine::nextGreaterCircular(measurements)
        );

        vector<Reading> pressureReadings = {
            {"compressor-A", 100, 42},
            {"compressor-A", 105, 38},
            {"compressor-A", 110, 51},
            {"compressor-A", 115, 45},
            {"compressor-A", 120, 60},
            {"compressor-A", 125, 33}
        };

        printResolutions(
            MonotonicQueryEngine::analyzeReadings(
                pressureReadings, true
            ),
            pressureReadings,
            "Next-greater pressure events"
        );

        printResolutions(
            MonotonicQueryEngine::analyzeReadings(
                pressureReadings, false
            ),
            pressureReadings,
            "Next-smaller pressure events"
        );

        require(
            MonotonicQueryEngine::nextGreaterRight({2, 1, 3}) ==
                vector<optional<int>>({3, 3, nullopt}),
            "next greater"
        );

        require(
            MonotonicQueryEngine::nextSmallerRight({2, 3, 1}) ==
                vector<optional<int>>({1, 1, nullopt}),
            "next smaller"
        );

        require(
            MonotonicQueryEngine::nextGreaterRight({5, 5, 5}) ==
                vector<optional<int>>({nullopt, nullopt, nullopt}),
            "strict duplicate handling"
        );

        require(
            MonotonicQueryEngine::nextGreaterCircular({1, 2, 1}) ==
                vector<optional<int>>({2, nullopt, 2}),
            "circular lookup"
        );

        require(
            MonotonicQueryEngine::nextGreaterRight({}).empty(),
            "empty input"
        );

        cout << "\nAll C++ tests passed.\n";
    } catch (const exception& error) {
        cerr << "Execution failed: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
