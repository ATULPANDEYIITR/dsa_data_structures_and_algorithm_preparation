/*
 * Day 25 — String Sliding Window
 *
 * C++17 case study:
 * High-volume security-event sequence analysis
 *
 * The program demonstrates:
 * - Sliding-window fundamentals
 * - Longest substring without repetition
 * - Frequency maps
 * - At-most-K distinct characters
 * - Exactly-K distinct counting
 * - Minimum-window substring
 * - Fixed-size windows
 * - Frequency-constrained windows
 * - Validation and failure handling
 * - Structured event processing
 * - Complexity and architectural trade-offs
 *
 * Compile:
 *     g++ -std=c++17 -O2 -Wall -Wextra -pedantic day25.cpp -o day25
 */

#include <algorithm>
#include <cstddef>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;


// ============================================================================
// 1. DOMAIN MODEL
// ============================================================================

struct SecurityEvent {
    string userId;
    string action;
    long long timestamp;
};

struct StringWindowResult {
    size_t length{};
    string substring;
};

struct EventWindowResult {
    size_t start{};
    size_t length{};
};


// ============================================================================
// 2. UTILITY FUNCTIONS
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


// ============================================================================
// 3. FIXED-SIZE STRING WINDOW
// ============================================================================

vector<string> fixedSizeWindows(const string& text, size_t windowSize) {
    if (windowSize == 0) {
        throw invalid_argument("Window size must be greater than zero.");
    }

    vector<string> result;

    if (windowSize > text.size()) {
        return result;
    }

    for (size_t start = 0;
         start + windowSize <= text.size();
         ++start) {
        result.push_back(
            text.substr(start, windowSize)
        );
    }

    return result;
}


// ============================================================================
// 4. LONGEST SUBSTRING WITHOUT REPETITION
// ============================================================================

StringWindowResult longestUniqueSubstring(const string& text) {
    /*
     * For ordinary ASCII/UTF-8 byte-oriented processing, unordered_map
     * operates on bytes when indexing std::string.
     *
     * This implementation therefore treats the input as a sequence of
     * bytes. That is appropriate for ASCII protocol tokens and many
     * machine-generated security identifiers.
     *
     * A full Unicode implementation would require decoding UTF-8 into
     * Unicode code points before applying the same algorithm.
     */

    unordered_map<unsigned char, size_t> lastSeen;

    size_t left = 0;
    size_t bestStart = 0;
    size_t bestLength = 0;

    for (size_t right = 0; right < text.size(); ++right) {
        unsigned char character =
            static_cast<unsigned char>(text[right]);

        auto it = lastSeen.find(character);

        if (it != lastSeen.end()) {
            /*
             * The previous occurrence may be outside the current window.
             * max() ensures left never moves backward.
             */
            left = max(left, it->second + 1);
        }

        lastSeen[character] = right;

        const size_t currentLength = right - left + 1;

        if (currentLength > bestLength) {
            bestLength = currentLength;
            bestStart = left;
        }
    }

    return {
        bestLength,
        text.substr(bestStart, bestLength)
    };
}


// ============================================================================
// 5. FREQUENCY MAP
// ============================================================================

unordered_map<char, int> frequencyMap(const string& text) {
    unordered_map<char, int> frequencies;

    for (char character : text) {
        ++frequencies[character];
    }

    return frequencies;
}

void printFrequencyMap(
    const unordered_map<char, int>& frequencies
) {
    vector<pair<char, int>> sorted(
        frequencies.begin(),
        frequencies.end()
    );

    sort(
        sorted.begin(),
        sorted.end(),
        [](const auto& left, const auto& right) {
            return left.first < right.first;
        }
    );

    for (const auto& [character, count] : sorted) {
        cout << "'" << character << "'=" << count << " ";
    }

    cout << "\n";
}


// ============================================================================
// 6. LONGEST SUBSTRING WITH AT MOST K DISTINCT
// ============================================================================

