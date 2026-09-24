#include <algorithm>
#include <chrono>
#include <cctype>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

/*
 * Day 22 — Palindromes
 *
 * Industry-style case study:
 *
 * A text-analysis service receives user-generated identifiers and messages.
 * It must:
 *
 *   1. Validate palindrome properties.
 *   2. Support punctuation-insensitive palindrome checks.
 *   3. Detect whether one character can be removed to produce a palindrome.
 *   4. Find the longest palindromic substring.
 *   5. Report distinct palindromic substrings for small inputs.
 *   6. Handle invalid or excessive input safely.
 *   7. Expose complexity-conscious implementations.
 *
 * C++17 standard library only.
 *
 * The architecture separates:
 *   - validation
 *   - algorithms
 *   - domain model
 *   - service orchestration
 *   - reporting
 *
 * This demonstrates how palindrome algorithms can become part of a
 * maintainable application rather than remaining isolated interview snippets.
 */


// ============================================================
// DOMAIN MODEL
// ============================================================

struct PalindromeReport {
    std::string input;
    bool exactPalindrome{};
    bool validPalindrome{};
    bool removableOnePalindrome{};
    std::string longestPalindromicSubstring;
    std::size_t distinctPalindromicSubstringCount{};
};


// ============================================================
// INPUT VALIDATION
// ============================================================

class InputValidator {
public:
    static void validateText(
        const std::string& text,
        std::size_t maximumLength
    ) {
        if (text.size() > maximumLength) {
            throw std::invalid_argument(
                "Input exceeds the configured maximum length."
            );
        }
    }
};


// ============================================================
// BASIC PALINDROME ALGORITHMS
// ============================================================

class PalindromeAlgorithms {
public:

    static bool isPalindrome(std::string_view text) {
        if (text.empty()) {
            return true;
        }

        std::size_t left = 0;
        std::size_t right = text.size() - 1;

        while (left < right) {
            if (text[left] != text[right]) {
                return false;
            }

            ++left;
            --right;
        }

        return true;
    }


    static bool isValidPalindrome(std::string_view text) {
        /*
         * This implementation intentionally operates on ASCII letters and
         * digits because std::isalnum depends on locale and operates on
         * unsigned-char values. Production Unicode normalization requires
         * a dedicated Unicode-aware layer.
         */
        std::size_t left = 0;
        std::size_t right = text.empty() ? 0 : text.size() - 1;

        while (left < right) {
            while (
                left < right &&
                !std::isalnum(
                    static_cast<unsigned char>(text[left])
                )
            ) {
                ++left;
            }

            while (
                left < right &&
                !std::isalnum(
                    static_cast<unsigned char>(text[right])
                )
            ) {
                --right;
            }

            const unsigned char leftCharacter =
                static_cast<unsigned char>(text[left]);

            const unsigned char rightCharacter =
                static_cast<unsigned char>(text[right]);

            if (
                std::tolower(leftCharacter) !=
                std::tolower(rightCharacter)
            ) {
                return false;
            }

            ++left;
            --right;
        }

        return true;
    }


    static bool canBecomePalindromeAfterRemovingOne(
        std::string_view text
    ) {
        auto rangeIsPalindrome = [&](std::size_t left,
                                     std::size_t right) {
            while (left < right) {
                if (text[left] != text[right]) {
                    return false;
                }

                ++left;
                --right;
            }

            return true;
        };

        if (text.empty()) {
            return true;
        }

        std::size_t left = 0;
        std::size_t right = text.size() - 1;

        while (left < right) {
            if (text[left] != text[right]) {
                return (
                    rangeIsPalindrome(left + 1, right) ||
                    rangeIsPalindrome(left, right - 1)
                );
            }

            ++left;
            --right;
        }

        return true;
    }


