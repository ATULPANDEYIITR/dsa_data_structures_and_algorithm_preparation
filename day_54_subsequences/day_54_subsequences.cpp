#include <algorithm>
#include <cstdint>
#include <functional>
#include <iostream>
#include <limits>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

using Sequence = vector<long long>;

void validateTarget(long long target) {
    (void)target;
}

vector<Sequence> generateSubsequences(const Sequence& values) {
    if (values.size() >= numeric_limits<size_t>::digits) {
        throw length_error("Too many elements to materialize subsequences.");
    }

    vector<Sequence> result;
    const size_t total = size_t{1} << values.size();
    result.reserve(total);

    // Each mask identifies which input indices are included.
    for (size_t mask = 0; mask < total; ++mask) {
        Sequence current;
        current.reserve(values.size());

        for (size_t index = 0; index < values.size(); ++index) {
            if (mask & (size_t{1} << index)) {
                current.push_back(values[index]);
            }
        }

        result.push_back(move(current));
    }

    return result;
}

map<long long, unsigned long long> sumCounts(const Sequence& values) {
    map<long long, unsigned long long> counts{{0, 1}};

    for (long long value : values) {
        auto updated = counts;

        for (const auto& [sum, count] : counts) {
            if ((value > 0 &&
                 sum > numeric_limits<long long>::max() - value) ||
                (value < 0 &&
                 sum < numeric_limits<long long>::min() - value)) {
                throw overflow_error("Subsequence sum overflow.");
            }

            const long long next = sum + value;
            auto& destination = updated[next];

            if (destination > numeric_limits<unsigned long long>::max() - count) {
                throw overflow_error("Subsequence count overflow.");
            }

            destination += count;
        }

        counts.swap(updated);
    }

    return counts;
}

bool hasSubsequenceSum(const Sequence& values, long long target) {
    const auto counts = sumCounts(values);
    return counts.find(target) != counts.end();
}

unsigned long long countWithSum(const Sequence& values, long long target) {
    const auto counts = sumCounts(values);
    const auto found = counts.find(target);
    return found == counts.end() ? 0ULL : found->second;
}

struct MergeCandidate {
    string repository;
    string pullRequest;
    Sequence changes;
    long long targetSum;
    bool checksPassed;
    bool reviewApproved;
    bool branchProtected;
};

class SubsequenceChangeAnalyzer {
public:
    bool eligible(const MergeCandidate& candidate) const {
        if (candidate.repository.empty() || candidate.pullRequest.empty()) {
            throw invalid_argument("Repository and pull request IDs are required.");
        }

        // Sum matching is a domain condition, not a substitute for governance.
        return candidate.checksPassed &&
               candidate.reviewApproved &&
               (!candidate.branchProtected ||
                hasSubsequenceSum(candidate.changes, candidate.targetSum));
    }

    void printAnalysis(const MergeCandidate& candidate) const {
        cout << "Repository: " << candidate.repository << '\n';
        cout << "Pull request: " << candidate.pullRequest << '\n';
        cout << "Target sum: " << candidate.targetSum << '\n';
        cout << "Matching subsequence count: "
             << countWithSum(candidate.changes, candidate.targetSum) << '\n';
        cout << "Merge eligible: "
             << (eligible(candidate) ? "yes" : "no") << '\n';
    }
};

int main() {
    try {
        const Sequence values{1, 2, 3};

        cout << "Subsequences of [1, 2, 3]:\n";
        for (const auto& item : generateSubsequences(values)) {
            cout << '[';
            for (size_t i = 0; i < item.size(); ++i) {
                if (i) cout << ", ";
                cout << item[i];
            }
            cout << "]\n";
        }

        cout << "\nCount with sum 3: " << countWithSum(values, 3) << '\n';
        cout << "Negative values supported: "
             << (hasSubsequenceSum({-2, 5}, 3) ? "yes" : "no") << '\n';

        SubsequenceChangeAnalyzer analyzer;
        MergeCandidate candidate{
            "operations-platform",
            "PR-104",
            {1, 2, 3},
            3,
            true,
            true,
            true
        };
        analyzer.printAnalysis(candidate);

        MergeCandidate rejected{
            "operations-platform",
            "PR-105",
            {5, 7},
            3,
            true,
            true,
            true
        };
        analyzer.printAnalysis(rejected);

        if (countWithSum({0, 0}, 0) != 4) {
            throw logic_error("Zero-value counting test failed.");
        }
        if (countWithSum({}, 0) != 1) {
            throw logic_error("Empty subsequence test failed.");
        }
    } catch (const exception& error) {
        cerr << "Error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