StringWindowResult longestAtMostKDistinct(
    const string& text,
    size_t k
) {
    if (k == 0 || text.empty()) {
        return {};
    }

    unordered_map<char, size_t> frequencies;

    size_t left = 0;
    size_t distinct = 0;

    size_t bestStart = 0;
    size_t bestLength = 0;

    for (size_t right = 0; right < text.size(); ++right) {
        const char incoming = text[right];

        auto [it, inserted] = frequencies.emplace(incoming, 0);

        if (inserted) {
            ++distinct;
        }

        ++it->second;

        while (distinct > k) {
            const char outgoing = text[left];

            auto frequencyIt = frequencies.find(outgoing);

            if (frequencyIt == frequencies.end()) {
                throw logic_error(
                    "Window-frequency invariant violated."
                );
            }

            --frequencyIt->second;

            if (frequencyIt->second == 0) {
                frequencies.erase(frequencyIt);
                --distinct;
            }

            ++left;
        }

        const size_t currentLength = right - left + 1;

        if (currentLength > bestLength) {
            bestLength = currentLength;
            bestStart = left;
        }
    }

    return {
        bestLength,
        text.substr(bestStart, bestLength)
    };
}


// ============================================================================
// 7. COUNT SUBSTRINGS WITH AT MOST K DISTINCT
// ============================================================================

long long countAtMostKDistinct(
    const string& text,
    size_t k
) {
    if (k == 0 || text.empty()) {
        return 0;
    }

    unordered_map<char, size_t> frequencies;

    size_t left = 0;
    size_t distinct = 0;

    long long result = 0;

    for (size_t right = 0; right < text.size(); ++right) {
        const char incoming = text[right];

        auto [it, inserted] = frequencies.emplace(incoming, 0);

        if (inserted) {
            ++distinct;
        }

        ++it->second;

        while (distinct > k) {
            const char outgoing = text[left];
            auto frequencyIt = frequencies.find(outgoing);

            --frequencyIt->second;

            if (frequencyIt->second == 0) {
                frequencies.erase(frequencyIt);
                --distinct;
            }

            ++left;
        }

        /*
         * Every substring beginning at:
         *
         *     left, left + 1, ..., right
         *
         * is valid for this right boundary.
         *
         * Therefore:
         *     number of new valid substrings = right - left + 1
         */
        result += static_cast<long long>(right - left + 1);
    }

    return result;
}


// ============================================================================
// 8. EXACTLY K DISTINCT
// ============================================================================

long long countExactlyKDistinct(
    const string& text,
    size_t k
) {
    if (k == 0) {
        return 0;
    }

    return (
        countAtMostKDistinct(text, k)
        - countAtMostKDistinct(text, k - 1)
    );
}


// ============================================================================
// 9. MINIMUM WINDOW SUBSTRING
// ============================================================================

string minimumWindow(
    const string& text,
    const string& target
) {
    if (text.empty() || target.empty()) {
        return "";
    }

    if (target.size() > text.size()) {
        return "";
    }

    unordered_map<char, size_t> required;
    unordered_map<char, size_t> window;

    for (char character : target) {
        ++required[character];
    }

    const size_t requiredKinds = required.size();

    size_t satisfiedKinds = 0;
    size_t left = 0;

    size_t bestStart = 0;
    size_t bestLength = numeric_limits<size_t>::max();

    for (size_t right = 0; right < text.size(); ++right) {
        const char incoming = text[right];

        ++window[incoming];

        auto requiredIt = required.find(incoming);

        if (
            requiredIt != required.end()
            && window[incoming] == requiredIt->second
        ) {
            ++satisfiedKinds;
        }

        /*
         * Once all requirements are satisfied, contract the window.
         * This is the central difference from a longest-window problem.
         */
        while (satisfiedKinds == requiredKinds) {
            const size_t currentLength = right - left + 1;

            if (currentLength < bestLength) {
                bestLength = currentLength;
                bestStart = left;
            }

            const char outgoing = text[left];

            auto windowIt = window.find(outgoing);

            if (windowIt == window.end()) {
                throw logic_error(
                    "Minimum-window frequency invariant violated."
                );
            }

            --windowIt->second;

            auto requiredOutgoing = required.find(outgoing);

            if (
                requiredOutgoing != required.end()
                && windowIt->second < requiredOutgoing->second
            ) {
                --satisfiedKinds;
            }

            if (windowIt->second == 0) {
                window.erase(windowIt);
            }

            ++left;
        }
    }

    if (bestLength == numeric_limits<size_t>::max()) {
        return "";
    }

    return text.substr(bestStart, bestLength);
}


