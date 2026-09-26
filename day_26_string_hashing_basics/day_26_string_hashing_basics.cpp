/*
 * Day 26 — String Hashing Basics
 *
 * C++17 case study:
 * A document indexing and duplicate-fragment detection engine.
 *
 * The system demonstrates:
 * - Polynomial rolling hashing
 * - Prefix hashes
 * - O(1) substring hash queries
 * - Double hashing
 * - Collision verification
 * - Rabin-Karp pattern matching
 * - Duplicate fragment detection
 * - Frequency indexing
 * - Longest repeated fragment detection
 * - Validation and error handling
 * - Complexity and design trade-offs
 *
 * Compile:
 *   g++ -std=c++17 -O2 day26_string_hashing.cpp -o day26
 *
 * Run:
 *   ./day26
 */

#include <algorithm>
#include <cstdint>
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

// -----------------------------------------------------------------------------
// 1. HASH PARAMETERS
// -----------------------------------------------------------------------------

struct HashParameters {
    uint64_t base;
    uint64_t modulus;
};

// -----------------------------------------------------------------------------
// 2. POLYNOMIAL ROLLING HASH
// -----------------------------------------------------------------------------

class RollingHash {
private:
    string text;
    HashParameters parameters;
    vector<uint64_t> prefix;
    vector<uint64_t> power;

public:
    RollingHash(
        const string& input,
        HashParameters parameters_
    )
        : text(input),
          parameters(parameters_) {

        if (parameters.modulus <= 1) {
            throw invalid_argument("modulus must be greater than 1");
        }

        if (
            parameters.base == 0 ||
            parameters.base >= parameters.modulus
        ) {
            throw invalid_argument(
                "base must be positive and smaller than modulus"
            );
        }

        prefix.assign(text.size() + 1, 0);
        power.assign(text.size() + 1, 1);

        for (size_t i = 0; i < text.size(); ++i) {
            /*
             * unsigned char avoids implementation-defined negative values
             * when char itself is signed.
             */
            uint64_t code =
                static_cast<unsigned char>(text[i]);

            prefix[i + 1] =
                (
                    prefix[i] * parameters.base +
                    code
                ) % parameters.modulus;

            power[i + 1] =
                (
                    power[i] * parameters.base
                ) % parameters.modulus;
        }
    }

    uint64_t substringHash(
        size_t left,
        size_t right
    ) const {
        if (left > right || right > text.size()) {
            throw out_of_range("invalid substring bounds");
        }

        /*
         * H(left:right) =
         *
         * prefix[right] -
         * prefix[left] * base^(right-left)
         *
         * modulo M.
         */
        uint64_t removed =
            (
                prefix[left] *
                power[right - left]
            ) % parameters.modulus;

        uint64_t result =
            (
                prefix[right] +
                parameters.modulus -
                removed
            ) % parameters.modulus;

        return result;
    }

    const string& getText() const {
        return text;
    }

    size_t size() const {
        return text.size();
    }
};

// -----------------------------------------------------------------------------
// 3. HASH PAIR
// -----------------------------------------------------------------------------

struct HashPair {
    uint64_t first;
    uint64_t second;

    bool operator==(const HashPair& other) const {
        return first == other.first &&
               second == other.second;
    }
};

struct HashPairHasher {
    size_t operator()(const HashPair& value) const {
        /*
         * The pair is used as an unordered_map key.
         * This is only the container's internal hash and is separate from
         * the two polynomial hashes used by the string algorithm.
         */
        size_t h1 = std::hash<uint64_t>{}(value.first);
        size_t h2 = std::hash<uint64_t>{}(value.second);

        return h1 ^ (
            h2 +
            static_cast<size_t>(0x9e3779b9) +
            (h1 << 6) +
            (h1 >> 2)
        );
    }
};

// -----------------------------------------------------------------------------
// 4. DOUBLE HASH INDEX
// -----------------------------------------------------------------------------

class DoubleHashIndex {
private:
    RollingHash first;
    RollingHash second;

public:
    explicit DoubleHashIndex(const string& text)
        : first(
            text,
            HashParameters{
                911382323ULL,
                972663749ULL
            }
        ),
          second(
            text,
            HashParameters{
                97266353ULL,
                1000000007ULL
            }
        ) {}

    HashPair substringHash(
        size_t left,
        size_t right
    ) const {
        return {
            first.substringHash(left, right),
            second.substringHash(left, right)
        };
    }

