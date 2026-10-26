#include <algorithm>
#include <exception>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <vector>

using namespace std;

class PermutationError : public runtime_error {
public:
    explicit PermutationError(const string& message)
        : runtime_error(message) {}
};

class PermutationEngine {
public:
    explicit PermutationEngine(vector<string> values)
        : values_(move(values)) {
        validate();
    }

    size_t uniquePermutationCount() const {
        vector<string> sorted = values_;
        sort(sorted.begin(), sorted.end());

        size_t result = factorial(sorted.size());

        for (size_t i = 0; i < sorted.size();) {
            size_t j = i + 1;
            while (j < sorted.size() && sorted[j] == sorted[i]) {
                ++j;
            }

            result /= factorial(j - i);
            i = j;
        }

        return result;
    }

    vector<vector<string>> generateSwapBased() {
        vector<vector<string>> result;
        swapBacktrack(0, result);
        return result;
    }

    vector<vector<string>> generateUsedArray() const {
        vector<vector<string>> result;
        vector<bool> used(values_.size(), false);
        vector<string> current;

        usedBacktrack(used, current, result);
        return result;
    }

private:
    vector<string> values_;

    static size_t factorial(size_t n) {
        size_t result = 1;

        for (size_t i = 2; i <= n; ++i) {
            if (result > 1000000000ULL / i) {
                throw PermutationError(
                    "Permutation count exceeds supported arithmetic range.");
            }
            result *= i;
        }

        return result;
    }

    void validate() const {
        if (values_.size() > 9) {
            throw PermutationError(
                "Exhaustive permutation generation is limited to 9 elements.");
        }
    }

    void swapBacktrack(size_t start, vector<vector<string>>& result) {
        if (start == values_.size()) {
            result.push_back(values_);
            return;
        }

        /*
         * A set at each recursion depth prevents equal values from occupying
         * the same position through separate branches.
         */
        set<string> usedAtLevel;

        for (size_t i = start; i < values_.size(); ++i) {
            if (!usedAtLevel.insert(values_[i]).second) {
                continue;
            }

            swap(values_[start], values_[i]);

            swapBacktrack(start + 1, result);

            swap(values_[start], values_[i]);
        }
    }

    void usedBacktrack(
        vector<bool>& used,
        vector<string>& current,
        vector<vector<string>>& result
    ) const {
        if (current.size() == values_.size()) {
            result.push_back(current);
            return;
        }

        /*
         * Since values are sorted, equal unused values appear together.
         * This local set prevents duplicate branches at the current depth.
         */
        set<string> usedAtLevel;

        for (size_t i = 0; i < values_.size(); ++i) {
            if (used[i]) {
                continue;
            }

            if (!usedAtLevel.insert(values_[i]).second) {
                continue;
            }

            used[i] = true;
            current.push_back(values_[i]);

            usedBacktrack(used, current, result);

            current.pop_back();
            used[i] = false;
        }
    }
};

void printPermutations(const vector<vector<string>>& permutations) {
    cout << "[\n";

    for (const auto& permutation : permutations) {
        cout << "  [";

        for (size_t i = 0; i < permutation.size(); ++i) {
            cout << '"' << permutation[i] << '"';
            if (i + 1 < permutation.size()) {
                cout << ", ";
            }
        }

        cout << "]\n";
    }

    cout << "]\n";
}

void verify(
    const vector<vector<string>>& permutations,
    size_t expected
) {
    if (permutations.size() != expected) {
        throw logic_error("Generated permutation count is incorrect.");
    }

    set<vector<string>> unique(permutations.begin(), permutations.end());

    if (unique.size() != expected) {
        throw logic_error("Duplicate permutations were generated.");
    }
}

int main() {
    try {
        vector<vector<string>> examples = {
            {"A", "B", "C"},
            {"A", "A", "B"},
            {"1", "2", "3", "4"}
        };

        for (const auto& input : examples) {
            PermutationEngine engine(input);

            const size_t expected = engine.uniquePermutationCount();

            cout << "\nInput: ";
            for (const auto& value : input) {
                cout << value << ' ';
            }
            cout << "\nExpected unique permutations: " << expected << '\n';

            auto swapResult = engine.generateSwapBased();
            auto usedResult = engine.generateUsedArray();

            verify(swapResult, expected);
            verify(usedResult, expected);

            cout << "\nSwap-based generation:\n";
            printPermutations(swapResult);

            cout << "\nUsed-array generation:\n";
            printPermutations(usedResult);
        }

        cout << "\nEdge case: empty input\n";
        PermutationEngine empty({});
        auto emptyResult = empty.generateSwapBased();

        if (emptyResult.size() != 1 || !emptyResult[0].empty()) {
            throw logic_error("Empty input should have exactly one permutation.");
        }

        cout << "Empty input correctly produces one empty permutation.\n";

        cout << "\nPerformance:\n";
        cout << "For n distinct elements, n! permutations are produced.\n";
        cout << "Materializing all results costs O(n * n!) output work.\n";
        cout << "Recursive working memory is O(n), excluding stored results.\n";

    } catch (const exception& error) {
        cerr << "Error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