// ============================================================================
// 10. LONGEST REPEATING CHARACTER REPLACEMENT
// ============================================================================

StringWindowResult longestRepeatingReplacement(
    const string& text,
    size_t k
) {
    unordered_map<char, size_t> frequencies;

    size_t left = 0;
    size_t highestFrequency = 0;

    size_t bestStart = 0;
    size_t bestLength = 0;

    for (size_t right = 0; right < text.size(); ++right) {
        const char character = text[right];

        const size_t newFrequency =
            ++frequencies[character];

        highestFrequency =
            max(highestFrequency, newFrequency);

        /*
         * To turn the entire window into one repeated character,
         * all characters except the most frequent one need replacement.
         */
        while (
            (right - left + 1) - highestFrequency > k
        ) {
            --frequencies[text[left]];
            ++left;
        }

        const size_t currentLength = right - left + 1;

        if (currentLength > bestLength) {
            bestLength = currentLength;
            bestStart = left;
        }
    }

    return {
        bestLength,
        text.substr(bestStart, bestLength)
    };
}


// ============================================================================
// 11. STRUCTURED SECURITY EVENT WINDOW
// ============================================================================

class SecurityEventAnalyzer {
public:
    explicit SecurityEventAnalyzer(
        vector<SecurityEvent> events
    )
        : events_(move(events)) {}

    EventWindowResult longestUniqueActionSequence() const {
        /*
         * This is the same invariant as longest unique substring, but each
         * item is a structured event and the uniqueness key is event.action.
         *
         * This demonstrates why sliding windows are a general algorithmic
         * pattern rather than a string-specific trick.
         */

        unordered_map<string, size_t> lastSeen;

        size_t left = 0;
        size_t bestStart = 0;
        size_t bestLength = 0;

        for (size_t right = 0; right < events_.size(); ++right) {
            const string& action = events_[right].action;

            auto it = lastSeen.find(action);

            if (it != lastSeen.end()) {
                left = max(left, it->second + 1);
            }

            lastSeen[action] = right;

            const size_t currentLength = right - left + 1;

            if (currentLength > bestLength) {
                bestLength = currentLength;
                bestStart = left;
            }
        }

        return {
            bestStart,
            bestLength
        };
    }

    vector<SecurityEvent> getWindow(
        const EventWindowResult& result
    ) const {
        if (
            result.start > events_.size()
            || result.length > events_.size() - result.start
        ) {
            throw out_of_range(
                "Requested event window is outside the event collection."
            );
        }

        return vector<SecurityEvent>(
            events_.begin() + static_cast<ptrdiff_t>(result.start),
            events_.begin()
                + static_cast<ptrdiff_t>(
                    result.start + result.length
                )
        );
    }

private:
    vector<SecurityEvent> events_;
};


// ============================================================================
// 12. EVENT RATE WINDOW
// ============================================================================

size_t maximumEventsInTimeWindow(
    const vector<long long>& timestamps,
    long long windowDuration
) {
    if (windowDuration < 0) {
        throw invalid_argument(
            "Window duration cannot be negative."
        );
    }

    if (timestamps.empty()) {
        return 0;
    }

    /*
     * This function assumes timestamps are sorted in ascending order.
     *
     * A production implementation receiving unsorted timestamps would need
     * to sort them first, which changes the total complexity to O(n log n).
     *
     * With sorted timestamps, the two-pointer scan is O(n).
     */

    for (size_t i = 1; i < timestamps.size(); ++i) {
        if (timestamps[i] < timestamps[i - 1]) {
            throw invalid_argument(
                "Timestamps must be sorted in ascending order."
            );
        }
    }

    size_t left = 0;
    size_t best = 0;

    for (size_t right = 0; right < timestamps.size(); ++right) {
        while (
            timestamps[right] - timestamps[left]
            > windowDuration
        ) {
            ++left;
        }

        best = max(best, right - left + 1);
    }

    return best;
}


