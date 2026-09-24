/*
 * Day 23 — Anagrams
 * ==================
 *
 * Industry-style C++17 case study:
 *
 * A text-indexing service receives large collections of textual records.
 * It must:
 *
 * 1. Validate and normalize records.
 * 2. Determine whether two records are anagrams.
 * 3. Build canonical signatures.
 * 4. Group records by anagram class.
 * 5. Search for anagram occurrences inside larger text.
 * 6. Maintain frequency counts efficiently with a sliding window.
 * 7. Demonstrate sorting and frequency-based approaches.
 * 8. Handle invalid input and edge cases.
 * 9. Report complexity and operational statistics.
 *
 * The implementation uses only the C++17 standard library.
 */

#include <algorithm>
#include <array>
#include <chrono>
#include <cctype>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;


// ============================================================================
// 1. DATA TYPES
// ============================================================================

using FrequencyArray = array<int, 26>;

struct Record {
    int id;
    string originalText;
    string normalizedText;
};

struct AnagramGroup {
    string signature;
    vector<int> recordIds;
};

struct SearchResult {
    string pattern;
    vector<size_t> startingPositions;
};


// ============================================================================
// 2. TEXT NORMALIZATION
// ============================================================================

string normalizeAsciiLetters(const string& input) {
    /*
     * This case study deliberately uses ASCII letters.
     *
     * A production Unicode implementation requires a Unicode-aware
     * normalization and grapheme-segmentation strategy rather than
     * treating every byte as an independent character.
     */
    string normalized;

    for (unsigned char character : input) {
        if (character >= 'A' && character <= 'Z') {
            normalized.push_back(
                static_cast<char>(character - 'A' + 'a')
            );
        } else if (character >= 'a' && character <= 'z') {
            normalized.push_back(static_cast<char>(character));
        }
    }

    return normalized;
}


bool containsOnlyAsciiLetters(const string& input) {
    for (unsigned char character : input) {
        if (!(
            (character >= 'a' && character <= 'z') ||
            (character >= 'A' && character <= 'Z')
        )) {
            return false;
        }
    }

    return true;
}


// ============================================================================
// 3. FREQUENCY COUNTING
// ============================================================================

FrequencyArray buildFrequencyArray(const string& text) {
    FrequencyArray frequencies{};

    for (unsigned char character : text) {
        if (character < 'a' || character > 'z') {
            throw invalid_argument(
                "FrequencyArray expects normalized lowercase ASCII letters."
            );
        }

        frequencies[character - 'a']++;
    }

    return frequencies;
}


bool frequenciesEqual(
    const FrequencyArray& first,
    const FrequencyArray& second
) {
    return first == second;
}


// ============================================================================
// 4. SORTING-BASED ANAGRAM CHECK
// ============================================================================

bool areAnagramsBySorting(
    const string& first,
    const string& second
) {
    if (first.size() != second.size()) {
        return false;
    }

    string firstCopy = first;
    string secondCopy = second;

    sort(firstCopy.begin(), firstCopy.end());
    sort(secondCopy.begin(), secondCopy.end());

    return firstCopy == secondCopy;
}


// ============================================================================
// 5. FREQUENCY-BASED ANAGRAM CHECK
// ============================================================================

bool areAnagramsByFrequency(
    const string& first,
    const string& second
) {
    if (first.size() != second.size()) {
        return false;
    }

    FrequencyArray frequencies{};

    for (char character : first) {
        if (character < 'a' || character > 'z') {
            throw invalid_argument(
                "Frequency comparison requires lowercase ASCII letters."
            );
        }

        frequencies[character - 'a']++;
    }

    for (char character : second) {
        if (character < 'a' || character > 'z') {
            throw invalid_argument(
                "Frequency comparison requires lowercase ASCII letters."
            );
        }

        frequencies[character - 'a']--;
    }

    return all_of(
        frequencies.begin(),
        frequencies.end(),
        [](int count) {
            return count == 0;
        }
    );
}


// ============================================================================
// 6. CANONICAL SIGNATURE
// ============================================================================

