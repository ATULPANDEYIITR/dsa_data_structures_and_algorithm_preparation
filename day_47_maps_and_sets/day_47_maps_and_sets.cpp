#include <algorithm>
#include <cctype>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

// Case study: determine whether a repository change is eligible to merge.
// Maps aggregate review decisions and check results; sets represent unique
// reviewers, outstanding discussions, and required status checks.

enum class ReviewState {
    Approved,
    ChangesRequested,
    Commented,
    Dismissed
};

struct Review {
    string reviewer;
    ReviewState state;
};

struct StatusCheck {
    string name;
    bool passed;
};

struct PullRequest {
    int id;
    string sourceBranch;
    string targetBranch;
    bool draft = false;
    bool open = true;
    bool conflicts = false;
    bool conversationsResolved = true;
    bool commitsSatisfyLinearHistory = true;
    vector<Review> reviews;
    vector<StatusCheck> checks;
};

struct BranchProtection {
    string branch;
    size_t requiredApprovals = 2;
    set<string> requiredChecks;
    set<string> eligibleReviewers;
    bool requireResolvedConversations = true;
    bool requireLinearHistory = true;
    bool allowDirectPush = false;
    bool allowForcePush = false;
    bool allowDeletion = false;
    bool allowAdministratorBypass = false;
};

struct Evaluation {
    bool eligible = true;
    vector<string> blockers;
    set<string> effectiveApprovers;
};

class MergeEligibilityEngine {
public:
    Evaluation evaluate(
        const PullRequest& pr,
        const BranchProtection& policy
    ) const {
        Evaluation result;

        auto reject = [&](const string& reason) {
            result.eligible = false;
            result.blockers.push_back(reason);
        };

        if (!pr.open) {
            reject("Pull request is closed.");
        }
        if (pr.draft) {
            reject("Draft pull requests cannot be merged.");
        }
        if (pr.targetBranch != policy.branch) {
            reject("Target branch does not match the evaluated protection policy.");
        }
        if (pr.sourceBranch.empty() || pr.targetBranch.empty()) {
            reject("Source and target branch names are required.");
        }
        if (pr.sourceBranch == pr.targetBranch) {
            reject("Source and target branches must differ.");
        }
        if (pr.conflicts) {
            reject("Merge conflicts must be resolved.");
        }
        if (policy.requireResolvedConversations && !pr.conversationsResolved) {
            reject("Review conversations remain unresolved.");
        }
        if (policy.requireLinearHistory && !pr.commitsSatisfyLinearHistory) {
            reject("The proposed merge violates linear-history policy.");
        }

        // Only the latest recorded decision from each reviewer is effective.
        // A later dismissal or changes-requested review invalidates an older
        // approval by that reviewer.
        unordered_map<string, ReviewState> latestReview;
        for (const auto& review : pr.reviews) {
            if (review.reviewer.empty()) {
                reject("Review contains an empty reviewer identity.");
                continue;
            }
            latestReview[review.reviewer] = review.state;
        }

        for (const auto& entry : latestReview) {
            const string& reviewer = entry.first;
            if (entry.second == ReviewState::Approved &&
                policy.eligibleReviewers.count(reviewer) > 0) {
                result.effectiveApprovers.insert(reviewer);
            }
        }

        if (result.effectiveApprovers.size() < policy.requiredApprovals) {
            reject(
                "Insufficient eligible approvals: " +
                to_string(result.effectiveApprovers.size()) + " of " +
                to_string(policy.requiredApprovals) + "."
            );
        }

        unordered_map<string, bool> checkResults;
        for (const auto& check : pr.checks) {
            if (check.name.empty()) {
                reject("Status check contains an empty name.");
                continue;
            }
            // If a check is reported more than once, its last result is used.
            checkResults[check.name] = check.passed;
        }

        for (const auto& required : policy.requiredChecks) {
            auto found = checkResults.find(required);
            if (found == checkResults.end()) {
                reject("Required check is missing: " + required + ".");
            } else if (!found->second) {
                reject("Required check failed: " + required + ".");
            }
        }

        return result;
    }
};

class RepositoryGovernance {
private:
    unordered_map<string, BranchProtection> policies_;

public:
    void protect(BranchProtection policy) {
        if (policy.branch.empty()) {
            throw invalid_argument("Protected branch name cannot be empty.");
        }
        if (policy.requiredApprovals > policy.eligibleReviewers.size()) {
            throw invalid_argument(
                "Required approvals exceed the number of eligible reviewers."
            );
        }
        if (policy.requiredChecks.count("") > 0) {
            throw invalid_argument("Required check names cannot be empty.");
        }
        policies_[policy.branch] = move(policy);
    }

