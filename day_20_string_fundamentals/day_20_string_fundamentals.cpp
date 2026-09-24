/*
 * Day 20 — String Fundamentals
 * =============================
 *
 * C++17 industry-style case study:
 * A command-line Text Intelligence Analyzer.
 *
 * The program demonstrates:
 * - std::string
 * - characters and indexing
 * - traversal
 * - concatenation
 * - comparison
 * - conversion
 * - case conversion
 * - whitespace removal
 * - word counting
 * - vowel counting
 * - first unique character
 * - frequency analysis
 * - validation
 * - structured results
 * - classes and modular design
 * - complexity considerations
 * - edge-case handling
 *
 * Compile:
 *   g++ -std=c++17 -O2 -Wall -Wextra -pedantic main.cpp -o text_analyzer
 *
 * Run:
 *   ./text_analyzer
 */

#include <algorithm>
#include <cctype>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;


// ---------------------------------------------------------------------------
// Utility functions
// ---------------------------------------------------------------------------

string toLowerASCII(const string& text) {
    string result = text;

    for (char& character : result) {
        unsigned char value = static_cast<unsigned char>(character);
        character = static_cast<char>(tolower(value));
    }

    return result;
}


string toUpperASCII(const string& text) {
    string result = text;

    for (char& character : result) {
        unsigned char value = static_cast<unsigned char>(character);
        character = static_cast<char>(toupper(value));
    }

    return result;
}


bool isWhitespace(char character) {
    return isspace(static_cast<unsigned char>(character)) != 0;
}


bool isASCIIAlpha(char character) {
    return isalpha(static_cast<unsigned char>(character)) != 0;
}


bool isASCIIDigit(char character) {
    return isdigit(static_cast<unsigned char>(character)) != 0;
}


bool isVowel(char character) {
    character = static_cast<char>(
        tolower(static_cast<unsigned char>(character))
    );

    return character == 'a' ||
           character == 'e' ||
           character == 'i' ||
           character == 'o' ||
           character == 'u';
}


string trim(const string& text) {
    size_t first = 0;

    while (first < text.size() && isWhitespace(text[first])) {
        ++first;
    }

    if (first == text.size()) {
        return "";
    }

    size_t last = text.size() - 1;

    while (last > first && isWhitespace(text[last])) {
        --last;
    }

    return text.substr(first, last - first + 1);
}


// ---------------------------------------------------------------------------
// Basic string operations
// ---------------------------------------------------------------------------

void demonstrateCharacters() {
    cout << "\n=== 1. Characters and strings ===\n";

    char character = 'A';
    string word = "C++";
    string sentence = "String fundamentals are important.";

    cout << "Character: " << character << '\n';
    cout << "Word: " << word << '\n';
    cout << "Sentence: " << sentence << '\n';

    cout << "Character size: " << sizeof(character) << " byte(s)\n";
    cout << "String length: " << word.size() << '\n';

    /*
     * std::string stores a sequence of char objects.
     * A char normally represents one byte, not necessarily one human-visible
     * Unicode character. Full Unicode processing requires an appropriate
     * encoding strategy or dedicated library.
     */
    cout << "Byte-oriented example: cafe -> " << "cafe" << '\n';
}


void demonstrateIndexingAndTraversal() {
    cout << "\n=== 2. Indexing and traversal ===\n";

    string text = "CPP";

    cout << "Text: " << text << '\n';
    cout << "Index 0: " << text[0] << '\n';
    cout << "Index 1: " << text[1] << '\n';
    cout << "Last character: " << text[text.size() - 1] << '\n';

    cout << "Range-based traversal:\n";

    for (char character : text) {
        cout << character << '\n';
    }

    cout << "Index-based traversal:\n";

    for (size_t index = 0; index < text.size(); ++index) {
        cout << index << " -> " << text[index] << '\n';
    }

    /*
     * at() performs bounds checking and throws std::out_of_range for an
     * invalid index, while operator[] does not perform bounds checking.
     */
    try {
        cout << "Checked access: " << text.at(100) << '\n';
    } catch (const out_of_range& error) {
        cout << "Invalid index handled: " << error.what() << '\n';
    }
}


void demonstrateConcatenationAndComparison() {
    cout << "\n=== 3. Concatenation and comparison ===\n";

    string firstName = "Atul";
    string lastName = "Pandey";

    string fullName = firstName + " " + lastName;

    cout << "Full name: " << fullName << '\n';

    string message = "C++ " + string("supports ") + "string operations.";
    cout << message << '\n';

    cout << "apple == apple: "
         << boolalpha << ("apple" == "apple") << '\n';

    cout << "apple == Apple: "
         << ("apple" == "Apple") << '\n';

    cout << "apple < banana: "
         << ("apple" < "banana") << '\n';
}