string createSortingSignature(const string& normalizedText) {
    string signature = normalizedText;
    sort(signature.begin(), signature.end());
    return signature;
}


string createFrequencySignature(const string& normalizedText) {
    FrequencyArray frequencies = buildFrequencyArray(normalizedText);

    ostringstream output;

    for (size_t index = 0; index < frequencies.size(); ++index) {
        if (index > 0) {
            output << '#';
        }

        output << frequencies[index];
    }

    return output.str();
}


// ============================================================================
// 7. RECORD INDEX
// ============================================================================

class AnagramRecordIndex {
private:
    unordered_map<string, vector<int>> groups;
    unordered_map<int, Record> records;

public:
    void addRecord(int id, const string& originalText) {
        if (records.find(id) != records.end()) {
            throw invalid_argument(
                "Record ID already exists: " + to_string(id)
            );
        }

        const string normalized = normalizeAsciiLetters(originalText);

        if (normalized.empty()) {
            throw invalid_argument(
                "Record must contain at least one ASCII letter."
            );
        }

        Record record{
            id,
            originalText,
            normalized
        };

        const string signature = createFrequencySignature(normalized);

        records.emplace(id, record);
        groups[signature].push_back(id);
    }


    vector<int> findAnagrams(const string& text) const {
        const string normalized = normalizeAsciiLetters(text);

        if (normalized.empty()) {
            return {};
        }

        const string signature = createFrequencySignature(normalized);

        auto iterator = groups.find(signature);

        if (iterator == groups.end()) {
            return {};
        }

        return iterator->second;
    }


    vector<AnagramGroup> getGroups() const {
        vector<AnagramGroup> result;

        for (const auto& [signature, recordIds] : groups) {
            result.push_back({
                signature,
                recordIds
            });
        }

        return result;
    }


    const Record& getRecord(int id) const {
        auto iterator = records.find(id);

        if (iterator == records.end()) {
            throw out_of_range(
                "Unknown record ID: " + to_string(id)
            );
        }

        return iterator->second;
    }


    size_t recordCount() const {
        return records.size();
    }


    size_t groupCount() const {
        return groups.size();
    }
};


// ============================================================================
// 8. SLIDING-WINDOW SEARCH
// ============================================================================

vector<size_t> findAnagramWindows(
    const string& text,
    const string& pattern
) {
    if (pattern.empty() || pattern.size() > text.size()) {
        return {};
    }

    FrequencyArray patternFrequency =
        buildFrequencyArray(pattern);

    FrequencyArray windowFrequency{};

    vector<size_t> positions;

    const size_t windowSize = pattern.size();

    for (size_t index = 0; index < windowSize; ++index) {
        const char character = text[index];

        if (character < 'a' || character > 'z') {
            throw invalid_argument(
                "Sliding-window search requires lowercase ASCII input."
            );
        }

        windowFrequency[character - 'a']++;
    }

    if (frequenciesEqual(patternFrequency, windowFrequency)) {
        positions.push_back(0);
    }

    for (size_t right = windowSize; right < text.size(); ++right) {
        const char entering = text[right];
        const char leaving = text[right - windowSize];

        if (
            entering < 'a' || entering > 'z' ||
            leaving < 'a' || leaving > 'z'
        ) {
            throw invalid_argument(
                "Sliding-window search requires lowercase ASCII input."
            );
        }

        windowFrequency[entering - 'a']++;
        windowFrequency[leaving - 'a']--;

        if (frequenciesEqual(patternFrequency, windowFrequency)) {
            positions.push_back(right - windowSize + 1);
        }
    }

    return positions;
}


// ============================================================================
// 9. OPTIMIZED SLIDING WINDOW
// ============================================================================

