/*
 * Day 21 — Character Frequency
 * =============================
 *
 * Industry-style case study:
 * A text analytics engine that receives documents, validates them,
 * calculates character-frequency statistics, detects duplicates and unique
 * characters, compares frequency distributions, groups documents by
 * character signature, and performs a sliding-window search.
 *
 * Standard: C++17
 *
 * Concepts demonstrated:
 * - unordered_map
 * - array-based frequency counting
 * - strings and character processing
 * - classes and encapsulation
 * - validation
 * - algorithms
 * - sorting
 * - frequency comparison
 * - grouping
 * - sliding windows
 * - complexity and trade-offs
 * - exception handling
 */

#include <algorithm>
#include <array>
#include <cctype>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;


// ============================================================================
// 1. DATA TYPES
// ============================================================================

using FrequencyMap = unordered_map<char, int>;

struct CharacterStat {
    char character;
    int frequency;
};

struct DocumentAnalysis {
    string documentId;
    size_t length = 0;
    size_t distinctCharacters = 0;
    optional<CharacterStat> mostFrequent;
    optional<char> firstNonRepeating;
    vector<CharacterStat> duplicates;
};


// ============================================================================
// 2. TEXT ANALYTICS ENGINE
// ============================================================================

class TextAnalyticsEngine {
public:
    static void validate(const string& text) {
        /*
         * Empty strings are valid analytical inputs. They simply produce
         * empty frequency statistics.
         */
        if (text.size() > 10'000'000) {
            throw invalid_argument(
                "Document exceeds the supported 10,000,000-byte limit."
            );
        }
    }


    static FrequencyMap countCharacters(const string& text) {
        validate(text);

        FrequencyMap frequency;

        for (char character : text) {
            ++frequency[character];
        }

        return frequency;
    }


    static array<int, 26> lowercaseLetterArray(const string& text) {
        validate(text);

        array<int, 26> frequency{};
        frequency.fill(0);

        for (unsigned char rawCharacter : text) {
            char character = static_cast<char>(rawCharacter);

            if (character >= 'a' && character <= 'z') {
                ++frequency[character - 'a'];
            }
        }

        return frequency;
    }


    static vector<CharacterStat> sortedStatistics(
        const FrequencyMap& frequency
    ) {
        vector<CharacterStat> statistics;

        statistics.reserve(frequency.size());

        for (const auto& [character, count] : frequency) {
            statistics.push_back({character, count});
        }

        /*
         * Sorting gives deterministic output. Frequency is the primary key;
         * character is the secondary key.
         */
        sort(
            statistics.begin(),
            statistics.end(),
            [](const CharacterStat& first, const CharacterStat& second) {
                if (first.frequency != second.frequency) {
                    return first.frequency > second.frequency;
                }

                return first.character < second.character;
            }
        );

        return statistics;
    }


    static optional<CharacterStat> mostFrequentCharacter(
        const string& text
    ) {
        const FrequencyMap frequency = countCharacters(text);

        if (frequency.empty()) {
            return nullopt;
        }

        CharacterStat best{'\0', -1};

        /*
         * Tie-breaking uses the smallest character. A production system can
         * choose another explicit policy depending on business requirements.
         */
        for (const auto& [character, count] : frequency) {
            if (
                count > best.frequency ||
                (count == best.frequency && character < best.character)
            ) {
                best = {character, count};
            }
        }

        return best;
    }


    static vector<CharacterStat> duplicateCharacters(
        const string& text
    ) {
        const FrequencyMap frequency = countCharacters(text);
        vector<CharacterStat> result;

        for (const auto& [character, count] : frequency) {
            if (count > 1) {
                result.push_back({character, count});
            }
        }

        sort(
            result.begin(),
            result.end(),
            [](const CharacterStat& first, const CharacterStat& second) {
                return first.character < second.character;
            }
        );

        return result;
    }


    static optional<char> firstNonRepeatingCharacter(
        const string& text
    ) {
        const FrequencyMap frequency = countCharacters(text);

        for (char character : text) {
            if (frequency.at(character) == 1) {
                return character;
            }
        }

        return nullopt;
    }


    static bool sameFrequency(
        const string& first,
        const string& second
    ) {
        return countCharacters(first) == countCharacters(second);
    }


    static bool areAnagrams(
        const string& first,
        const string& second
    ) {
        /*
         * This example treats spaces and punctuation as irrelevant and
         * compares ASCII letters case-insensitively.
         */
        string normalizedFirst = normalizeLetters(first);
        string normalizedSecond = normalizeLetters(second);

        return sameFrequency(normalizedFirst, normalizedSecond);
    }