// ---------------------------------------------------------------------------
// Practice algorithms
// ---------------------------------------------------------------------------

string reverseString(const string& text) {
    string result = text;

    reverse(result.begin(), result.end());

    return result;
}


size_t countCharacters(const string& text) {
    return text.size();
}


string removeSpaces(const string& text) {
    string result;
    result.reserve(text.size());

    for (char character : text) {
        if (!isWhitespace(character)) {
            result.push_back(character);
        }
    }

    return result;
}


string changeCase(const string& text, const string& mode) {
    if (mode == "upper") {
        return toUpperASCII(text);
    }

    if (mode == "lower") {
        return toLowerASCII(text);
    }

    if (mode == "capitalize") {
        string result = toLowerASCII(text);

        if (!result.empty()) {
            result[0] = static_cast<char>(
                toupper(static_cast<unsigned char>(result[0]))
            );
        }

        return result;
    }

    throw invalid_argument(
        "Unsupported case mode. Use upper, lower, or capitalize."
    );
}


size_t countVowels(const string& text) {
    size_t count = 0;

    for (char character : text) {
        if (isVowel(character)) {
            ++count;
        }
    }

    return count;
}


pair<size_t, size_t> countVowelsAndConsonants(const string& text) {
    size_t vowels = 0;
    size_t consonants = 0;

    for (char character : text) {
        if (!isASCIIAlpha(character)) {
            continue;
        }

        if (isVowel(character)) {
            ++vowels;
        } else {
            ++consonants;
        }
    }

    return {vowels, consonants};
}


unordered_map<char, size_t> characterFrequency(const string& text) {
    unordered_map<char, size_t> frequencies;

    for (char character : text) {
        ++frequencies[character];
    }

    return frequencies;
}


optional<char> firstUniqueCharacter(const string& text) {
    unordered_map<char, size_t> frequencies =
        characterFrequency(text);

    for (char character : text) {
        if (frequencies[character] == 1) {
            return character;
        }
    }

    return nullopt;
}


size_t countWords(const string& text) {
    size_t wordCount = 0;
    bool insideWord = false;

    for (char character : text) {
        if (isWhitespace(character)) {
            insideWord = false;
        } else if (!insideWord) {
            ++wordCount;
            insideWord = true;
        }
    }

    return wordCount;
}


string longestWord(const string& text) {
    istringstream input(text);
    string word;
    string longest;

    while (input >> word) {
        if (word.size() > longest.size()) {
            longest = word;
        }
    }

    return longest;
}


string normalizeWhitespace(const string& text) {
    istringstream input(text);
    ostringstream output;

    string word;
    bool firstWord = true;

    while (input >> word) {
        if (!firstWord) {
            output << ' ';
        }

        output << word;
        firstWord = false;
    }

    return output.str();
}


bool isPalindrome(const string& text) {
    string cleaned;

    for (char character : text) {
        if (isASCIIAlpha(character) || isASCIIDigit(character)) {
            cleaned.push_back(
                static_cast<char>(
                    tolower(static_cast<unsigned char>(character))
                )
            );
        }
    }

    return cleaned == reverseString(cleaned);
}


vector<size_t> findAllOccurrences(
    const string& text,
    const string& target
) {
    if (target.empty()) {
        throw invalid_argument("Target must not be empty.");
    }

    vector<size_t> positions;

    size_t position = text.find(target);

    while (position != string::npos) {
        positions.push_back(position);

        /*
         * Move by one position rather than by target.size() so overlapping
         * matches can also be discovered.
         */
        position = text.find(target, position + 1);
    }

    return positions;
}


// ---------------------------------------------------------------------------
// Character classification
// ---------------------------------------------------------------------------

struct CharacterClasses {
    size_t letters = 0;
    size_t digits = 0;
    size_t whitespace = 0;
    size_t punctuationOrSymbols = 0;
};


CharacterClasses classifyCharacters(const string& text) {
    CharacterClasses result;

    for (char character : text) {
        unsigned char value =
            static_cast<unsigned char>(character);

        if (isalpha(value)) {
            ++result.letters;
        } else if (isdigit(value)) {
            ++result.digits;
        } else if (isspace(value)) {
            ++result.whitespace;
        } else {
            ++result.punctuationOrSymbols;
        }
    }

    return result;
}


