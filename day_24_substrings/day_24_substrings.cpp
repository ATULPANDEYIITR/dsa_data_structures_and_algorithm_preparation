/*
 * Day 24 — Substrings
 *
 * Industry-style C++ case study:
 * A high-volume log-search and text-analysis engine.
 *
 * The program demonstrates:
 *   - substring generation
 *   - contiguous versus non-contiguous sequences
 *   - brute-force string search
 *   - KMP string search
 *   - rolling-hash search
 *   - overlapping occurrence counting
 *   - sliding-window substring analysis
 *   - longest palindromic substring
 *   - longest common substring
 *   - validation and error handling
 *   - complexity and architectural trade-offs
 *
 * Compile:
 *   g++ -std=c++17 -O2 -Wall -Wextra -pedantic day24_substrings.cpp -o day24
 */

#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

// ============================================================================
// Utility
// ============================================================================

void requireNonEmptyPattern(const string& pattern) {
    if (pattern.empty()) {
        throw invalid_argument("Search pattern must not be empty.");
    }
}

// ============================================================================
// Substring generation
// ============================================================================

vector<string> generateSubstrings(const string& text) {
    vector<string> result;

    // There are n(n+1)/2 non-empty substring occurrences.
    const size_t expected =
        text.size() * (text.size() + 1) / 2;

    result.reserve(expected);

    for (size_t start = 0; start < text.size(); ++start) {
        for (size_t length = 1;
             start + length <= text.size();
             ++length) {
            result.push_back(text.substr(start, length));
        }
    }

    return result;
}

unordered_set<string> generateDistinctSubstrings(const string& text) {
    unordered_set<string> result;

    for (size_t start = 0; start < text.size(); ++start) {
        for (size_t length = 1;
             start + length <= text.size();
             ++length) {
            result.insert(text.substr(start, length));
        }
    }

    return result;
}

size_t countAllSubstrings(const string& text) {
    const size_t n = text.size();
    return n * (n + 1) / 2;
}

// ============================================================================
// Substring versus subsequence
// ============================================================================

bool isSubstring(const string& text, const string& candidate) {
    return text.find(candidate) != string::npos;
}

bool isSubsequence(const string& text, const string& candidate) {
    size_t candidateIndex = 0;

    for (char character : text) {
        if (
            candidateIndex < candidate.size() &&
            character == candidate[candidateIndex]
        ) {
            ++candidateIndex;
        }
    }

    return candidateIndex == candidate.size();
}

// ============================================================================
// Brute-force string search
// ============================================================================

int bruteForceSearch(
    const string& text,
    const string& pattern
) {
    requireNonEmptyPattern(pattern);

    if (pattern.size() > text.size()) {
        return -1;
    }

    for (size_t start = 0;
         start + pattern.size() <= text.size();
         ++start) {

        bool matched = true;

        for (size_t offset = 0;
             offset < pattern.size();
             ++offset) {

            if (text[start + offset] != pattern[offset]) {
                matched = false;
                break;
            }
        }

        if (matched) {
            return static_cast<int>(start);
        }
    }

    return -1;
}

// ============================================================================
// KMP prefix function
// ============================================================================

vector<int> buildLPS(const string& pattern) {
    vector<int> lps(pattern.size(), 0);

    int length = 0;

    for (size_t index = 1;
         index < pattern.size();) {

        if (pattern[index] == pattern[length]) {
            ++length;
            lps[index] = length;
            ++index;
        } else if (length > 0) {
            length = lps[length - 1];
        } else {
            lps[index] = 0;
            ++index;
        }
    }

    return lps;
}

int kmpSearch(
    const string& text,
    const string& pattern
) {
    requireNonEmptyPattern(pattern);

    if (pattern.size() > text.size()) {
        return -1;
    }

    const vector<int> lps = buildLPS(pattern);

    size_t textIndex = 0;
    size_t patternIndex = 0;

    while (textIndex < text.size()) {
        if (text[textIndex] == pattern[patternIndex]) {
            ++textIndex;
            ++patternIndex;

            if (patternIndex == pattern.size()) {
                return static_cast<int>(
                    textIndex - patternIndex
                );
            }
        } else if (patternIndex > 0) {
            patternIndex = lps[patternIndex - 1];
        } else {
            ++textIndex;
        }
    }

    return -1;
}

