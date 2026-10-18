#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

using IndexPair = pair<size_t, size_t>;
using ValuePair = pair<long long, long long>;

class PairAnalytics {
public:
    // A warehouse reconciliation system uses integer-cent amounts.
    // Each record retains its original position so repeated amounts
    // represent different transactions rather than duplicate identities.

    static optional<IndexPair> findTwoSum(
        const vector<long long>& amounts,
        long long target
    ) {
        unordered_map<long long, size_t> earliestIndex;
        earliestIndex.reserve(amounts.size());

        for (size_t right = 0; right < amounts.size(); ++right) {
            const long long value = amounts[right];
            const __int128 complementWide =
                static_cast<__int128>(target) - value;

            // Widened arithmetic prevents signed overflow during subtraction.
            if (complementWide >= numeric_limits<long long>::min() &&
                complementWide <= numeric_limits<long long>::max()) {
                const long long complement =
                    static_cast<long long>(complementWide);

                auto match = earliestIndex.find(complement);
                if (match != earliestIndex.end()) {
                    return IndexPair{match->second, right};
                }
            }

            earliestIndex.emplace(value, right);
        }

        return nullopt;
    }

    static vector<IndexPair> findAllPairs(
        const vector<long long>& amounts,
        long long target
    ) {
        unordered_map<long long, vector<size_t>> indicesByAmount;
        vector<IndexPair> result;

        for (size_t right = 0; right < amounts.size(); ++right) {
            const long long value = amounts[right];
            const __int128 complementWide =
                static_cast<__int128>(target) - value;

            if (complementWide >= numeric_limits<long long>::min() &&
                complementWide <= numeric_limits<long long>::max()) {
                const long long complement =
                    static_cast<long long>(complementWide);

                auto matches = indicesByAmount.find(complement);
                if (matches != indicesByAmount.end()) {
                    for (size_t left : matches->second) {
                        result.emplace_back(left, right);
                    }
                }
            }

            indicesByAmount[value].push_back(right);
        }

        return result;
    }

    static unsigned long long countPairs(
        const vector<long long>& amounts,
        long long target
    ) {
        unordered_map<long long, unsigned long long> frequency;
        frequency.reserve(amounts.size());

        unsigned long long count = 0;

        for (long long value : amounts) {
            const __int128 complementWide =
                static_cast<__int128>(target) - value;

            if (complementWide >= numeric_limits<long long>::min() &&
                complementWide <= numeric_limits<long long>::max()) {
                const long long complement =
                    static_cast<long long>(complementWide);

                auto found = frequency.find(complement);
                if (found != frequency.end()) {
                    if (numeric_limits<unsigned long long>::max() - count
                        < found->second) {
                        throw overflow_error("Pair count exceeds supported range");
                    }
                    count += found->second;
                }
            }

            ++frequency[value];
        }

        return count;
    }

    static vector<ValuePair> uniqueValuePairs(
        const vector<long long>& amounts,
        long long target
    ) {
        unordered_map<long long, size_t> frequency;
        for (long long value : amounts) {
            ++frequency[value];
        }

        vector<long long> values;
        values.reserve(frequency.size());

        for (const auto& entry : frequency) {
            values.push_back(entry.first);
        }

        sort(values.begin(), values.end());

        vector<ValuePair> result;

        for (long long value : values) {
            const __int128 complementWide =
                static_cast<__int128>(target) - value;

            if (complementWide < numeric_limits<long long>::min() ||
                complementWide > numeric_limits<long long>::max()) {
                continue;
            }

            const long long complement =
                static_cast<long long>(complementWide);

            if (complement < value) {
                continue;
            }

            auto found = frequency.find(complement);
            if (found == frequency.end()) {
                continue;
            }

            if (complement == value && frequency[value] < 2) {
                continue;
            }

            result.emplace_back(value, complement);
        }

        return result;
    }

    static optional<IndexPair> findSignedDifference(
        const vector<long long>& values,
        long long difference
    ) {
        unordered_map<long long, size_t> earliestIndex;
        earliestIndex.reserve(values.size());

        for (size_t right = 0; right < values.size(); ++right) {
            const __int128 requiredWide =
                static_cast<__int128>(values[right]) - difference;

            if (requiredWide >= numeric_limits<long long>::min() &&
                requiredWide <= numeric_limits<long long>::max()) {
                const long long required = static_cast<long long>(requiredWide);

                auto found = earliestIndex.find(required);
                if (found != earliestIndex.end()) {
                    return IndexPair{found->second, right};
                }
            }

            earliestIndex.emplace(values[right], right);
        }

        return nullopt;
    }