// ---------------------------------------------------------------------------
// Complete analyzer model
// ---------------------------------------------------------------------------

struct TextAnalysis {
    string original;
    size_t characterCount = 0;
    size_t charactersWithoutSpaces = 0;
    size_t wordCount = 0;
    size_t vowelCount = 0;
    size_t consonantCount = 0;
    optional<char> firstUnique;
    string longestWord;
    bool palindrome = false;
    string normalized;
    CharacterClasses classes;
};


class TextAnalyzer {
private:
    string text;

public:
    explicit TextAnalyzer(string input)
        : text(move(input)) {
        if (trim(text).empty()) {
            throw invalid_argument(
                "Text must not be empty or whitespace-only."
            );
        }
    }

    TextAnalysis analyze() const {
        auto [vowels, consonants] =
            countVowelsAndConsonants(text);

        TextAnalysis result;

        result.original = text;
        result.characterCount = countCharacters(text);
        result.charactersWithoutSpaces = removeSpaces(text).size();
        result.wordCount = countWords(text);
        result.vowelCount = vowels;
        result.consonantCount = consonants;
        result.firstUnique = firstUniqueCharacter(text);
        result.longestWord = longestWord(text);
        result.palindrome = isPalindrome(text);
        result.normalized = normalizeWhitespace(text);
        result.classes = classifyCharacters(text);

        return result;
    }
};


// ---------------------------------------------------------------------------
// Report generation
// ---------------------------------------------------------------------------

void printFrequencyTable(const string& text) {
    cout << "\nCharacter frequency table:\n";

    map<char, size_t> sortedFrequencies;

    for (char character : text) {
        if (!isWhitespace(character)) {
            ++sortedFrequencies[character];
        }
    }

    for (const auto& [character, frequency] : sortedFrequencies) {
        cout << "  ";

        if (character == '\n') {
            cout << "\\n";
        } else if (character == '\t') {
            cout << "\\t";
        } else {
            cout << character;
        }

        cout << " : " << frequency << '\n';
    }
}


void printReport(const TextAnalysis& analysis) {
    cout << "\n=== Text analysis report ===\n";

    cout << "Original: "
         << analysis.original << '\n';

    cout << "Character count: "
         << analysis.characterCount << '\n';

    cout << "Characters without spaces: "
         << analysis.charactersWithoutSpaces << '\n';

    cout << "Word count: "
         << analysis.wordCount << '\n';

    cout << "Vowel count: "
         << analysis.vowelCount << '\n';

    cout << "Consonant count: "
         << analysis.consonantCount << '\n';

    cout << "First unique character: ";

    if (analysis.firstUnique.has_value()) {
        cout << *analysis.firstUnique << '\n';
    } else {
        cout << "none\n";
    }

    cout << "Longest word: "
         << analysis.longestWord << '\n';

    cout << "Palindrome: "
         << boolalpha << analysis.palindrome << '\n';

    cout << "Normalized whitespace: "
         << analysis.normalized << '\n';

    cout << "Letters: "
         << analysis.classes.letters << '\n';

    cout << "Digits: "
         << analysis.classes.digits << '\n';

    cout << "Whitespace: "
         << analysis.classes.whitespace << '\n';

    cout << "Punctuation/symbols: "
         << analysis.classes.punctuationOrSymbols << '\n';

    printFrequencyTable(analysis.original);
}


// ---------------------------------------------------------------------------
// Input validation and tests
// ---------------------------------------------------------------------------

void demonstrateInputValidation() {
    cout << "\n=== Input validation ===\n";

    vector<string> invalidInputs = {
        "",
        "   ",
        "\t\n"
    };

    for (const string& input : invalidInputs) {
        try {
            TextAnalyzer analyzer(input);
            static_cast<void>(analyzer);
        } catch (const invalid_argument& error) {
            cout << "Rejected invalid input: "
                 << error.what() << '\n';
        }
    }
}


