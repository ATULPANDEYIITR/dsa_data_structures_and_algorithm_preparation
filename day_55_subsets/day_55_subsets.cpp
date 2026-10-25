#include <algorithm>
#include <functional>
#include <iostream>
#include <limits>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

using Subset = vector<int>;
using Subsets = vector<Subset>;

struct SubsetRecord {
    Subset values;
    long long sum;
};

class SubsetEngine {
private:
    static long long checkedAdd(long long a, long long b) {
        if (b > 0 && a > numeric_limits<long long>::max() - b) {
            throw overflow_error("Subset sum overflow.");
        }
        if (b < 0 && a < numeric_limits<long long>::min() - b) {
            throw overflow_error("Subset sum overflow.");
        }
        return a + b;
    }

public:
    // Each input position is a distinct choice, even when values repeat.
    static Subsets generate(const Subset& values) {
        Subsets result(1);

        for (int value : values) {
            const size_t oldSize = result.size();
            result.reserve(oldSize * 2);

            for (size_t i = 0; i < oldSize; ++i) {
                Subset candidate = result[i];
                candidate.push_back(value);
                result.push_back(std::move(candidate));
            }
        }

        return result;
    }

    // Sorting and skipping equal siblings prevents duplicate value combinations.
    static Subsets uniqueSubsets(Subset values) {
        sort(values.begin(), values.end());

        Subsets result;
        Subset path;

        function<void(size_t)> dfs = [&](size_t start) {
            result.push_back(path);

            for (size_t i = start; i < values.size(); ++i) {
                if (i > start && values[i] == values[i - 1]) {
                    continue;
                }

                path.push_back(values[i]);
                dfs(i + 1);
                path.pop_back();
            }
        };

        dfs(0);
        return result;
    }

    static Subsets subsetSum(Subset values, long long target) {
        sort(values.begin(), values.end());

        Subsets result;
        Subset path;

        function<void(size_t, long long)> dfs =
            [&](size_t start, long long remaining) {
                if (remaining == 0) {
                    result.push_back(path);
                }

                for (size_t i = start; i < values.size(); ++i) {
                    if (i > start && values[i] == values[i - 1]) {
                        continue;
                    }

                    path.push_back(values[i]);
                    dfs(i + 1, checkedAdd(remaining, -static_cast<long long>(values[i])));
                    path.pop_back();
                }
            };

        dfs(0, target);
        return result;
    }

    static bool subsetSumExists(const Subset& values, long long target) {
        set<long long> reachable{0};

        for (int value : values) {
            set<long long> next = reachable;

            for (long long sum : reachable) {
                next.insert(checkedAdd(sum, value));
            }

            reachable.swap(next);

            if (reachable.count(target)) {
                return true;
            }
        }

        return reachable.count(target) != 0;
    }

    static vector<SubsetRecord> constrained(
        const Subset& values,
        size_t minSize,
        size_t maxSize,
        long long minSum,
        long long maxSum,
        const function<bool(const Subset&, long long)>& predicate = nullptr
    ) {
        if (minSize > maxSize || maxSize > values.size()) {
            throw invalid_argument("Invalid subset-size limits.");
        }

        if (minSum > maxSum) {
            throw invalid_argument("Minimum sum exceeds maximum sum.");
        }

        vector<SubsetRecord> result;
        Subset path;

        function<void(size_t, long long)> dfs =
            [&](size_t index, long long total) {
                if (path.size() > maxSize) {
                    return;
                }

                if (index == values.size()) {
                    if (path.size() < minSize ||
                        total < minSum || total > maxSum) {
                        return;
                    }

                    if (!predicate || predicate(path, total)) {
                        result.push_back({path, total});
                    }
                    return;
                }

                dfs(index + 1, total);

                path.push_back(values[index]);
                dfs(index + 1, checkedAdd(total, values[index]));
                path.pop_back();
            };

        dfs(0, 0);
        return result;
    }
};

void printSubsets(const string& label, const Subsets& subsets) {
    cout << label << '\n';

    for (const auto& subset : subsets) {
        cout << '[';
        for (size_t i = 0; i < subset.size(); ++i) {
            if (i) cout << ", ";
            cout << subset[i];
        }
        cout << "]\n";
    }
}

int main() {
    try {
        const Subset values{1, 2, 2, 3};

        printSubsets("Index-distinct subsets:", SubsetEngine::generate(values));
        printSubsets("Unique value-based subsets:",
                     SubsetEngine::uniqueSubsets(values));
        printSubsets("Subsets summing to 4:",
                     SubsetEngine::subsetSum(values, 4));

        cout << "\nConstrained subsets (size 2-3, sum 4-6):\n";
        const auto records = SubsetEngine::constrained(
            values, 2, 3, 4, 6,
            [](const Subset& subset, long long sum) {
                return sum % 2 == 0 && !subset.empty();
            }
        );

        for (const auto& record : records) {
            cout << "sum=" << record.sum << " values=[";
            for (size_t i = 0; i < record.values.size(); ++i) {
                if (i) cout << ", ";
                cout << record.values[i];
            }
            cout << "]\n";
        }

        cout << "\nTarget 7 reachable: "
             << boolalpha << SubsetEngine::subsetSumExists(values, 7) << '\n';

        if (SubsetEngine::subsetSum({0, 0}, 0).size() != 4) {
            throw runtime_error("Zero-valued subset test failed.");
        }

        if (SubsetEngine::uniqueSubsets({1, 1}).size() != 3) {
            throw runtime_error("Duplicate handling test failed.");
        }

        cout << "All checks passed.\n";
    } catch (const exception& error) {
        cerr << "Subset engine error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