vector<int> kmpSearchAll(
    const string& text,
    const string& pattern
) {
    requireNonEmptyPattern(pattern);

    vector<int> positions;

    if (pattern.size() > text.size()) {
        return positions;
    }

    const vector<int> lps = buildLPS(pattern);

    size_t textIndex = 0;
    size_t patternIndex = 0;

    while (textIndex < text.size()) {
        if (text[textIndex] == pattern[patternIndex]) {
            ++textIndex;
            ++patternIndex;

            if (patternIndex == pattern.size()) {
                positions.push_back(
                    static_cast<int>(
                        textIndex - patternIndex
                    )
                );

                // Falling back instead of resetting to zero preserves
                // overlapping matches.
                patternIndex = lps[patternIndex - 1];
            }
        } else if (patternIndex > 0) {
            patternIndex = lps[patternIndex - 1];
        } else {
            ++textIndex;
        }
    }

    return positions;
}

// ============================================================================
// Rabin-Karp rolling hash
// ============================================================================

class RollingHash {
private:
    static constexpr uint64_t BASE = 257;
    static constexpr uint64_t MOD = 1000000007ULL;

public:
    static int search(
        const string& text,
        const string& pattern
    ) {
        requireNonEmptyPattern(pattern);

        if (pattern.size() > text.size()) {
            return -1;
        }

        const size_t m = pattern.size();

        uint64_t patternHash = 0;
        uint64_t windowHash = 0;
        uint64_t highestPower = 1;

        for (size_t i = 0; i < m - 1; ++i) {
            highestPower =
                (highestPower * BASE) % MOD;
        }

        for (size_t i = 0; i < m; ++i) {
            patternHash =
                (patternHash * BASE +
                 static_cast<unsigned char>(pattern[i])) % MOD;

            windowHash =
                (windowHash * BASE +
                 static_cast<unsigned char>(text[i])) % MOD;
        }

        for (size_t start = 0;
             start + m <= text.size();
             ++start) {

            if (patternHash == windowHash) {
                // Hash equality is only a candidate match.
                // Exact verification eliminates collision errors.
                if (text.compare(start, m, pattern) == 0) {
                    return static_cast<int>(start);
                }
            }

            if (start + m < text.size()) {
                const uint64_t outgoing =
                    static_cast<unsigned char>(text[start]);

                windowHash =
                    (windowHash +
                     MOD -
                     (outgoing * highestPower) % MOD) % MOD;

                windowHash =
                    (windowHash * BASE +
                     static_cast<unsigned char>(
                         text[start + m]
                     )) % MOD;
            }
        }

        return -1;
    }
};

// ============================================================================
// Overlapping occurrences
// ============================================================================

int countOverlappingOccurrences(
    const string& text,
    const string& pattern
) {
    requireNonEmptyPattern(pattern);

    int count = 0;

    for (size_t start = 0;
         start + pattern.size() <= text.size();
         ++start) {

        if (text.compare(start, pattern.size(), pattern) == 0) {
            ++count;
        }
    }

    return count;
}

// ============================================================================
// Longest unique substring
// ============================================================================

string longestUniqueSubstring(const string& text) {
    unordered_map<char, size_t> lastSeen;

    size_t left = 0;
    size_t bestStart = 0;
    size_t bestLength = 0;

    for (size_t right = 0;
         right < text.size();
         ++right) {

        const char character = text[right];

        auto iterator = lastSeen.find(character);

        if (
            iterator != lastSeen.end() &&
            iterator->second >= left
        ) {
            left = iterator->second + 1;
        }

        lastSeen[character] = right;

        const size_t currentLength =
            right - left + 1;

        if (currentLength > bestLength) {
            bestLength = currentLength;
            bestStart = left;
        }
    }

    return text.substr(bestStart, bestLength);
}