vector<size_t> findAnagramWindowsOptimized(
    const string& text,
    const string& pattern
) {
    if (pattern.empty() || pattern.size() > text.size()) {
        return {};
    }

    FrequencyArray patternFrequency{};
    FrequencyArray windowFrequency{};

    for (char character : pattern) {
        if (character < 'a' || character > 'z') {
            throw invalid_argument(
                "Optimized search accepts lowercase ASCII letters."
            );
        }

        patternFrequency[character - 'a']++;
    }

    for (size_t index = 0; index < pattern.size(); ++index) {
        char character = text[index];

        if (character < 'a' || character > 'z') {
            throw invalid_argument(
                "Optimized search accepts lowercase ASCII letters."
            );
        }

        windowFrequency[character - 'a']++;
    }

    int matches = 0;

    for (size_t index = 0; index < 26; ++index) {
        if (patternFrequency[index] == windowFrequency[index]) {
            ++matches;
        }
    }

    vector<size_t> positions;

    if (matches == 26) {
        positions.push_back(0);
    }

    auto update = [&](size_t index, int delta) {
        const bool beforeEqual =
            patternFrequency[index] == windowFrequency[index];

        windowFrequency[index] += delta;

        const bool afterEqual =
            patternFrequency[index] == windowFrequency[index];

        if (beforeEqual && !afterEqual) {
            --matches;
        } else if (!beforeEqual && afterEqual) {
            ++matches;
        }
    };

    for (
        size_t right = pattern.size();
        right < text.size();
        ++right
    ) {
        const size_t enteringIndex =
            text[right] - 'a';

        const size_t leavingIndex =
            text[right - pattern.size()] - 'a';

        update(enteringIndex, 1);
        update(leavingIndex, -1);

        if (matches == 26) {
            positions.push_back(right - pattern.size() + 1);
        }
    }

    return positions;
}


// ============================================================================
// 10. INPUT VALIDATION
// ============================================================================

string readNonEmptyLine(const string& prompt) {
    cout << prompt;

    string input;
    getline(cin, input);

    if (input.empty()) {
        throw invalid_argument(
            "Input cannot be empty."
        );
    }

    return input;
}


int readPositiveInteger(const string& prompt) {
    cout << prompt;

    string input;
    getline(cin, input);

    try {
        size_t consumed = 0;
        int value = stoi(input, &consumed);

        if (consumed != input.size() || value <= 0) {
            throw invalid_argument("not a positive integer");
        }

        return value;
    } catch (const exception&) {
        throw invalid_argument(
            "Expected a positive integer."
        );
    }
}


// ============================================================================
// 11. REPORTING
// ============================================================================

void printPositions(const vector<size_t>& positions) {
    cout << '[';

    for (size_t index = 0; index < positions.size(); ++index) {
        if (index > 0) {
            cout << ", ";
        }

        cout << positions[index];
    }

    cout << ']';
}


void printRecord(const Record& record) {
    cout
        << "ID=" << record.id
        << ", original=" << quoted(record.originalText)
        << ", normalized=" << quoted(record.normalizedText)
        << '\n';
}


// ============================================================================
// 12. DEMONSTRATION
// ============================================================================

void demonstrateBasicAlgorithms() {
    cout << "\n";
    cout << string(78, '=') << '\n';
    cout << "BASIC ANAGRAM ALGORITHMS\n";
    cout << string(78, '=') << '\n';

    const vector<pair<string, string>> cases = {
        {"listen", "silent"},
        {"triangle", "integral"},
        {"evil", "vile"},
        {"hello", "world"},
        {"aabbcc", "abcabc"},
        {"aab", "abb"}
    };

    for (const auto& [first, second] : cases) {
        cout
            << quoted(first)
            << " vs "
            << quoted(second)
            << " -> sorting="
            << boolalpha
            << areAnagramsBySorting(first, second)
            << ", frequency="
            << areAnagramsByFrequency(first, second)
            << '\n';
    }
}