    bool equalSubstrings(
        size_t firstLeft,
        size_t firstRight,
        size_t secondLeft,
        size_t secondRight,
        bool verify = true
    ) const {
        if (
            firstRight - firstLeft !=
            secondRight - secondLeft
        ) {
            return false;
        }

        HashPair firstHash =
            substringHash(firstLeft, firstRight);

        HashPair secondHash =
            substringHash(secondLeft, secondRight);

        if (!(firstHash == secondHash)) {
            return false;
        }

        if (!verify) {
            return true;
        }

        /*
         * Hash equality is only a candidate equality.
         * Direct comparison provides exact correctness.
         */
        const string& text = first.getText();

        return text.compare(
            firstLeft,
            firstRight - firstLeft,
            text,
            secondLeft,
            secondRight - secondLeft
        ) == 0;
    }

    const string& getText() const {
        return first.getText();
    }

    size_t size() const {
        return first.size();
    }
};

// -----------------------------------------------------------------------------
// 5. DOCUMENT INDEX
// -----------------------------------------------------------------------------

class DocumentIndex {
private:
    string document;
    DoubleHashIndex hashes;

public:
    explicit DocumentIndex(const string& input)
        : document(input),
          hashes(input) {}

    vector<size_t> findPattern(
        const string& pattern
    ) const {
        vector<size_t> positions;

        if (pattern.empty()) {
            for (size_t i = 0; i <= document.size(); ++i) {
                positions.push_back(i);
            }
            return positions;
        }

        if (pattern.size() > document.size()) {
            return positions;
        }

        /*
         * Hash the pattern using the same parameters as the document.
         */
        RollingHash patternFirst(
            pattern,
            HashParameters{
                911382323ULL,
                972663749ULL
            }
        );

        RollingHash patternSecond(
            pattern,
            HashParameters{
                97266353ULL,
                1000000007ULL
            }
        );

        HashPair patternHash{
            patternFirst.substringHash(0, pattern.size()),
            patternSecond.substringHash(0, pattern.size())
        };

        for (
            size_t start = 0;
            start + pattern.size() <= document.size();
            ++start
        ) {
            size_t end = start + pattern.size();

            HashPair windowHash =
                hashes.substringHash(start, end);

            if (windowHash == patternHash) {
                /*
                 * Collision-safe verification.
                 */
                if (
                    document.compare(
                        start,
                        pattern.size(),
                        pattern
                    ) == 0
                ) {
                    positions.push_back(start);
                }
            }
        }

        return positions;
    }

    bool containsPattern(const string& pattern) const {
        return !findPattern(pattern).empty();
    }

    const string& getDocument() const {
        return document;
    }
};

// -----------------------------------------------------------------------------
// 6. DUPLICATE FRAGMENT DETECTOR
// -----------------------------------------------------------------------------

class DuplicateFragmentDetector {
private:
    const string& text;
    DoubleHashIndex hashes;

public:
    explicit DuplicateFragmentDetector(
        const string& input
    )
        : text(input),
          hashes(input) {}

    pair<size_t, size_t> findDuplicate(
        size_t length
    ) const {
        if (length > text.size()) {
            return {
                numeric_limits<size_t>::max(),
                numeric_limits<size_t>::max()
            };
        }

        if (length == 0) {
            return {0, 0};
        }

        /*
         * Hash -> candidate positions.
         *
         * We retain all positions associated with a hash because different
         * strings may collide.
         */
        unordered_map<
            HashPair,
            vector<size_t>,
            HashPairHasher
        > seen;

        for (
            size_t start = 0;
            start + length <= text.size();
            ++start
        ) {
            HashPair key =
                hashes.substringHash(start, start + length);

            auto& positions = seen[key];

            for (size_t previous : positions) {
                /*
                 * Exact verification makes this robust against hash
                 * collisions.
                 */
                if (
                    text.compare(
                        previous,
                        length,
                        text,
                        start,
                        length
                    ) == 0
                ) {
                    return {previous, start};
                }
            }

            positions.push_back(start);
        }

        return {
            numeric_limits<size_t>::max(),
            numeric_limits<size_t>::max()
        };
    }
};

// -----------------------------------------------------------------------------
// 7. LONGEST REPEATED FRAGMENT
// -----------------------------------------------------------------------------

class LongestRepeatedFragment {
private:
    const string& text;
    DoubleHashIndex hashes;