    static string normalizeLetters(const string& text) {
        string normalized;

        for (unsigned char rawCharacter : text) {
            char character = static_cast<char>(rawCharacter);

            if (
                (character >= 'A' && character <= 'Z') ||
                (character >= 'a' && character <= 'z')
            ) {
                normalized.push_back(
                    static_cast<char>(tolower(rawCharacter))
                );
            }
        }

        return normalized;
    }


    static unordered_map<int, vector<char>> groupByFrequency(
        const string& text
    ) {
        const FrequencyMap frequency = countCharacters(text);
        unordered_map<int, vector<char>> groups;

        for (const auto& [character, count] : frequency) {
            groups[count].push_back(character);
        }

        for (auto& [count, characters] : groups) {
            sort(characters.begin(), characters.end());
        }

        return groups;
    }


    static string longestUniqueSubstring(const string& text) {
        /*
         * Sliding window:
         *
         * lastSeen[c] stores the latest index at which c occurred.
         * left never moves backward.
         *
         * Complexity:
         *   Time  = O(n)
         *   Space = O(k)
         *
         * The algorithm operates on bytes because std::string is a byte
         * sequence. Full Unicode grapheme processing requires a Unicode
         * library and is outside the C++ standard library.
         */
        unordered_map<char, size_t> lastSeen;

        size_t left = 0;
        size_t bestStart = 0;
        size_t bestLength = 0;

        for (size_t right = 0; right < text.size(); ++right) {
            char character = text[right];

            auto found = lastSeen.find(character);

            if (
                found != lastSeen.end() &&
                found->second >= left
            ) {
                left = found->second + 1;
            }

            lastSeen[character] = right;

            size_t currentLength = right - left + 1;

            if (currentLength > bestLength) {
                bestLength = currentLength;
                bestStart = left;
            }
        }

        return text.substr(bestStart, bestLength);
    }


    static optional<string> minimumWindow(
        const string& text,
        const string& required
    ) {
        if (required.empty()) {
            return string{};
        }

        FrequencyMap requiredCounts = countCharacters(required);
        FrequencyMap windowCounts;

        size_t formed = 0;
        const size_t requiredKinds = requiredCounts.size();

        size_t left = 0;
        size_t bestStart = 0;
        size_t bestLength = numeric_limits<size_t>::max();

        for (size_t right = 0; right < text.size(); ++right) {
            char character = text[right];
            ++windowCounts[character];

            auto requiredIt = requiredCounts.find(character);

            if (
                requiredIt != requiredCounts.end() &&
                windowCounts[character] == requiredIt->second
            ) {
                ++formed;
            }

            while (formed == requiredKinds && left <= right) {
                const size_t currentLength = right - left + 1;

                if (currentLength < bestLength) {
                    bestLength = currentLength;
                    bestStart = left;
                }

                char leftCharacter = text[left];
                --windowCounts[leftCharacter];

                auto leftRequired =
                    requiredCounts.find(leftCharacter);

                if (
                    leftRequired != requiredCounts.end() &&
                    windowCounts[leftCharacter] < leftRequired->second
                ) {
                    --formed;
                }

                ++left;
            }
        }

        if (bestLength == numeric_limits<size_t>::max()) {
            return nullopt;
        }

        return text.substr(bestStart, bestLength);
    }


    static string signature(const string& text) {
        /*
         * A fixed 256-entry signature is practical for byte-oriented input.
         * It avoids dependence on unordered_map iteration order.
         */
        array<int, 256> frequency{};
        frequency.fill(0);

        for (unsigned char character : text) {
            ++frequency[character];
        }

        ostringstream output;

        for (size_t index = 0; index < frequency.size(); ++index) {
            if (frequency[index] > 0) {
                output
                    << index
                    << ':'
                    << frequency[index]
                    << ';';
            }
        }

        return output.str();
    }


    static unordered_map<string, vector<string>> groupAnagrams(
        const vector<string>& words
    ) {
        unordered_map<string, vector<string>> groups;

        for (const string& word : words) {
            groups[signature(word)].push_back(word);
        }

        return groups;
    }


    static DocumentAnalysis analyzeDocument(
        const string& documentId,
        const string& text
    ) {
        validate(text);

        const FrequencyMap frequency = countCharacters(text);

        DocumentAnalysis analysis;
        analysis.documentId = documentId;
        analysis.length = text.size();
        analysis.distinctCharacters = frequency.size();
        analysis.mostFrequent = mostFrequentCharacter(text);
        analysis.firstNonRepeating = firstNonRepeatingCharacter(text);
        analysis.duplicates = duplicateCharacters(text);

        return analysis;
    }
};