void demonstrateIndex() {
    cout << "\n";
    cout << string(78, '=') << '\n';
    cout << "INDUSTRY-STYLE TEXT RECORD INDEX\n";
    cout << string(78, '=') << '\n';

    AnagramRecordIndex index;

    index.addRecord(101, "Listen");
    index.addRecord(102, "Silent");
    index.addRecord(103, "Enlist");
    index.addRecord(104, "Debit Card");
    index.addRecord(105, "card debit");
    index.addRecord(106, "Secure Login");
    index.addRecord(107, "Login Secure");
    index.addRecord(108, "Python");

    cout << "Records: " << index.recordCount() << '\n';
    cout << "Anagram groups: " << index.groupCount() << '\n';

    for (const string& query : {
        "listen",
        "debitcard",
        "securelogin",
        "unknown"
    }) {
        cout << "\nQuery: " << quoted(query) << '\n';

        const vector<int> matches = index.findAnagrams(query);

        if (matches.empty()) {
            cout << "No matching records.\n";
            continue;
        }

        for (int id : matches) {
            printRecord(index.getRecord(id));
        }
    }
}


void demonstrateSlidingWindow() {
    cout << "\n";
    cout << string(78, '=') << '\n';
    cout << "ANAGRAM WINDOW SEARCH\n";
    cout << string(78, '=') << '\n';

    const string text = "cbaebabacd";
    const string pattern = "abc";

    cout << "Text: " << text << '\n';
    cout << "Pattern: " << pattern << '\n';

    cout << "Frequency comparison positions: ";
    printPositions(findAnagramWindows(text, pattern));
    cout << '\n';

    cout << "Optimized positions: ";
    printPositions(findAnagramWindowsOptimized(text, pattern));
    cout << '\n';

    cout << "\nRepeated-window example:\n";

    const string repeatedText = "abab";
    const string repeatedPattern = "ab";

    cout << "Text: " << repeatedText << '\n';
    cout << "Pattern: " << repeatedPattern << '\n';
    cout << "Positions: ";
    printPositions(
        findAnagramWindowsOptimized(
            repeatedText,
            repeatedPattern
        )
    );
    cout << '\n';
}


// ============================================================================
// 13. ERROR CASES
// ============================================================================

void demonstrateErrorHandling() {
    cout << "\n";
    cout << string(78, '=') << '\n';
    cout << "ERROR HANDLING AND EDGE CASES\n";
    cout << string(78, '=') << '\n';

    try {
        areAnagramsByFrequency("hello!", "olleh!");
    } catch (const exception& error) {
        cout << "Expected error: " << error.what() << '\n';
    }

    try {
        AnagramRecordIndex index;
        index.addRecord(1, "abc");
        index.addRecord(1, "def");
    } catch (const exception& error) {
        cout << "Expected duplicate-ID error: "
             << error.what() << '\n';
    }

    try {
        AnagramRecordIndex index;
        index.addRecord(1, "12345");
    } catch (const exception& error) {
        cout << "Expected invalid-record error: "
             << error.what() << '\n';
    }

    try {
        findAnagramWindows("abc!def", "abc");
    } catch (const exception& error) {
        cout << "Expected window-input error: "
             << error.what() << '\n';
    }
}


// ============================================================================
// 14. AUTOMATED TESTS
// ============================================================================

void runTests() {
    cout << "\n";
    cout << string(78, '=') << '\n';
    cout << "AUTOMATED TESTS\n";
    cout << string(78, '=') << '\n';

    const vector<pair<string, string>> positiveCases = {
        {"listen", "silent"},
        {"triangle", "integral"},
        {"evil", "vile"},
        {"anagram", "nagaram"},
        {"aabbcc", "abcabc"},
        {"", ""}
    };

    for (const auto& [first, second] : positiveCases) {
        if (
            !areAnagramsBySorting(first, second) ||
            !areAnagramsByFrequency(first, second)
        ) {
            throw runtime_error(
                "Positive anagram test failed."
            );
        }
    }

    const vector<pair<string, string>> negativeCases = {
        {"hello", "world"},
        {"abc", "abd"},
        {"a", "aa"},
        {"abc", "abcd"}
    };

    for (const auto& [first, second] : negativeCases) {
        if (
            areAnagramsBySorting(first, second) ||
            areAnagramsByFrequency(first, second)
        ) {
            throw runtime_error(
                "Negative anagram test failed."
            );
        }
    }

    if (
        findAnagramWindows("cbaebabacd", "abc") !=
        vector<size_t>{0, 6}
    ) {
        throw runtime_error(
            "Sliding-window test failed."
        );
    }

    if (
        findAnagramWindowsOptimized("cbaebabacd", "abc") !=
        vector<size_t>{0, 6}
    ) {
        throw runtime_error(
            "Optimized sliding-window test failed."
        );
    }

    if (
        findAnagramWindowsOptimized("abab", "ab") !=
        vector<size_t>{0, 1, 2}
    ) {
        throw runtime_error(
            "Repeated-window test failed."
        );
    }

    if (
        !findAnagramWindowsOptimized("abc", "").empty()
    ) {
        throw runtime_error(
            "Empty-pattern test failed."
        );
    }

    cout << "All tests passed.\n";
}


