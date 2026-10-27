#include <algorithm>
#include <exception>
#include <iostream>
#include <limits>
#include <map>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using Combination = std::vector<int>;

enum class ReviewDecision {
    Choose,
    Skip
};

struct PullRequestCandidate {
    std::string id;
    std::vector<int> changedComponents;
    int riskScore;
    bool testsPassing;
};

class CombinationError : public std::runtime_error {
public:
    explicit CombinationError(const std::string& message)
        : std::runtime_error(message) {}
};

class GovernanceCombinationEngine {
private:
    std::vector<int> values_;
    std::size_t nodeCount_ = 0;

    void validateValues() const {
        if (values_.empty()) {
            throw CombinationError("candidate values cannot be empty");
        }

        for (int value : values_) {
            if (value <= 0) {
                throw CombinationError("candidate values must be positive");
            }
        }
    }

    static int checkedAdd(int left, int right) {
        if (right > 0 &&
            left > std::numeric_limits<int>::max() - right) {
            throw CombinationError("integer overflow during sum evaluation");
        }
        return left + right;
    }

public:
    explicit GovernanceCombinationEngine(std::vector<int> values)
        : values_(std::move(values)) {
        std::sort(values_.begin(), values_.end());
        values_.erase(
            std::unique(values_.begin(), values_.end()),
            values_.end()
        );
        validateValues();
    }

    std::vector<Combination> chooseOrSkip() {
        std::vector<Combination> result;
        Combination path;

        std::function<void(std::size_t)> search =
            [&](std::size_t index) {
                ++nodeCount_;

                if (index == values_.size()) {
                    result.push_back(path);
                    return;
                }

                path.push_back(values_[index]);
                search(index + 1);
                path.pop_back();

                search(index + 1);
            };

        search(0);
        return result;
    }

    std::vector<Combination> fixedSize(std::size_t size) {
        std::vector<Combination> result;
        Combination path;

        std::function<void(std::size_t)> search =
            [&](std::size_t start) {
                ++nodeCount_;

                if (path.size() == size) {
                    result.push_back(path);
                    return;
                }

                const std::size_t remaining = size - path.size();
                if (values_.size() - start < remaining) {
                    return;
                }

                for (std::size_t i = start; i < values_.size(); ++i) {
                    path.push_back(values_[i]);
                    search(i + 1);
                    path.pop_back();
                }
            };

        if (size == 0) {
            return {{}};
        }

        if (size <= values_.size()) {
            search(0);
        }

        return result;
    }

    std::vector<Combination> sumToTarget(
        int target,
        bool allowReuse
    ) {
        if (target < 0) {
            throw CombinationError("target cannot be negative");
        }

        std::vector<Combination> result;
        Combination path;

        std::function<void(std::size_t, int)> search =
            [&](std::size_t start, int remaining) {
                ++nodeCount_;

                if (remaining == 0) {
                    result.push_back(path);
                    return;
                }

                for (std::size_t i = start; i < values_.size(); ++i) {
                    const int value = values_[i];

                    if (value > remaining) {
                        break;
                    }

                    path.push_back(value);

                    const std::size_t next =
                        allowReuse ? i : i + 1;

                    search(next, remaining - value);
                    path.pop_back();
                }
            };

        search(0, target);
        return result;
    }