// ============================================================================
// 3. REPORTING
// ============================================================================

string printableCharacter(char character) {
    if (character == ' ') {
        return "<space>";
    }

    if (character == '\n') {
        return "<newline>";
    }

    if (character == '\t') {
        return "<tab>";
    }

    if (isprint(static_cast<unsigned char>(character))) {
        return string(1, character);
    }

    ostringstream output;
    output << "ASCII(" << static_cast<int>(
        static_cast<unsigned char>(character)
    ) << ')';

    return output.str();
}


void printFrequencyTable(const FrequencyMap& frequency) {
    vector<CharacterStat> statistics =
        TextAnalyticsEngine::sortedStatistics(frequency);

    cout << left
         << setw(16)
         << "Character"
         << setw(12)
         << "Frequency"
         << '\n';

    cout << string(28, '-') << '\n';

    for (const auto& statistic : statistics) {
        cout << left
             << setw(16)
             << printableCharacter(statistic.character)
             << setw(12)
             << statistic.frequency
             << '\n';
    }
}


void printDocumentAnalysis(const DocumentAnalysis& analysis) {
    cout << "\nDocument: " << analysis.documentId << '\n';
    cout << "Length: " << analysis.length << '\n';
    cout << "Distinct characters: "
         << analysis.distinctCharacters << '\n';

    cout << "Most frequent: ";

    if (analysis.mostFrequent.has_value()) {
        cout
            << printableCharacter(
                analysis.mostFrequent->character
            )
            << " ("
            << analysis.mostFrequent->frequency
            << ")\n";
    } else {
        cout << "none\n";
    }

    cout << "First non-repeating: ";

    if (analysis.firstNonRepeating.has_value()) {
        cout << printableCharacter(
            analysis.firstNonRepeating.value()
        ) << '\n';
    } else {
        cout << "none\n";
    }

    cout << "Duplicate characters: ";

    if (analysis.duplicates.empty()) {
        cout << "none\n";
    } else {
        for (size_t index = 0; index < analysis.duplicates.size(); ++index) {
            if (index > 0) {
                cout << ", ";
            }

            cout
                << printableCharacter(
                    analysis.duplicates[index].character
                )
                << '='
                << analysis.duplicates[index].frequency;
        }

        cout << '\n';
    }
}


// ============================================================================
// 4. TESTING
// ============================================================================

void require(
    bool condition,
    const string& testName
) {
    if (!condition) {
        throw runtime_error("Test failed: " + testName);
    }

    cout << "[PASS] " << testName << '\n';
}


void runTests() {
    require(
        TextAnalyticsEngine::countCharacters("banana")['a'] == 3,
        "basic character counting"
    );

    require(
        TextAnalyticsEngine::countCharacters("").empty(),
        "empty input"
    );

    auto mostFrequent =
        TextAnalyticsEngine::mostFrequentCharacter("banana");

    require(
        mostFrequent.has_value() &&
        mostFrequent->character == 'a' &&
        mostFrequent->frequency == 3,
        "most frequent character"
    );

    auto firstUnique =
        TextAnalyticsEngine::firstNonRepeatingCharacter("swiss");

    require(
        firstUnique.has_value() &&
        firstUnique.value() == 'w',
        "first non-repeating character"
    );

    require(
        TextAnalyticsEngine::sameFrequency(
            "aabbcc",
            "ccbbaa"
        ),
        "frequency comparison"
    );

    require(
        TextAnalyticsEngine::areAnagrams(
            "Dormitory",
            "Dirty room"
        ),
        "anagram comparison"
    );

    require(
        TextAnalyticsEngine::longestUniqueSubstring("abcabcbb") == "abc",
        "longest unique substring"
    );

    auto minimum =
        TextAnalyticsEngine::minimumWindow(
            "ADOBECODEBANC",
            "ABC"
        );

    require(
        minimum.has_value() &&
        minimum.value() == "BANC",
        "minimum required-character window"
    );

    const auto groups =
        TextAnalyticsEngine::groupAnagrams(
            {"eat", "tea", "tan", "ate", "nat", "bat"}
        );

    require(
        groups.size() == 3,
        "anagram grouping"
    );

    try {
        TextAnalyticsEngine::validate(
            string(10'000'001, 'x')
        );

        throw runtime_error(
            "Expected oversized document validation to fail."
        );
    } catch (const invalid_argument&) {
        cout << "[PASS] input size validation\n";
    }
}