    static optional<IndexPair> findAbsoluteDifference(
        const vector<long long>& values,
        long long difference
    ) {
        if (difference < 0) {
            throw invalid_argument("Absolute difference cannot be negative");
        }

        unordered_map<long long, size_t> earliestIndex;
        earliestIndex.reserve(values.size());

        for (size_t right = 0; right < values.size(); ++right) {
            const long long value = values[right];
            vector<long long> candidates;

            if (difference == 0) {
                candidates.push_back(value);
            } else {
                const __int128 lower =
                    static_cast<__int128>(value) - difference;
                const __int128 upper =
                    static_cast<__int128>(value) + difference;

                if (lower >= numeric_limits<long long>::min() &&
                    lower <= numeric_limits<long long>::max()) {
                    candidates.push_back(static_cast<long long>(lower));
                }

                if (upper >= numeric_limits<long long>::min() &&
                    upper <= numeric_limits<long long>::max()) {
                    candidates.push_back(static_cast<long long>(upper));
                }
            }

            for (long long candidate : candidates) {
                auto found = earliestIndex.find(candidate);
                if (found != earliestIndex.end()) {
                    return IndexPair{found->second, right};
                }
            }

            earliestIndex.emplace(value, right);
        }

        return nullopt;
    }

    static optional<IndexPair> findSortedTwoSum(
        const vector<long long>& sortedValues,
        long long target
    ) {
        if (!is_sorted(sortedValues.begin(), sortedValues.end())) {
            throw invalid_argument("Input must be sorted in ascending order");
        }

        if (sortedValues.size() < 2) {
            return nullopt;
        }

        size_t left = 0;
        size_t right = sortedValues.size() - 1;

        while (left < right) {
            const __int128 sum =
                static_cast<__int128>(sortedValues[left]) +
                sortedValues[right];

            if (sum == target) {
                return IndexPair{left, right};
            }

            if (sum < target) {
                ++left;
            } else {
                --right;
            }
        }

        return nullopt;
    }
};

void printPair(
    const string& description,
    const optional<IndexPair>& result
) {
    cout << description << ": ";

    if (!result) {
        cout << "no matching pair\n";
        return;
    }

    cout << "indices (" << result->first << ", " << result->second << ")\n";
}

int main() {
    // Reconciliation identifies two line items that explain a discrepancy.
    const vector<long long> ledgerCents = {
        12500, 27500, 8000, 20000, 12500
    };
    const long long budgetCents = 40000;

    printPair(
        "First pair matching the budget",
        PairAnalytics::findTwoSum(ledgerCents, budgetCents)
    );

    const auto allPairs =
        PairAnalytics::findAllPairs(ledgerCents, budgetCents);

    cout << "All matching index pairs: " << allPairs.size() << '\n';
    for (const auto& pair : allPairs) {
        cout << "  (" << pair.first << ", " << pair.second << ")\n";
    }

    cout << "Pair count: "
         << PairAnalytics::countPairs(ledgerCents, budgetCents) << '\n';

    cout << "Distinct value pairs:\n";
    for (const auto& pair :
         PairAnalytics::uniqueValuePairs(ledgerCents, budgetCents)) {
        cout << "  " << pair.first << " + " << pair.second << '\n';
    }

    printPair(
        "Signed difference of 7500 cents",
        PairAnalytics::findSignedDifference(ledgerCents, 7500)
    );

    printPair(
        "Absolute difference of 7500 cents",
        PairAnalytics::findAbsoluteDifference(ledgerCents, 7500)
    );

    const vector<long long> sortedValues = {-500, -100, 200, 700};
    printPair(
        "Sorted two-pointer lookup for 200 cents",
        PairAnalytics::findSortedTwoSum(sortedValues, 200)
    );

    // Edge cases distinguish an equal value from two separate records.
    assert(PairAnalytics::findTwoSum({4}, 8) == nullopt);
    assert(PairAnalytics::findTwoSum({4, 4}, 8) == IndexPair(0, 1));
    assert(PairAnalytics::countPairs({2, 2, 2, 2}, 4) == 6);
    assert(PairAnalytics::countPairs({-2, -1, 0, 1, 2}, 0) == 2);
    assert(PairAnalytics::findAbsoluteDifference({5}, 0) == nullopt);
    assert(PairAnalytics::findAbsoluteDifference({5, 5}, 0)
           == IndexPair(0, 1));

    bool rejectedNegativeDifference = false;
    try {
        PairAnalytics::findAbsoluteDifference({1, 2}, -1);
    } catch (const invalid_argument&) {
        rejectedNegativeDifference = true;
    }
    assert(rejectedNegativeDifference);

    bool rejectedUnsortedInput = false;
    try {
        PairAnalytics::findSortedTwoSum({2, 1}, 3);
    } catch (const invalid_argument&) {
        rejectedUnsortedInput = true;
    }
    assert(rejectedUnsortedInput);

    cout << "All C++ governance-case tests passed.\n";
    return 0;
}