    static bool isSubstringPalindrome(
        std::string_view text,
        std::size_t start,
        std::size_t endExclusive
    ) {
        if (
            start > endExclusive ||
            endExclusive > text.size()
        ) {
            throw std::out_of_range(
                "Invalid substring boundaries."
            );
        }

        if (start == endExclusive) {
            return true;
        }

        std::size_t left = start;
        std::size_t right = endExclusive - 1;

        while (left < right) {
            if (text[left] != text[right]) {
                return false;
            }

            ++left;
            --right;
        }

        return true;
    }


    // ========================================================
    // CENTER EXPANSION
    // ========================================================

    static std::pair<std::size_t, std::size_t> expandAroundCenter(
        std::string_view text,
        std::size_t left,
        std::size_t right
    ) {
        /*
         * Signed indices are used internally because expansion can move
         * beyond index zero. The returned values are converted to a
         * half-open [start, end) interval.
         */
        long long l = static_cast<long long>(left);
        long long r = static_cast<long long>(right);
        const long long n = static_cast<long long>(text.size());

        while (
            l >= 0 &&
            r < n &&
            text[static_cast<std::size_t>(l)] ==
            text[static_cast<std::size_t>(r)]
        ) {
            --l;
            ++r;
        }

        return {
            static_cast<std::size_t>(l + 1),
            static_cast<std::size_t>(r)
        };
    }


    static std::string longestPalindromeCenter(
        std::string_view text
    ) {
        if (text.empty()) {
            return {};
        }

        std::size_t bestStart = 0;
        std::size_t bestEnd = 1;

        for (std::size_t center = 0;
             center < text.size();
             ++center) {

            auto [start, end] =
                expandAroundCenter(text, center, center);

            if (
                end - start >
                bestEnd - bestStart
            ) {
                bestStart = start;
                bestEnd = end;
            }

            if (center + 1 < text.size()) {
                std::tie(start, end) =
                    expandAroundCenter(
                        text,
                        center,
                        center + 1
                    );

                if (
                    end - start >
                    bestEnd - bestStart
                ) {
                    bestStart = start;
                    bestEnd = end;
                }
            }
        }

        return std::string(
            text.substr(bestStart, bestEnd - bestStart)
        );
    }


    // ========================================================
    // DYNAMIC PROGRAMMING
    // ========================================================

    static std::string longestPalindromeDP(
        std::string_view text
    ) {
        const std::size_t n = text.size();

        if (n == 0) {
            return {};
        }

        /*
         * A vector<vector<bool>> is compact but can have specialized
         * bitset-like behavior. For readability this implementation uses
         * a byte matrix.
         */
        std::vector<std::vector<unsigned char>> dp(
            n,
            std::vector<unsigned char>(n, 0)
        );

        std::size_t bestStart = 0;
        std::size_t bestLength = 1;

        for (std::size_t index = 0; index < n; ++index) {
            dp[index][index] = 1;
        }

        for (std::size_t length = 2; length <= n; ++length) {
            for (
                std::size_t left = 0;
                left + length <= n;
                ++left
            ) {
                const std::size_t right =
                    left + length - 1;

                if (
                    text[left] == text[right] &&
                    (
                        length == 2 ||
                        dp[left + 1][right - 1]
                    )
                ) {
                    dp[left][right] = 1;

                    if (length > bestLength) {
                        bestStart = left;
                        bestLength = length;
                    }
                }
            }
        }

        return std::string(
            text.substr(bestStart, bestLength)
        );
    }


    // ========================================================
    // MANACHER'S ALGORITHM
    // ========================================================