// ============================================================================
// Longest palindromic substring
// ============================================================================

pair<size_t, size_t> expandAroundCenter(
    const string& text,
    int left,
    int right
) {
    while (
        left >= 0 &&
        right < static_cast<int>(text.size()) &&
        text[left] == text[right]
    ) {
        --left;
        ++right;
    }

    const size_t start =
        static_cast<size_t>(left + 1);

    const size_t length =
        static_cast<size_t>(right - left - 1);

    return {start, length};
}

string longestPalindromicSubstring(
    const string& text
) {
    if (text.empty()) {
        return "";
    }

    size_t bestStart = 0;
    size_t bestLength = 1;

    for (int center = 0;
         center < static_cast<int>(text.size());
         ++center) {

        const auto odd =
            expandAroundCenter(
                text,
                center,
                center
            );

        if (odd.second > bestLength) {
            bestStart = odd.first;
            bestLength = odd.second;
        }

        const auto even =
            expandAroundCenter(
                text,
                center,
                center + 1
            );

        if (even.second > bestLength) {
            bestStart = even.first;
            bestLength = even.second;
        }
    }

    return text.substr(bestStart, bestLength);
}

// ============================================================================
// Longest common substring
// ============================================================================

string longestCommonSubstring(
    const string& first,
    const string& second
) {
    /*
     * dp[j] represents the length of the common suffix ending at the
     * current characters of first and second.
     *
     * Space optimization reduces O(nm) memory to O(m).
     */
    vector<size_t> previous(second.size() + 1, 0);
    vector<size_t> current(second.size() + 1, 0);

    size_t bestLength = 0;
    size_t bestEnd = 0;

    for (size_t i = 1; i <= first.size(); ++i) {
        fill(current.begin(), current.end(), 0);

        for (size_t j = 1; j <= second.size(); ++j) {
            if (first[i - 1] == second[j - 1]) {
                current[j] =
                    previous[j - 1] + 1;

                if (current[j] > bestLength) {
                    bestLength = current[j];
                    bestEnd = i;
                }
            }
        }

        swap(previous, current);
    }

    return first.substr(
        bestEnd - bestLength,
        bestLength
    );
}

// ============================================================================
// Log record
// ============================================================================

struct LogRecord {
    int id;
    string severity;
    string service;
    string message;
};

// ============================================================================
// Industry-style substring search engine
// ============================================================================

class LogSearchEngine {
private:
    vector<LogRecord> records;

public:
    explicit LogSearchEngine(
        vector<LogRecord> recordsInput
    )
        : records(std::move(recordsInput)) {}

    vector<LogRecord> searchBruteForce(
        const string& pattern
    ) const {
        requireNonEmptyPattern(pattern);

        vector<LogRecord> matches;

        for (const auto& record : records) {
            if (bruteForceSearch(
                    record.message,
                    pattern
                ) != -1) {

                matches.push_back(record);
            }
        }

        return matches;
    }

    vector<LogRecord> searchKMP(
        const string& pattern
    ) const {
        requireNonEmptyPattern(pattern);

        vector<LogRecord> matches;

        for (const auto& record : records) {
            if (kmpSearch(
                    record.message,
                    pattern
                ) != -1) {

                matches.push_back(record);
            }
        }

        return matches;
    }

    map<string, int> countBySeverity(
        const string& pattern
    ) const {
        requireNonEmptyPattern(pattern);

        map<string, int> counts;

        for (const auto& record : records) {
            const int occurrences =
                countOverlappingOccurrences(
                    record.message,
                    pattern
                );

            counts[record.severity] += occurrences;
        }

        return counts;
    }

    vector<int> exactMatchPositions(
        const string& message,
        const string& pattern
    ) const {
        return kmpSearchAll(message, pattern);
    }
};

// ============================================================================
// Display helpers
// ============================================================================