// ============================================================================
// 13. TESTS
// ============================================================================

void assertEqual(
    size_t actual,
    size_t expected,
    const string& description
) {
    if (actual != expected) {
        throw runtime_error(
            description
            + ": expected "
            + to_string(expected)
            + ", got "
            + to_string(actual)
        );
    }
}

void assertEqual(
    long long actual,
    long long expected,
    const string& description
) {
    if (actual != expected) {
        throw runtime_error(
            description
            + ": expected "
            + to_string(expected)
            + ", got "
            + to_string(actual)
        );
    }
}

void assertEqual(
    const string& actual,
    const string& expected,
    const string& description
) {
    if (actual != expected) {
        throw runtime_error(
            description
            + ": expected "
            + expected
            + ", got "
            + actual
        );
    }
}

void runTests() {
    printSection("Automated Tests");

    assertEqual(
        longestUniqueSubstring("").length,
        static_cast<size_t>(0),
        "Empty unique substring"
    );

    assertEqual(
        longestUniqueSubstring("abcabcbb").length,
        static_cast<size_t>(3),
        "abcabcbb"
    );

    assertEqual(
        longestUniqueSubstring("bbbbb").length,
        static_cast<size_t>(1),
        "bbbbb"
    );

    assertEqual(
        longestUniqueSubstring("pwwkew").length,
        static_cast<size_t>(3),
        "pwwkew"
    );

    assertEqual(
        longestUniqueSubstring("abba").length,
        static_cast<size_t>(2),
        "abba"
    );

    assertEqual(
        longestAtMostKDistinct("eceba", 2).length,
        static_cast<size_t>(3),
        "At most two distinct"
    );

    assertEqual(
        countExactlyKDistinct("pqpqs", 2),
        7LL,
        "Exactly two distinct"
    );

    assertEqual(
        minimumWindow("ADOBECODEBANC", "ABC"),
        "BANC",
        "Minimum window"
    );

    assertEqual(
        minimumWindow("a", "aa"),
        "",
        "Impossible minimum window"
    );

    assertEqual(
        longestRepeatingReplacement("AABABBA", 1).length,
        static_cast<size_t>(4),
        "Replacement window"
    );

    assertEqual(
        maximumEventsInTimeWindow(
            {1, 2, 3, 8, 9, 10},
            2
        ),
        static_cast<size_t>(3),
        "Time-based event window"
    );

    cout << "All C++ tests passed.\n";
}


// ============================================================================
// 14. MAIN CASE STUDY
// ============================================================================