// ============================================================================
// 5. MAIN CASE STUDY
// ============================================================================

int main() {
    try {
        cout << "============================================================\n";
        cout << "DAY 21 — CHARACTER FREQUENCY\n";
        cout << "TEXT ANALYTICS ENGINE CASE STUDY\n";
        cout << "============================================================\n";

        /*
         * A realistic document-processing scenario:
         * several documents arrive at an analytics service. The service
         * computes structural character statistics before other processing.
         */
        vector<pair<string, string>> documents = {
            {
                "DOC-001",
                "Data structures make software efficient."
            },
            {
                "DOC-002",
                "Character frequency reveals repeated patterns."
            },
            {
                "DOC-003",
                "Algorithms use frequency maps for many problems."
            }
        };

        for (const auto& [documentId, text] : documents) {
            DocumentAnalysis analysis =
                TextAnalyticsEngine::analyzeDocument(
                    documentId,
                    text
                );

            printDocumentAnalysis(analysis);

            cout << "\nFrequency table:\n";

            printFrequencyTable(
                TextAnalyticsEngine::countCharacters(text)
            );
        }

        cout << "\n============================================================\n";
        cout << "FIXED-ALPHABET ARRAY ANALYSIS\n";
        cout << "============================================================\n";

        const string sample = "banana";

        auto letterArray =
            TextAnalyticsEngine::lowercaseLetterArray(sample);

        for (size_t index = 0; index < letterArray.size(); ++index) {
            if (letterArray[index] > 0) {
                cout
                    << static_cast<char>('a' + index)
                    << " -> "
                    << letterArray[index]
                    << '\n';
            }
        }

        cout << "\n============================================================\n";
        cout << "FREQUENCY COMPARISON\n";
        cout << "============================================================\n";

        const string first = "listen";
        const string second = "silent";

        cout << "First:  " << first << '\n';
        cout << "Second: " << second << '\n';
        cout
            << "Same frequency distribution: "
            << boolalpha
            << TextAnalyticsEngine::sameFrequency(first, second)
            << '\n';

        cout
            << "Anagram after normalization: "
            << TextAnalyticsEngine::areAnagrams(
                "The eyes",
                "They see"
            )
            << '\n';

        cout << "\n============================================================\n";
        cout << "SLIDING-WINDOW ANALYSIS\n";
        cout << "============================================================\n";

        const string sequence = "abcabcbb";

        cout
            << "Input: "
            << sequence
            << '\n';

        cout
            << "Longest unique substring: "
            << TextAnalyticsEngine::longestUniqueSubstring(sequence)
            << '\n';

        auto minimumWindow =
            TextAnalyticsEngine::minimumWindow(
                "ADOBECODEBANC",
                "ABC"
            );

        cout << "Minimum window containing ABC: ";

        if (minimumWindow.has_value()) {
            cout << minimumWindow.value();
        } else {
            cout << "not found";
        }

        cout << '\n';

        cout << "\n============================================================\n";
        cout << "ANAGRAM GROUPING\n";
        cout << "============================================================\n";

        vector<string> words = {
            "eat",
            "tea",
            "tan",
            "ate",
            "nat",
            "bat"
        };

        const auto anagramGroups =
            TextAnalyticsEngine::groupAnagrams(words);

        for (const auto& [signature, members] : anagramGroups) {
            cout << "Signature " << signature << " -> ";

            for (size_t index = 0; index < members.size(); ++index) {
                if (index > 0) {
                    cout << ", ";
                }

                cout << members[index];
            }

            cout << '\n';
        }

        cout << "\n============================================================\n";
        cout << "TEST SUITE\n";
        cout << "============================================================\n";

        runTests();

        cout << "\nAll case-study operations completed successfully.\n";

        /*
         * Production considerations:
         *
         * 1. Input limits prevent uncontrolled memory consumption.
         * 2. unordered_map gives expected O(1) lookup but is not guaranteed
         *    O(1) in the strict worst case.
         * 3. Arrays are preferable for a small known alphabet.
         * 4. Unicode requires a clear definition of "character".
         * 5. Deterministic sorting is useful for reproducible reports.
         * 6. Frequency data can reveal sensitive textual patterns and should
         *    be handled according to the application's data-security policy.
         */
        return 0;
    }
    catch (const exception& error) {
        cerr
            << "Fatal error: "
            << error.what()
            << '\n';

        return 1;
    }
}