void printRecords(
    const vector<LogRecord>& records
) {
    for (const auto& record : records) {
        cout
            << "  #" << record.id
            << " [" << record.severity << "] "
            << record.service
            << ": " << record.message
            << '\n';
    }
}

void printVector(
    const vector<int>& values
) {
    cout << "[";

    for (size_t i = 0; i < values.size(); ++i) {
        if (i > 0) {
            cout << ", ";
        }

        cout << values[i];
    }

    cout << "]";
}

// ============================================================================
// Validation tests
// ============================================================================

void runTests() {
    assert(countAllSubstrings("abc") == 6);

    assert(isSubstring("abcdef", "bcd"));
    assert(isSubsequence("abcdef", "ace"));
    assert(!isSubsequence("abcdef", "aec"));

    assert(
        bruteForceSearch(
            "hello world",
            "world"
        ) == 6
    );

    assert(
        kmpSearch(
            "ABABDABACDABABCABAB",
            "ABABCABAB"
        ) == 10
    );

    const vector<int> expected = {0, 1, 2};

    assert(
        kmpSearchAll("aaaa", "aa") ==
        expected
    );

    assert(
        RollingHash::search(
            "hello world",
            "world"
        ) == 6
    );

    assert(
        countOverlappingOccurrences(
            "aaaa",
            "aa"
        ) == 3
    );

    assert(
        longestUniqueSubstring(
            "abcabcbb"
        ) == "abc"
    );

    assert(
        longestPalindromicSubstring(
            "babad"
        ) == "bab" ||
        longestPalindromicSubstring(
            "babad"
        ) == "aba"
    );

    assert(
        longestCommonSubstring(
            "ABABC",
            "BABCA"
        ) == "BABC"
    );
}

// ============================================================================
// Main case study
// ============================================================================