void runTests() {
    cout << "\n=== Practice tests ===\n";

    if (reverseString("C++") != "++C") {
        throw runtime_error("Reverse-string test failed.");
    }

    if (reverseString("") != "") {
        throw runtime_error("Empty reverse test failed.");
    }

    if (removeSpaces("a b\tc\n") != "abc") {
        throw runtime_error("Space-removal test failed.");
    }

    if (changeCase("hello", "upper") != "HELLO") {
        throw runtime_error("Uppercase test failed.");
    }

    if (changeCase("HELLO", "lower") != "hello") {
        throw runtime_error("Lowercase test failed.");
    }

    if (countVowels("education") != 5) {
        throw runtime_error("Vowel-count test failed.");
    }

    if (countWords("one two three") != 3) {
        throw runtime_error("Word-count test failed.");
    }

    auto unique = firstUniqueCharacter("swiss");

    if (!unique.has_value() || *unique != 'w') {
        throw runtime_error("First-unique-character test failed.");
    }

    if (firstUniqueCharacter("aabb").has_value()) {
        throw runtime_error("No-unique-character test failed.");
    }

    if (!isPalindrome("level")) {
        throw runtime_error("Palindrome test failed.");
    }

    if (isPalindrome("C++")) {
        throw runtime_error("Non-palindrome test failed.");
    }

    vector<size_t> positions =
        findAllOccurrences("banana", "ana");

    if (positions.size() != 2 ||
        positions[0] != 1 ||
        positions[1] != 3) {
        throw runtime_error("Occurrence-search test failed.");
    }

    cout << "All tests passed.\n";
}


// ---------------------------------------------------------------------------
// Performance and trade-off demonstration
// ---------------------------------------------------------------------------

void demonstratePerformance() {
    cout << "\n=== Performance considerations ===\n";

    /*
     * Repeated concatenation can cause repeated allocation and copying.
     * reserve() gives the string capacity before repeated push_back().
     */
    vector<string> parts;

    for (int index = 0; index < 10; ++index) {
        parts.push_back("item-" + to_string(index));
    }

    string efficient;
    efficient.reserve(100);

    for (const string& part : parts) {
        efficient += part;
    }

    cout << "Constructed text: " << efficient << '\n';

    cout << "Character-frequency counting is expected O(n).\n";
    cout << "First-unique-character analysis is expected O(n) average time.\n";
    cout << "Word counting is O(n).\n";
    cout << "Reversing a string is O(n).\n";
    cout << "These operations generally require O(n) storage when creating "
            "new strings.\n";
}


// ---------------------------------------------------------------------------
// Main case study
// ---------------------------------------------------------------------------

int main() {
    try {
        cout << "============================================================\n";
        cout << "DAY 20 — STRING FUNDAMENTALS\n";
        cout << "============================================================\n";

        demonstrateCharacters();
        demonstrateIndexingAndTraversal();
        demonstrateConcatenationAndComparison();

        cout << "\n=== Practice problem demonstrations ===\n";

        const string sample =
            "C++ String Fundamentals";

        cout << "Original: "
             << sample << '\n';

        cout << "Reverse: "
             << reverseString(sample) << '\n';

        cout << "Character count: "
             << countCharacters(sample) << '\n';

        cout << "Without spaces: "
             << removeSpaces(sample) << '\n';

        cout << "Uppercase: "
             << changeCase(sample, "upper") << '\n';

        cout << "Lowercase: "
             << changeCase(sample, "lower") << '\n';

        cout << "Vowels: "
             << countVowels(sample) << '\n';

        cout << "Word count: "
             << countWords(sample) << '\n';

        cout << "Longest word: "
             << longestWord(sample) << '\n';

        cout << "First unique character: ";

        auto unique = firstUniqueCharacter(sample);

        if (unique.has_value()) {
            cout << *unique << '\n';
        } else {
            cout << "none\n";
        }

        vector<size_t> occurrences =
            findAllOccurrences("banana", "ana");

        cout << "Occurrences of \"ana\" in \"banana\": ";

        for (size_t position : occurrences) {
            cout << position << ' ';
        }

        cout << '\n';

        TextAnalyzer analyzer(
            "C++ provides efficient control over text-processing operations."
        );

        TextAnalysis analysis = analyzer.analyze();

        printReport(analysis);

        demonstrateInputValidation();
        demonstratePerformance();
        runTests();

        cout << "\n=== Study checklist ===\n";

        const vector<string> checklist = {
            "Characters",
            "Indexing",
            "Traversal",
            "Concatenation",
            "Comparison",
            "Conversion",
            "Case conversion",
            "Reverse string",
            "Count characters",
            "Remove spaces",
            "Change case",
            "Count vowels",
            "First unique character",
            "Count words"
        };

        for (const string& item : checklist) {
            cout << "[x] " << item << '\n';
        }

        cout << "\nDay 20 string fundamentals completed.\n";
    }
    catch (const exception& error) {
        cerr << "Fatal error: "
             << error.what() << '\n';

        return 1;
    }

    return 0;
}