// ============================================================================
// 15. BENCHMARK
// ============================================================================

void benchmarkAlgorithms() {
    cout << "\n";
    cout << string(78, '=') << '\n';
    cout << "PERFORMANCE COMPARISON\n";
    cout << string(78, '=') << '\n';

    string first;

    for (int repetition = 0; repetition < 2000; ++repetition) {
        first += "abcdefghijklmnopqrstuvwxyz";
    }

    string second = first;
    reverse(second.begin(), second.end());

    auto startSorting = chrono::high_resolution_clock::now();

    const bool sortingResult =
        areAnagramsBySorting(first, second);

    auto endSorting = chrono::high_resolution_clock::now();

    auto startFrequency = chrono::high_resolution_clock::now();

    const bool frequencyResult =
        areAnagramsByFrequency(first, second);

    auto endFrequency = chrono::high_resolution_clock::now();

    const auto sortingDuration =
        chrono::duration_cast<chrono::microseconds>(
            endSorting - startSorting
        ).count();

    const auto frequencyDuration =
        chrono::duration_cast<chrono::microseconds>(
            endFrequency - startFrequency
        ).count();

    cout
        << "Sorting result: "
        << boolalpha
        << sortingResult
        << ", time: "
        << sortingDuration
        << " microseconds\n";

    cout
        << "Frequency result: "
        << frequencyResult
        << ", time: "
        << frequencyDuration
        << " microseconds\n";

    cout << "\nThe benchmark is hardware-dependent and should be interpreted\n";
    cout << "as an implementation observation rather than a universal ratio.\n";
}


// ============================================================================
// 16. COMPLEXITY REPORT
// ============================================================================

void printComplexityReport() {
    cout << "\n";
    cout << string(78, '=') << '\n';
    cout << "COMPLEXITY REPORT\n";
    cout << string(78, '=') << '\n';

    cout
        << left
        << setw(42)
        << "Technique"
        << setw(24)
        << "Complexity"
        << '\n';

    cout << string(66, '-') << '\n';

    cout
        << setw(42)
        << "Sorting-based comparison"
        << setw(24)
        << "O(n log n)"
        << '\n';

    cout
        << setw(42)
        << "Frequency-array comparison"
        << setw(24)
        << "O(n)"
        << '\n';

    cout
        << setw(42)
        << "Hash-based grouping"
        << setw(24)
        << "O(n * m) average"
        << '\n';

    cout
        << setw(42)
        << "Naive pairwise detection"
        << setw(24)
        << "O(n² * m)"
        << '\n';

    cout
        << setw(42)
        << "Sliding-window search"
        << setw(24)
        << "O(n)"
        << '\n';

    cout
        << setw(42)
        << "Fixed 26-character state"
        << setw(24)
        << "O(1) auxiliary space"
        << '\n';
}


// ============================================================================
// 17. MAIN
// ============================================================================

int main() {
    try {
        demonstrateBasicAlgorithms();
        demonstrateIndex();
        demonstrateSlidingWindow();
        demonstrateErrorHandling();
        runTests();
        benchmarkAlgorithms();
        printComplexityReport();

        cout << "\n";
        cout << string(78, '=') << '\n';
        cout << "CASE STUDY COMPLETED SUCCESSFULLY\n";
        cout << string(78, '=') << '\n';

        return 0;
    } catch (const exception& error) {
        cerr << "\nFatal error: " << error.what() << '\n';
        return 1;
    }
}