    static std::string longestPalindromeManacher(
        std::string_view text
    ) {
        if (text.empty()) {
            return {};
        }

        /*
         * Transformed representation:
         *
         *   ^#a#b#b#a#$
         *
         * '#' unifies odd and even palindrome cases.
         * '^' and '$' act as sentinels.
         */
        std::string transformed;
        transformed.reserve(text.size() * 2 + 3);

        transformed.push_back('^');

        for (char character : text) {
            transformed.push_back('#');
            transformed.push_back(character);
        }

        transformed.push_back('#');
        transformed.push_back('$');

        std::vector<std::size_t> radius(
            transformed.size(),
            0
        );

        std::size_t center = 0;
        std::size_t rightBoundary = 0;

        for (
            std::size_t index = 1;
            index + 1 < transformed.size();
            ++index
        ) {
            const long long mirror =
                2LL * static_cast<long long>(center) -
                static_cast<long long>(index);

            if (
                index < rightBoundary &&
                mirror >= 0
            ) {
                radius[index] = std::min(
                    rightBoundary - index,
                    radius[
                        static_cast<std::size_t>(mirror)
                    ]
                );
            }

            while (
                transformed[
                    index + 1 + radius[index]
                ] ==
                transformed[
                    index - 1 - radius[index]
                ]
            ) {
                ++radius[index];
            }

            if (
                index + radius[index] >
                rightBoundary
            ) {
                center = index;
                rightBoundary =
                    index + radius[index];
            }
        }

        std::size_t bestCenter = 0;
        std::size_t bestRadius = 0;

        for (
            std::size_t index = 0;
            index < radius.size();
            ++index
        ) {
            if (radius[index] > bestRadius) {
                bestRadius = radius[index];
                bestCenter = index;
            }
        }

        /*
         * With this transformation, the original starting position is
         * (center - radius) / 2.
         */
        const std::size_t start =
            (bestCenter - bestRadius) / 2;

        return std::string(
            text.substr(start, bestRadius)
        );
    }


    // ========================================================
    // DISTINCT PALINDROMIC SUBSTRINGS
    // ========================================================

    static std::unordered_set<std::string>
    distinctPalindromicSubstrings(
        std::string_view text
    ) {
        std::unordered_set<std::string> result;

        for (
            std::size_t center = 0;
            center < text.size();
            ++center
        ) {
            long long left =
                static_cast<long long>(center);

            long long right =
                static_cast<long long>(center);

            while (
                left >= 0 &&
                right < static_cast<long long>(text.size()) &&
                text[static_cast<std::size_t>(left)] ==
                text[static_cast<std::size_t>(right)]
            ) {
                result.emplace(
                    text.substr(
                        static_cast<std::size_t>(left),
                        static_cast<std::size_t>(
                            right - left + 1
                        )
                    )
                );

                --left;
                ++right;
            }

            left = static_cast<long long>(center);
            right = static_cast<long long>(center + 1);

            while (
                left >= 0 &&
                right < static_cast<long long>(text.size()) &&
                text[static_cast<std::size_t>(left)] ==
                text[static_cast<std::size_t>(right)]
            ) {
                result.emplace(
                    text.substr(
                        static_cast<std::size_t>(left),
                        static_cast<std::size_t>(
                            right - left + 1
                        )
                    )
                );

                --left;
                ++right;
            }
        }

        return result;
    }


    // ========================================================
    // PALINDROMIC SUBSEQUENCE
    // ========================================================

    static std::size_t longestPalindromicSubsequenceLength(
        std::string_view text
    ) {
        const std::size_t n = text.size();

        if (n == 0) {
            return 0;
        }

        std::vector<std::vector<std::size_t>> dp(
            n,
            std::vector<std::size_t>(n, 0)
        );

        for (std::size_t index = 0; index < n; ++index) {
            dp[index][index] = 1;
        }

        for (std::size_t length = 2; length <= n; ++length) {
            for (
                std::size_t left = 0;
                left + length <= n;
                ++left
            ) {
                const std::size_t right =
                    left + length - 1;

                if (text[left] == text[right]) {
                    dp[left][right] =
                        length == 2
                            ? 2
                            : dp[left + 1][right - 1] + 2;
                } else {
                    dp[left][right] = std::max(
                        dp[left + 1][right],
                        dp[left][right - 1]
                    );
                }
            }
        }

        return dp[0][n - 1];
    }
};


// ============================================================
// PALINDROME SERVICE
// ============================================================

class PalindromeAnalysisService {
public:
    explicit PalindromeAnalysisService(
        std::size_t maximumInputLength = 100000
    )
        : maximumInputLength_(maximumInputLength) {}