    pair<size_t, size_t> duplicateForLength(
        size_t length
    ) const {
        if (length == 0) {
            return {0, 0};
        }

        unordered_map<
            HashPair,
            vector<size_t>,
            HashPairHasher
        > seen;

        for (
            size_t start = 0;
            start + length <= text.size();
            ++start
        ) {
            HashPair key =
                hashes.substringHash(start, start + length);

            auto& positions = seen[key];

            for (size_t previous : positions) {
                if (
                    text.compare(
                        previous,
                        length,
                        text,
                        start,
                        length
                    ) == 0
                ) {
                    return {previous, start};
                }
            }

            positions.push_back(start);
        }

        return {
            numeric_limits<size_t>::max(),
            numeric_limits<size_t>::max()
        };
    }

public:
    explicit LongestRepeatedFragment(
        const string& input
    )
        : text(input),
          hashes(input) {}

    string find() const {
        if (text.empty()) {
            return "";
        }

        size_t low = 1;
        size_t high = text.size();
        size_t bestStart = 0;
        size_t bestLength = 0;

        /*
         * The predicate is monotonic:
         *
         * If a repeated substring of length L exists, then a repeated
         * substring of every smaller positive length also exists.
         *
         * This makes binary search possible.
         */
        while (low <= high) {
            size_t middle =
                low + (high - low) / 2;

            auto result =
                duplicateForLength(middle);

            if (
                result.first !=
                numeric_limits<size_t>::max()
            ) {
                bestStart = result.first;
                bestLength = middle;
                low = middle + 1;
            } else {
                high = middle - 1;
            }
        }

        return text.substr(
            bestStart,
            bestLength
        );
    }
};

// -----------------------------------------------------------------------------
// 8. WORD FREQUENCY INDEX
// -----------------------------------------------------------------------------

vector<string> splitWords(const string& text) {
    vector<string> words;
    string current;

    for (char character : text) {
        if (
            character == ' ' ||
            character == '\t' ||
            character == '\n' ||
            character == ',' ||
            character == '.' ||
            character == '!' ||
            character == '?' ||
            character == ';' ||
            character == ':'
        ) {
            if (!current.empty()) {
                words.push_back(current);
                current.clear();
            }
        } else {
            current += character;
        }
    }

    if (!current.empty()) {
        words.push_back(current);
    }

    return words;
}

map<string, size_t> buildWordFrequency(
    const string& document
) {
    map<string, size_t> frequencies;

    for (const string& word : splitWords(document)) {
        ++frequencies[word];
    }

    return frequencies;
}

// -----------------------------------------------------------------------------
// 9. APPLICATION CASE STUDY
// -----------------------------------------------------------------------------

void runDocumentCaseStudy() {
    cout << "\n=============================================\n";
    cout << "DOCUMENT INDEXING CASE STUDY\n";
    cout << "=============================================\n";

    const string document =
        "string hashing allows fast substring comparison; "
        "string hashing is useful in document indexing; "
        "substring comparison can support duplicate detection.";

    DocumentIndex index(document);

    vector<string> queries{
        "string hashing",
        "substring comparison",
        "duplicate",
        "missing phrase"
    };

    cout << "\nPattern searches:\n";

    for (const string& query : queries) {
        vector<size_t> positions =
            index.findPattern(query);

        cout << "Query: \"" << query << "\"";

        if (positions.empty()) {
            cout << " -> not found\n";
        } else {
            cout << " -> positions: ";

            for (size_t position : positions) {
                cout << position << ' ';
            }

            cout << '\n';
        }
    }

    cout << "\nRepeated fragments:\n";

    DuplicateFragmentDetector detector(document);

    for (size_t length : {5ULL, 10ULL, 15ULL}) {
        auto result = detector.findDuplicate(length);

        if (
            result.first ==
            numeric_limits<size_t>::max()
        ) {
            cout << "Length " << length
                 << ": none\n";
        } else {
            cout << "Length " << length
                 << ": \""
                 << document.substr(
                        result.first,
                        length
                    )
                 << "\" at "
                 << result.first
                 << " and "
                 << result.second
                 << '\n';
        }
    }

    cout << "\nLongest repeated fragment:\n";

    LongestRepeatedFragment longest(document);

    cout << "\"" << longest.find() << "\"\n";

    cout << "\nWord frequency index:\n";

    map<string, size_t> frequencies =
        buildWordFrequency(document);

    for (const auto& [word, count] : frequencies) {
        if (count > 1) {
            cout << word << ": " << count << '\n';
        }
    }
}

// -----------------------------------------------------------------------------
// 10. FUNDAMENTAL DEMONSTRATION
// -----------------------------------------------------------------------------

uint64_t simpleCharacterSumHash(
    const string& text
) {
    uint64_t result = 0;

    for (unsigned char character : text) {
        result += character;
    }

    return result;
}