    std::vector<Combination> constrained(
        std::size_t size,
        int minimumSum,
        int maximumSum
    ) {
        if (minimumSum > maximumSum) {
            throw CombinationError(
                "minimumSum cannot exceed maximumSum"
            );
        }

        std::vector<Combination> result;
        Combination path;

        std::function<void(std::size_t, int)> search =
            [&](std::size_t start, int currentSum) {
                ++nodeCount_;

                const std::size_t remaining =
                    size - path.size();

                if (remaining == 0) {
                    if (
                        currentSum >= minimumSum &&
                        currentSum <= maximumSum
                    ) {
                        result.push_back(path);
                    }
                    return;
                }

                if (values_.size() - start < remaining) {
                    return;
                }

                int lowerBound = 0;
                for (
                    std::size_t i = start;
                    i < start + remaining;
                    ++i
                ) {
                    lowerBound = checkedAdd(
                        lowerBound,
                        values_[i]
                    );
                }

                if (currentSum + lowerBound > maximumSum) {
                    return;
                }

                for (std::size_t i = start; i < values_.size(); ++i) {
                    const int nextSum =
                        checkedAdd(currentSum, values_[i]);

                    if (nextSum > maximumSum) {
                        break;
                    }

                    path.push_back(values_[i]);
                    search(i + 1, nextSum);
                    path.pop_back();
                }
            };

        if (size == 0) {
            if (minimumSum <= 0 && 0 <= maximumSum) {
                return {{}};
            }
            return {};
        }

        if (size <= values_.size()) {
            search(0, 0);
        }

        return result;
    }

    std::size_t nodeCount() const {
        return nodeCount_;
    }
};

struct GovernancePolicy {
    std::size_t requiredApprovals;
    bool requirePassingTests;
    int maximumRisk;
    bool requireUniqueComponents;
};

bool governanceEligible(
    const PullRequestCandidate& candidate,
    const GovernancePolicy& policy,
    std::size_t approvals
) {
    if (approvals < policy.requiredApprovals) {
        return false;
    }

    if (policy.requirePassingTests && !candidate.testsPassing) {
        return false;
    }

    if (candidate.riskScore > policy.maximumRisk) {
        return false;
    }

    if (policy.requireUniqueComponents) {
        std::set<int> unique(
            candidate.changedComponents.begin(),
            candidate.changedComponents.end()
        );

        if (unique.size() != candidate.changedComponents.size()) {
            return false;
        }
    }

    return true;
}

void printCombinations(
    const std::vector<Combination>& combinations
) {
    for (const auto& combination : combinations) {
        std::cout << "[";
        for (std::size_t i = 0; i < combination.size(); ++i) {
            if (i > 0) {
                std::cout << ", ";
            }
            std::cout << combination[i];
        }
        std::cout << "]\n";
    }
}

int main() {
    try {
        GovernanceCombinationEngine engine({2, 3, 5, 7});

        std::cout << "Choose/not choose:\n";
        const auto subsets = engine.chooseOrSkip();
        printCombinations(subsets);

        std::cout << "\nFixed-size combinations:\n";
        const auto pairs = engine.fixedSize(2);
        printCombinations(pairs);

        std::cout << "\nCombination sum without reuse:\n";
        const auto uniqueSums = engine.sumToTarget(10, false);
        printCombinations(uniqueSums);

        std::cout << "\nCombination sum with reuse:\n";
        const auto reusableSums = engine.sumToTarget(8, true);
        printCombinations(reusableSums);

        std::cout << "\nConstraint-based governance search:\n";
        const auto constrained = engine.constrained(3, 12, 18);
        printCombinations(constrained);

        PullRequestCandidate candidate{
            "PR-1042",
            {2, 3, 5},
            7,
            true
        };

        GovernancePolicy policy{
            2,
            true,
            10,
            true
        };

        std::cout << "\nMerge eligibility: "
                  << (
                      governanceEligible(candidate, policy, 2)
                          ? "eligible"
                          : "blocked"
                  )
                  << "\n";

        std::cout << "\nSearch nodes visited: "
                  << engine.nodeCount()
                  << "\n";

        // Invalid input is rejected instead of silently producing
        // mathematically misleading combinations.
        try {
            GovernanceCombinationEngine invalid({1, 0, 2});
        } catch (const CombinationError& error) {
            std::cout << "Validation failure: "
                      << error.what()
                      << "\n";
        }

        /*
         * Complexity:
         * chooseOrSkip explores O(2^n) states.
         * k-combination generation produces O(C(n,k)) results.
         * Combination-sum is exponential in the worst case.
         * Sorted positive values permit early termination when a value
         * exceeds the remaining target or policy maximum.
         */
    } catch (const std::exception& error) {
        std::cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