    PalindromeReport analyze(
        const std::string& text
    ) const {
        InputValidator::validateText(
            text,
            maximumInputLength_
        );

        PalindromeReport report;
        report.input = text;

        report.exactPalindrome =
            PalindromeAlgorithms::isPalindrome(text);

        report.validPalindrome =
            PalindromeAlgorithms::isValidPalindrome(text);

        report.removableOnePalindrome =
            PalindromeAlgorithms::
            canBecomePalindromeAfterRemovingOne(text);

        report.longestPalindromicSubstring =
            PalindromeAlgorithms::
            longestPalindromeCenter(text);

        /*
         * Collecting all distinct palindromic substrings can consume
         * substantial memory. The service therefore limits this operation
         * to a smaller input size.
         */
        if (text.size() <= 2000) {
            report.distinctPalindromicSubstringCount =
                PalindromeAlgorithms::
                distinctPalindromicSubstrings(text).size();
        } else {
            report.distinctPalindromicSubstringCount = 0;
        }

        return report;
    }

private:
    std::size_t maximumInputLength_;
};


// ============================================================
// REPORTING
// ============================================================

void printReport(
    const PalindromeReport& report
) {
    std::cout
        << "\nInput: "
        << report.input
        << '\n';

    std::cout
        << "Exact palindrome: "
        << std::boolalpha
        << report.exactPalindrome
        << '\n';

    std::cout
        << "Valid palindrome: "
        << report.validPalindrome
        << '\n';

    std::cout
        << "Palindrome after removing at most one character: "
        << report.removableOnePalindrome
        << '\n';

    std::cout
        << "Longest palindromic substring: "
        << report.longestPalindromicSubstring
        << '\n';

    if (report.distinctPalindromicSubstringCount != 0) {
        std::cout
            << "Distinct palindromic substrings: "
            << report.distinctPalindromicSubstringCount
            << '\n';
    } else {
        std::cout
            << "Distinct palindromic substrings: "
            << "skipped for large input"
            << '\n';
    }
}


// ============================================================
// TESTING
// ============================================================

void require(
    bool condition,
    const std::string& description
) {
    if (!condition) {
        throw std::runtime_error(
            "Test failed: " + description
        );
    }
}


void runTests() {
    require(
        PalindromeAlgorithms::isPalindrome("racecar"),
        "racecar should be a palindrome"
    );

    require(
        !PalindromeAlgorithms::isPalindrome("hello"),
        "hello should not be a palindrome"
    );

    require(
        PalindromeAlgorithms::isValidPalindrome(
            "A man, a plan, a canal: Panama"
        ),
        "valid palindrome"
    );

    require(
        !PalindromeAlgorithms::isValidPalindrome(
            "race a car"
        ),
        "invalid palindrome"
    );

    require(
        PalindromeAlgorithms::
        canBecomePalindromeAfterRemovingOne("abca"),
        "abca can become a palindrome"
    );

    require(
        !PalindromeAlgorithms::
        canBecomePalindromeAfterRemovingOne("abc"),
        "abc cannot become a palindrome by one removal"
    );

    require(
        PalindromeAlgorithms::
        longestPalindromeCenter("cbbd") == "bb",
        "center expansion cbbd"
    );

    require(
        PalindromeAlgorithms::
        longestPalindromeDP("cbbd") == "bb",
        "DP cbbd"
    );

    require(
        PalindromeAlgorithms::
        longestPalindromeManacher("cbbd") == "bb",
        "Manacher cbbd"
    );

    require(
        PalindromeAlgorithms::
        longestPalindromicSubsequenceLength("bbbab") == 4,
        "longest palindromic subsequence"
    );

    require(
        PalindromeAlgorithms::
        isSubstringPalindrome("racecar", 1, 6),
        "aceca substring"
    );

    std::cout << "All C++ tests passed.\n";
}


// ============================================================
// ALGORITHM COMPARISON
// ============================================================