void demonstrateCollision() {
    cout << "\n=============================================\n";
    cout << "COLLISION DEMONSTRATION\n";
    cout << "=============================================\n";

    string first = "abc";
    string second = "acb";

    cout << first << " -> "
         << simpleCharacterSumHash(first)
         << '\n';

    cout << second << " -> "
         << simpleCharacterSumHash(second)
         << '\n';

    cout << "Collision: "
         << (
                simpleCharacterSumHash(first) ==
                simpleCharacterSumHash(second)
            ? "yes"
            : "no"
         )
         << '\n';
}

// -----------------------------------------------------------------------------
// 11. PERFORMANCE AND TRADE-OFF EXPLANATION
// -----------------------------------------------------------------------------

void printDesignAnalysis() {
    cout << "\n=============================================\n";
    cout << "DESIGN AND COMPLEXITY ANALYSIS\n";
    cout << "=============================================\n";

    cout << R"(
Prefix-hash construction:
    Time:  O(n)
    Space: O(n)

Substring hash query:
    Time:  O(1)
    Space: O(1) additional per query

Rabin-Karp-style search:
    Typical: O(n + m)
    Worst case: O(n * m) if candidate collisions require extensive
                 verification.

Duplicate substring search for a fixed length:
    Expected near O(n), subject to hashing and collision behavior.

Longest repeated substring using binary search:
    Expected O(n log n) with the presented approach.

Trade-offs:
    - More memory buys constant-time substring hash queries.
    - Double hashing reduces accidental collision probability.
    - Direct verification eliminates false positives after a hash match.
    - A cryptographic hash is designed for different security properties.
    - Native string searching can outperform educational rolling-hash code
      because standard libraries are heavily optimized.
)";
}

// -----------------------------------------------------------------------------
// 12. VALIDATION
// -----------------------------------------------------------------------------

void runTests() {
    cout << "\n=============================================\n";
    cout << "SELF-TESTS\n";
    cout << "=============================================\n";

    if (simpleCharacterSumHash("abc") !=
        simpleCharacterSumHash("acb")) {
        throw runtime_error(
            "basic collision test failed"
        );
    }

    RollingHash hash(
        "abcdef",
        HashParameters{
            257,
            1000000007ULL
        }
    );

    RollingHash abcHash(
        "abc",
        HashParameters{
            257,
            1000000007ULL
        }
    );

    if (
        hash.substringHash(0, 3) !=
        abcHash.substringHash(0, 3)
    ) {
        throw runtime_error(
            "substring hash test failed"
        );
    }

    DocumentIndex index("aaaaa");

    vector<size_t> matches =
        index.findPattern("aaa");

    vector<size_t> expected{
        0,
        1,
        2
    };

    if (matches != expected) {
        throw runtime_error(
            "Rabin-Karp matching test failed"
        );
    }

    DuplicateFragmentDetector detector("aaaa");

    auto duplicate =
        detector.findDuplicate(3);

    if (
        duplicate.first != 0 ||
        duplicate.second != 1
    ) {
        throw runtime_error(
            "duplicate detection test failed"
        );
    }

    LongestRepeatedFragment longest("aaaa");

    if (longest.find() != "aaa") {
        throw runtime_error(
            "longest repeated fragment test failed"
        );
    }

    if (!index.containsPattern("aa")) {
        throw runtime_error(
            "contains pattern test failed"
        );
    }

    if (index.containsPattern("xyz")) {
        throw runtime_error(
            "missing pattern test failed"
        );
    }

    cout << "All C++ self-tests passed.\n";
}

// -----------------------------------------------------------------------------
// 13. MAIN
// -----------------------------------------------------------------------------

int main() {
    try {
        demonstrateCollision();

        cout << "\n=============================================\n";
        cout << "BASIC POLYNOMIAL HASH\n";
        cout << "=============================================\n";

        const string sample = "hello";

        RollingHash sampleHash(
            sample,
            HashParameters{
                257,
                1000000007ULL
            }
        );

        cout << "Text: " << sample << '\n';
        cout << "Full hash: "
             << sampleHash.substringHash(
                    0,
                    sample.size()
                )
             << '\n';

        cout << "Hash of \"ell\": "
             << sampleHash.substringHash(1, 4)
             << '\n';

        runDocumentCaseStudy();
        printDesignAnalysis();
        runTests();

        cout << "\nSecurity distinction:\n";
        cout << "Polynomial rolling hashes are algorithmic tools, not password "
                "hashes or general cryptographic authentication primitives.\n";

        return 0;
    } catch (const exception& error) {
        cerr << "Fatal error: "
             << error.what()
             << '\n';

        return 1;
    }
}
