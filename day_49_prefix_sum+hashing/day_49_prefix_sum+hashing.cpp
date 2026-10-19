#include <algorithm>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

struct Range {
    int left;
    int right;
};

struct PullRequest {
    int number;
    string sourceBranch;
    string targetBranch;
    bool draft = true;
    bool open = true;
    bool conflict = false;
    string headRevision;
    string baseRevision;
    unordered_map<string, string> reviews;
    unordered_map<string, bool> checks;
};

struct BranchProtection {
    int requiredApprovals = 2;
    vector<string> requiredChecks;
    bool requireConversationResolution = true;
    bool allowForcePush = false;
    bool allowDirectPush = false;
};

class RepositoryGovernance {
private:
    BranchProtection policy;

    static int approvalCount(const PullRequest& pr) {
        unordered_set<string> approvedReviewers;

        for (const auto& [reviewer, state] : pr.reviews) {
            if (state == "APPROVED") {
                approvedReviewers.insert(reviewer);
            }
        }

        return static_cast<int>(approvedReviewers.size());
    }

public:
    explicit RepositoryGovernance(BranchProtection protection)
        : policy(std::move(protection)) {}

    bool mergeEligible(const PullRequest& pr) const {
        if (!pr.open || pr.draft || pr.conflict) {
            return false;
        }

        if (approvalCount(pr) < policy.requiredApprovals) {
            return false;
        }

        for (const string& check : policy.requiredChecks) {
            auto it = pr.checks.find(check);
            if (it == pr.checks.end() || !it->second) {
                return false;
            }
        }

        return true;
    }

    bool directPushAllowed(const string& branch) const {
        return branch != "main" || policy.allowDirectPush;
    }

    bool forcePushAllowed(const string& branch) const {
        return branch != "main" || policy.allowForcePush;
    }

    void printDecision(const PullRequest& pr) const {
        cout << "PR #" << pr.number
             << " from " << pr.sourceBranch
             << " -> " << pr.targetBranch << '\n';

        cout << "  approvals: " << approvalCount(pr)
             << "/" << policy.requiredApprovals << '\n';

        cout << "  conflict: " << (pr.conflict ? "yes" : "no") << '\n';

        cout << "  merge eligible: "
             << (mergeEligible(pr) ? "yes" : "no") << "\n\n";
    }
};

long long countSubarraySum(const vector<int>& values, long long target) {
    unordered_map<long long, long long> frequency;
    frequency[0] = 1;

    long long prefix = 0;
    long long result = 0;

    for (int value : values) {
        prefix += value;

        auto found = frequency.find(prefix - target);
        if (found != frequency.end()) {
            result += found->second;
        }

        ++frequency[prefix];
    }

    return result;
}

long long countZeroSum(const vector<int>& values) {
    return countSubarraySum(values, 0);
}

long long countEqualBinary(const vector<int>& values) {
    unordered_map<int, long long> frequency;
    frequency[0] = 1;

    int balance = 0;
    long long result = 0;

    for (int value : values) {
        if (value != 0 && value != 1) {
            throw invalid_argument("Binary input must contain only 0 and 1.");
        }

        balance += value == 1 ? 1 : -1;

        auto found = frequency.find(balance);
        if (found != frequency.end()) {
            result += found->second;
        }

        ++frequency[balance];
    }

    return result;
}

struct FrequencyState {
    vector<int> differences;

    bool operator==(const FrequencyState& other) const {
        return differences == other.differences;
    }
};

struct FrequencyStateHash {
    size_t operator()(const FrequencyState& state) const noexcept {
        size_t hash = 0;

        for (int value : state.differences) {
            hash ^= std::hash<int>{}(value)
                    + 0x9e3779b9
                    + (hash << 6)
                    + (hash >> 2);
        }

        return hash;
    }
};

long long countEqualFrequency(
    const vector<char>& values,
    const vector<char>& symbols
) {
    if (symbols.size() < 2) {
        throw invalid_argument("At least two symbols are required.");
    }

    unordered_set<char> allowed(symbols.begin(), symbols.end());
    if (allowed.size() != symbols.size()) {
        throw invalid_argument("Symbols must be unique.");
    }

    char reference = symbols.back();

    FrequencyState state{vector<int>(symbols.size() - 1, 0)};
    unordered_map<FrequencyState, long long, FrequencyStateHash> frequency;
    frequency[state] = 1;

    long long result = 0;

    for (char value : values) {
        if (!allowed.contains(value)) {
            throw invalid_argument("Input contains an unknown symbol.");
        }

        if (value == reference) {
            for (int& difference : state.differences) {
                --difference;
            }
        } else {
            auto position = find(symbols.begin(), symbols.end() - 1, value);
            int dimension = static_cast<int>(position - symbols.begin());
            ++state.differences[dimension];
        }

        auto found = frequency.find(state);
        if (found != frequency.end()) {
            result += found->second;
        }

        ++frequency[state];
    }

    return result;
}

void runGovernanceCaseStudy() {
    BranchProtection protection;
    protection.requiredApprovals = 2;
    protection.requiredChecks = {"unit-tests", "security-scan"};

    RepositoryGovernance governance(protection);

    PullRequest feature{
        108,
        "feature/prefix-hashing",
        "main",
        false,
        true,
        false,
        "commit-91",
        "main-37",
        {{"reviewer-a", "APPROVED"}, {"reviewer-b", "APPROVED"}},
        {{"unit-tests", true}, {"security-scan", true}}
    };

    governance.printDecision(feature);

    feature.conflict = true;
    governance.printDecision(feature);

    cout << "Direct push to main: "
         << (governance.directPushAllowed("main") ? "allowed" : "blocked")
         << '\n';

    cout << "Force push to main: "
         << (governance.forcePushAllowed("main") ? "allowed" : "blocked")
         << '\n';

    feature.conflict = false;
    feature.checks["security-scan"] = false;
    governance.printDecision(feature);
}

int main() {
    try {
        cout << "=== Prefix Sum and Hashing Case Study ===\n\n";

        vector<int> values{4, -1, -3, 5, -2, 2};
        cout << "Subarrays summing to 0: "
             << countZeroSum(values) << '\n';

        cout << "Subarrays summing to 3: "
             << countSubarraySum(values, 3) << '\n';

        vector<int> binary{0, 1, 0, 1, 1, 0};
        cout << "Equal 0/1 subarrays: "
             << countEqualBinary(binary) << '\n';

        vector<char> categories{'A', 'B', 'A', 'C', 'B', 'C', 'A', 'B', 'C'};
        cout << "Equal-frequency A/B/C subarrays: "
             << countEqualFrequency(categories, {'A', 'B', 'C'})
             << '\n';

        cout << "\n=== Repository Governance ===\n";
        runGovernanceCaseStudy();

        cout << "\nThe prefix-state algorithms use expected O(n) hash-table "
                "time and O(n) state storage.\n";
        cout << "The governance engine separates Pull Request state, "
                "review decisions, status checks, and branch policy.\n";
    }
    catch (const exception& error) {
        cerr << "Error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