int main() {
    try {
        printSection(
            "Day 25 — String Sliding Window: Security Event Analysis"
        );

        printSubsection("1. Fixed-Size Windows");

        const string text = "ABCDE";

        const auto windows = fixedSizeWindows(text, 3);

        for (const string& window : windows) {
            cout << window << "\n";
        }

        printSubsection("2. Longest Unique Substring");

        const vector<string> uniqueExamples = {
            "",
            "a",
            "abcabcbb",
            "bbbbb",
            "pwwkew",
            "dvdf",
            "abba",
            "abcdef"
        };

        for (const string& example : uniqueExamples) {
            const auto result =
                longestUniqueSubstring(example);

            cout << quoted(example)
                 << " -> "
                 << quoted(result.substring)
                 << ", length="
                 << result.length
                 << "\n";
        }

        printSubsection("3. Frequency Map");

        const auto frequencies =
            frequencyMap("aabccbb");

        printFrequencyMap(frequencies);

        printSubsection("4. At-Most-K Distinct");

        for (const auto& [input, k] : vector<pair<string, size_t>>{
            {"eceba", 2},
            {"aa", 1},
            {"aabbcc", 2},
            {"abcadcacacaca", 2}
        }) {
            const auto result =
                longestAtMostKDistinct(input, k);

            cout << quoted(input)
                 << ", k="
                 << k
                 << " -> "
                 << quoted(result.substring)
                 << ", length="
                 << result.length
                 << "\n";
        }

        printSubsection("5. Exactly-K Distinct Counting");

        for (const auto& [input, k] : vector<pair<string, size_t>>{
            {"pqpqs", 2},
            {"a", 1},
            {"abc", 2},
            {"aabbcc", 2}
        }) {
            cout << quoted(input)
                 << ", k="
                 << k
                 << " -> count="
                 << countExactlyKDistinct(input, k)
                 << "\n";
        }

        printSubsection("6. Minimum Window");

        for (const auto& [input, target] :
             vector<pair<string, string>>{
                 {"ADOBECODEBANC", "ABC"},
                 {"a", "a"},
                 {"a", "aa"},
                 {"aa", "aa"},
                 {"abc", "xyz"}
             }) {
            cout << "text="
                 << quoted(input)
                 << ", target="
                 << quoted(target)
                 << " -> "
                 << quoted(minimumWindow(input, target))
                 << "\n";
        }

        printSubsection("7. Frequency-Constrained Replacement");

        for (const auto& [input, k] :
             vector<pair<string, size_t>>{
                 {"AABABBA", 1},
                 {"ABAB", 2},
                 {"AAAA", 0},
                 {"ABCDE", 1}
             }) {
            const auto result =
                longestRepeatingReplacement(input, k);

            cout << quoted(input)
                 << ", k="
                 << k
                 << " -> "
                 << quoted(result.substring)
                 << ", length="
                 << result.length
                 << "\n";
        }

        printSubsection(
            "8. Security-Event Case Study"
        );

        vector<SecurityEvent> events = {
            {"U100", "LOGIN", 100},
            {"U100", "SEARCH", 101},
            {"U100", "VIEW", 102},
            {"U100", "DOWNLOAD", 103},
            {"U100", "SEARCH", 104},
            {"U100", "CHECKOUT", 105},
            {"U100", "PAYMENT", 106},
            {"U100", "LOGOUT", 107}
        };

        SecurityEventAnalyzer analyzer(events);

        const EventWindowResult result =
            analyzer.longestUniqueActionSequence();

        cout << "Longest sequence with unique actions:\n";

        const auto selectedEvents =
            analyzer.getWindow(result);

        for (const auto& event : selectedEvents) {
            cout << "user="
                 << event.userId
                 << ", action="
                 << event.action
                 << ", timestamp="
                 << event.timestamp
                 << "\n";
        }

        printSubsection(
            "9. Time-Based Sliding Window"
        );

        const vector<long long> timestamps = {
            100, 101, 102, 105, 106, 110, 111, 112
        };

        const size_t maximumEvents =
            maximumEventsInTimeWindow(
                timestamps,
                2
            );

        cout << "Maximum events inside any two-time-unit window: "
             << maximumEvents
             << "\n";

        printSubsection(
            "10. Design and Performance Characteristics"
        );

        cout << "Variable-window scans normally process each element "
                "with a bounded number of pointer movements.\n";

        cout << "For n input elements, the typical time complexity is O(n), "
                "provided frequency-map operations are average O(1).\n";

        cout << "The main extra memory cost is the active frequency or "
                "last-seen map, normally O(number of distinct keys).\n";

        cout << "For production security analytics, the input ordering, "
                "encoding, timestamp semantics, memory limits, and "
                "concurrency model must be explicitly defined.\n";

        runTests();

        printSection("Case Study Validation Complete");

        cout << "The program completed successfully.\n";
    }
    catch (const exception& error) {
        cerr << "ERROR: "
             << error.what()
             << "\n";

        return 1;
    }

    return 0;
}