    const BranchProtection& policyFor(const string& branch) const {
        auto found = policies_.find(branch);
        if (found == policies_.end()) {
            throw out_of_range("No branch protection policy exists for " + branch);
        }
        return found->second;
    }

    bool directPushAllowed(const string& branch) const {
        return !policyFor(branch).allowDirectPush;
    }

    bool forcePushAllowed(const string& branch) const {
        return policyFor(branch).allowForcePush;
    }

    bool deletionAllowed(const string& branch) const {
        return policyFor(branch).allowDeletion;
    }
};

string reviewStateName(ReviewState state) {
    switch (state) {
        case ReviewState::Approved: return "approved";
        case ReviewState::ChangesRequested: return "changes requested";
        case ReviewState::Commented: return "commented";
        case ReviewState::Dismissed: return "dismissed";
    }
    throw logic_error("Unknown review state.");
}

void printEvaluation(
    const PullRequest& pr,
    const Evaluation& evaluation
) {
    cout << "\nPull Request #" << pr.id << " (" << pr.sourceBranch
         << " -> " << pr.targetBranch << ")\n";
    cout << "Effective approvers: ";
    for (const auto& reviewer : evaluation.effectiveApprovers) {
        cout << reviewer << ' ';
    }
    cout << '\n';

    if (evaluation.eligible) {
        cout << "Merge eligibility: ALLOWED\n";
        return;
    }

    cout << "Merge eligibility: BLOCKED\n";
    for (const auto& blocker : evaluation.blockers) {
        cout << "  - " << blocker << '\n';
    }
}

int main() {
    try {
        BranchProtection mainPolicy;
        mainPolicy.branch = "main";
        mainPolicy.requiredApprovals = 2;
        mainPolicy.requiredChecks = {"build", "unit-tests", "security-scan"};
        mainPolicy.eligibleReviewers = {"Mira", "Dev", "Anika", "Rohan"};
        mainPolicy.requireResolvedConversations = true;
        mainPolicy.requireLinearHistory = true;
        mainPolicy.allowDirectPush = false;
        mainPolicy.allowForcePush = false;
        mainPolicy.allowDeletion = false;

        RepositoryGovernance governance;
        governance.protect(mainPolicy);

        PullRequest ready{
            81, "feature/token-validation", "main"
        };
        ready.reviews = {
            {"Mira", ReviewState::Approved},
            {"Dev", ReviewState::Approved},
            {"Anika", ReviewState::Commented}
        };
        ready.checks = {
            {"build", true},
            {"unit-tests", true},
            {"security-scan", true}
        };

        PullRequest staleApproval{
            82, "feature/session-fix", "main"
        };
        staleApproval.reviews = {
            {"Mira", ReviewState::Approved},
            {"Mira", ReviewState::Dismissed},
            {"Dev", ReviewState::Approved}
        };
        staleApproval.checks = {
            {"build", true},
            {"unit-tests", true},
            {"security-scan", true}
        };

        PullRequest blocked{
            83, "feature/authorization", "main"
        };
        blocked.draft = true;
        blocked.conflicts = true;
        blocked.conversationsResolved = false;
        blocked.commitsSatisfyLinearHistory = false;
        blocked.reviews = {
            {"Mira", ReviewState::Approved},
            {"OutsideContributor", ReviewState::Approved}
        };
        blocked.checks = {
            {"build", true},
            {"unit-tests", false}
        };

        MergeEligibilityEngine engine;
        const auto& policy = governance.policyFor("main");

        printEvaluation(ready, engine.evaluate(ready, policy));
        printEvaluation(staleApproval, engine.evaluate(staleApproval, policy));
        printEvaluation(blocked, engine.evaluate(blocked, policy));

        cout << "\nBranch governance controls\n";
        cout << "Direct push permitted: "
             << boolalpha << governance.directPushAllowed("main") << '\n';
        cout << "Force push permitted: "
             << boolalpha << governance.forcePushAllowed("main") << '\n';
        cout << "Branch deletion permitted: "
             << boolalpha << governance.deletionAllowed("main") << '\n';

        // A protection policy cannot require more approvals than it has
        // eligible reviewers. Rejecting this configuration avoids a policy
        // that can never be satisfied.
        try {
            BranchProtection impossible;
            impossible.branch = "release";
            impossible.requiredApprovals = 3;
            impossible.eligibleReviewers = {"Mira", "Dev"};
            governance.protect(impossible);
        } catch (const invalid_argument& error) {
            cout << "Invalid policy rejected: " << error.what() << '\n';
        }

        // Standard hash containers provide expected O(1) lookups. Ordering
        // is deliberately not used for policy decisions; sorted sets make
        // diagnostic output deterministic.
    } catch (const exception& error) {
        cerr << "Governance evaluation failed: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