void benchmarkLongestPalindrome() {
    std::string input;

    for (int index = 0; index < 8; ++index) {
        input += "abacabadabacaba";
    }

    std::cout
        << "\nLongest-palindrome benchmark"
        << "\nInput length: "
        << input.size()
        << '\n';

    {
        const auto start =
            std::chrono::steady_clock::now();

        const std::string result =
            PalindromeAlgorithms::
            longestPalindromeCenter(input);

        const auto finish =
            std::chrono::steady_clock::now();

        const auto elapsed =
            std::chrono::duration<double, std::milli>(
                finish - start
            ).count();

        std::cout
            << "Center expansion: "
            << elapsed
            << " ms, result length="
            << result.size()
            << '\n';
    }

    {
        const auto start =
            std::chrono::steady_clock::now();

        const std::string result =
            PalindromeAlgorithms::
            longestPalindromeDP(input);

        const auto finish =
            std::chrono::steady_clock::now();

        const auto elapsed =
            std::chrono::duration<double, std::milli>(
                finish - start
            ).count();

        std::cout
            << "Dynamic programming: "
            << elapsed
            << " ms, result length="
            << result.size()
            << '\n';
    }

    {
        const auto start =
            std::chrono::steady_clock::now();

        const std::string result =
            PalindromeAlgorithms::
            longestPalindromeManacher(input);

        const auto finish =
            std::chrono::steady_clock::now();

        const auto elapsed =
            std::chrono::duration<double, std::milli>(
                finish - start
            ).count();

        std::cout
            << "Manacher: "
            << elapsed
            << " ms, result length="
            << result.size()
            << '\n';
    }
}


// ============================================================
// INTERACTIVE INPUT
// ============================================================

std::string readLineSafely() {
    std::string input;

    if (!std::getline(std::cin, input)) {
        throw std::runtime_error(
            "Unable to read input."
        );
    }

    return input;
}


// ============================================================
// MAIN
// ============================================================

int main() {
    try {
        std::cout
            << "============================================================\n"
            << "DAY 22 — PALINDROMES\n"
            << "============================================================\n";

        runTests();

        PalindromeAnalysisService service(
            100000
        );

        const std::vector<std::string> examples = {
            "racecar",
            "hello",
            "A man, a plan, a canal: Panama",
            "abca",
            "cbbd",
            "forgeeksskeegfor"
        };

        for (const auto& example : examples) {
            printReport(
                service.analyze(example)
            );
        }

        std::cout
            << "\nSubstring example:\n";

        const std::string sample =
            "racecar";

        std::cout
            << "sample[1..6) = "
            << sample.substr(1, 5)
            << ", palindrome="
            << std::boolalpha
            << PalindromeAlgorithms::
               isSubstringPalindrome(sample, 1, 6)
            << '\n';

        std::cout
            << "\nLongest palindromic subsequence:\n";

        const std::string subsequenceInput =
            "bbbab";

        std::cout
            << subsequenceInput
            << " -> length "
            << PalindromeAlgorithms::
               longestPalindromicSubsequenceLength(
                   subsequenceInput
               )
            << '\n';

        std::cout
            << "\nOptional interactive analysis.\n"
            << "Enter a line of text and press Enter.\n"
            << "Press Ctrl+Z followed by Enter on Windows to skip.\n"
            << "> ";

        if (std::cin.peek() != EOF) {
            std::string userInput;

            if (std::getline(std::cin, userInput)) {
                printReport(
                    service.analyze(userInput)
                );
            }
        }

        benchmarkLongestPalindrome();

        std::cout
            << "\nComplexity reference:\n"
            << "Two-pointer palindrome check: O(n) time, O(1) space.\n"
            << "Remove-one-character check: O(n) time, O(1) space.\n"
            << "Center expansion: O(n^2) time, O(1) auxiliary space.\n"
            << "Dynamic programming: O(n^2) time, O(n^2) space.\n"
            << "Manacher's algorithm: O(n) time, O(n) space.\n"
            << "Palindrome partitioning can have exponential output size.\n";

        return 0;
    }
    catch (const std::exception& error) {
        std::cerr
            << "Application error: "
            << error.what()
            << '\n';

        return 1;
    }
}