int main() {
    try {
        cout << string(78, '=') << '\n';
        cout << "DAY 24 — SUBSTRINGS: C++ LOG SEARCH CASE STUDY\n";
        cout << string(78, '=') << "\n\n";

        // --------------------------------------------------------------------
        // Stage 1: Fundamental substring properties
        // --------------------------------------------------------------------

        const string sample = "banana";

        cout << "1. Fundamental substring analysis\n";
        cout << "Text: " << sample << '\n';
        cout
            << "Total substring occurrences: "
            << countAllSubstrings(sample)
            << '\n';

        const auto distinct =
            generateDistinctSubstrings(sample);

        cout
            << "Distinct substring values: "
            << distinct.size()
            << "\n\n";

        // --------------------------------------------------------------------
        // Stage 2: Contiguous versus non-contiguous
        // --------------------------------------------------------------------

        cout << "2. Contiguous versus non-contiguous\n";

        for (const string& candidate :
             {"ABC", "ACE", "AEC", "BCD"}) {

            cout
                << candidate
                << " -> substring="
                << boolalpha
                << isSubstring("ABCDE", candidate)
                << ", subsequence="
                << isSubsequence("ABCDE", candidate)
                << '\n';
        }

        cout << '\n';

        // --------------------------------------------------------------------
        // Stage 3: Compare search implementations
        // --------------------------------------------------------------------

        const string logText =
            "ERROR database connection failed after timeout";

        const string pattern = "connection";

        cout << "3. Search-engine comparison\n";

        cout
            << "Brute force index: "
            << bruteForceSearch(logText, pattern)
            << '\n';

        cout
            << "KMP index: "
            << kmpSearch(logText, pattern)
            << '\n';

        cout
            << "Rabin-Karp index: "
            << RollingHash::search(logText, pattern)
            << "\n\n";

        // --------------------------------------------------------------------
        // Stage 4: Repeated occurrences
        // --------------------------------------------------------------------

        cout << "4. Overlapping search\n";

        const string repeated = "aaaa";
        const string repeatedPattern = "aa";

        cout
            << "Text: "
            << repeated
            << ", pattern: "
            << repeatedPattern
            << '\n';

        cout
            << "Occurrences: "
            << countOverlappingOccurrences(
                   repeated,
                   repeatedPattern
               )
            << '\n';

        cout << "Positions: ";
        printVector(
            kmpSearchAll(
                repeated,
                repeatedPattern
            )
        );
        cout << "\n\n";

        // --------------------------------------------------------------------
        // Stage 5: Sliding-window analysis
        // --------------------------------------------------------------------

        cout << "5. Sliding-window substring analysis\n";

        cout
            << "Longest substring without repeating characters: "
            << longestUniqueSubstring("abcabcbb")
            << '\n';

        cout
            << "Longest palindrome: "
            << longestPalindromicSubstring(
                   "forgeeksskeegfor"
               )
            << '\n';

        cout << '\n';

        // --------------------------------------------------------------------
        // Stage 6: Dynamic programming
        // --------------------------------------------------------------------

        cout << "6. Longest common substring\n";

        cout
            << "First string:  ABABC\n"
            << "Second string: BABCA\n"
            << "Result: "
            << longestCommonSubstring(
                   "ABABC",
                   "BABCA"
               )
            << "\n\n";

        // --------------------------------------------------------------------
        // Stage 7: Industry-style log dataset
        // --------------------------------------------------------------------

        cout << "7. Industry-style log search\n";

        vector<LogRecord> logs = {
            {
                1,
                "INFO",
                "auth",
                "user authentication completed"
            },
            {
                2,
                "ERROR",
                "database",
                "database connection failed"
            },
            {
                3,
                "WARN",
                "gateway",
                "database response exceeded timeout"
            },
            {
                4,
                "ERROR",
                "payment",
                "payment service database connection failed"
            },
            {
                5,
                "INFO",
                "cache",
                "cache refresh completed"
            }
        };

        LogSearchEngine engine(logs);

        cout << "\nBrute-force search for 'database':\n";
        printRecords(
            engine.searchBruteForce("database")
        );

        cout << "\nKMP search for 'database':\n";
        printRecords(
            engine.searchKMP("database")
        );

        cout << "\nOccurrences by severity for 'database':\n";

        const auto counts =
            engine.countBySeverity("database");

        for (const auto& [severity, count] : counts) {
            cout
                << "  "
                << severity
                << ": "
                << count
                << '\n';
        }

        cout << "\nAll 'database' positions in one message:\n";

        const auto positions =
            engine.exactMatchPositions(
                logs[3].message,
                "database"
            );

        printVector(positions);
        cout << "\n\n";

        // --------------------------------------------------------------------
        // Stage 8: Edge conditions
        // --------------------------------------------------------------------

        cout << "8. Edge conditions\n";

        cout
            << "Empty text substring count: "
            << countAllSubstrings("")
            << '\n';

        cout
            << "Pattern longer than text: "
            << kmpSearch("abc", "abcdef")
            << '\n';

        cout
            << "Single-character search: "
            << kmpSearch("aaaaa", "a")
            << '\n';

        // --------------------------------------------------------------------
        // Stage 9: Correctness validation
        // --------------------------------------------------------------------

        cout << "\n9. Correctness tests\n";
        runTests();
        cout << "All C++ assertions passed.\n\n";

        // --------------------------------------------------------------------
        // Complexity discussion
        // --------------------------------------------------------------------

        cout << "10. Complexity characteristics\n";
        cout
            << "Substring generation: O(n^2) substring occurrences, "
               "plus substring-copy costs\n";
        cout
            << "Brute-force search: O(n*m) worst case\n";
        cout
            << "KMP: O(n+m) time, O(m) auxiliary space\n";
        cout
            << "Rabin-Karp: average near O(n+m), "
               "with collision-dependent worst case\n";
        cout
            << "Longest unique substring: O(n) average hash-table behavior\n";
        cout
            << "Longest common substring: O(n*m) time and O(m) space here\n";

        cout << "\nCase study completed successfully.\n";

    } catch (const exception& error) {
        cerr
            << "Application error: "
            << error.what()
            << '\n';

        return 1;
    }

    return 0;
}
