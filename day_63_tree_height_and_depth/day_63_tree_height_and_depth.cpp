#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <memory>
#include <optional>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

struct TreeNode {
    int value;
    std::unique_ptr<TreeNode> left;
    std::unique_ptr<TreeNode> right;

    explicit TreeNode(int value) : value(value) {}
};

enum class BalanceState {
    Balanced,
    Unbalanced
};

struct TreeMetrics {
    int maximumDepth{};
    int minimumDepth{};
    std::size_t leafCount{};
    BalanceState balance{};
    std::vector<int> shortestPath;
};

class TreeBuilder {
public:
    static std::unique_ptr<TreeNode>
    fromLevelOrder(const std::vector<std::optional<int>>& values) {
        if (values.empty() || !values.front().has_value()) {
            return nullptr;
        }

        auto root = std::make_unique<TreeNode>(*values.front());
        std::queue<TreeNode*> queue;
        queue.push(root.get());

        std::size_t index = 1;

        while (!queue.empty() && index < values.size()) {
            TreeNode* node = queue.front();
            queue.pop();

            if (index < values.size()) {
                if (values[index].has_value()) {
                    node->left =
                        std::make_unique<TreeNode>(*values[index]);
                    queue.push(node->left.get());
                }
                ++index;
            }

            if (index < values.size()) {
                if (values[index].has_value()) {
                    node->right =
                        std::make_unique<TreeNode>(*values[index]);
                    queue.push(node->right.get());
                }
                ++index;
            }
        }

        if (index != values.size()) {
            throw std::invalid_argument(
                "Level-order input contains unreachable nodes.");
        }

        return root;
    }
};

class TreeGovernanceAnalyzer {
private:
    const TreeNode* root_;

    static int maxDepth(const TreeNode* node) {
        if (node == nullptr) {
            return 0;
        }

        return 1 + std::max(
            maxDepth(node->left.get()),
            maxDepth(node->right.get())
        );
    }

    static int balancedHeight(const TreeNode* node) {
        if (node == nullptr) {
            return 0;
        }

        const int left = balancedHeight(node->left.get());
        if (left == -1) {
            return -1;
        }

        const int right = balancedHeight(node->right.get());
        if (right == -1) {
            return -1;
        }

        if (std::abs(left - right) > 1) {
            return -1;
        }

        return 1 + std::max(left, right);
    }

    static std::size_t leafCount(const TreeNode* node) {
        if (node == nullptr) {
            return 0;
        }

        if (node->left == nullptr && node->right == nullptr) {
            return 1;
        }

        return leafCount(node->left.get()) +
               leafCount(node->right.get());
    }

    static std::pair<int, std::vector<int>>
    shortestPath(const TreeNode* root) {
        if (root == nullptr) {
            return {0, {}};
        }

        struct QueueItem {
            const TreeNode* node;
            std::vector<int> path;
        };

        std::queue<QueueItem> queue;
        queue.push({root, {root->value}});

        while (!queue.empty()) {
            QueueItem current = std::move(queue.front());
            queue.pop();

            const TreeNode* node = current.node;

            if (node->left == nullptr && node->right == nullptr) {
                return {
                    static_cast<int>(current.path.size()),
                    std::move(current.path)
                };
            }

            if (node->left != nullptr) {
                auto nextPath = current.path;
                nextPath.push_back(node->left->value);
                queue.push({node->left.get(), std::move(nextPath)});
            }

            if (node->right != nullptr) {
                auto nextPath = current.path;
                nextPath.push_back(node->right->value);
                queue.push({node->right.get(), std::move(nextPath)});
            }
        }

        throw std::logic_error("A non-empty tree must have a leaf.");
    }

public:
    explicit TreeGovernanceAnalyzer(const TreeNode* root) : root_(root) {}

    TreeMetrics analyze() const {
        const auto shortest = shortestPath(root_);

        return {
            maxDepth(root_),
            shortest.first,
            leafCount(root_),
            balancedHeight(root_) != -1
                ? BalanceState::Balanced
                : BalanceState::Unbalanced,
            shortest.second
        };
    }
};

class MetricsReporter {
public:
    static void print(const std::string& name, const TreeMetrics& metrics) {
        std::cout << "\n[" << name << "]\n";
        std::cout << "Maximum depth: " << metrics.maximumDepth << '\n';
        std::cout << "Minimum depth: " << metrics.minimumDepth << '\n';
        std::cout << "Leaf count: " << metrics.leafCount << '\n';
        std::cout << "Balanced: "
                  << (metrics.balance == BalanceState::Balanced
                          ? "true"
                          : "false")
                  << '\n';

        std::cout << "Shortest path: ";
        for (std::size_t i = 0; i < metrics.shortestPath.size(); ++i) {
            if (i > 0) {
                std::cout << " -> ";
            }
            std::cout << metrics.shortestPath[i];
        }
        std::cout << '\n';
    }

    static void writeJson(const std::string& fileName,
                          const TreeMetrics& metrics) {
        std::ofstream output(fileName, std::ios::trunc);
        if (!output) {
            throw std::runtime_error("Unable to open report file.");
        }

        output << "{\n"
               << "  \"maximumDepth\": " << metrics.maximumDepth << ",\n"
               << "  \"minimumDepth\": " << metrics.minimumDepth << ",\n"
               << "  \"leafCount\": " << metrics.leafCount << ",\n"
               << "  \"balanced\": "
               << (metrics.balance == BalanceState::Balanced
                       ? "true"
                       : "false")
               << ",\n"
               << "  \"shortestPath\": [";

        for (std::size_t i = 0; i < metrics.shortestPath.size(); ++i) {
            if (i > 0) {
                output << ", ";
            }
            output << metrics.shortestPath[i];
        }

        output << "]\n}\n";
    }
};

void validate(const std::vector<std::optional<int>>& values) {
    if (values.size() > 100000) {
        throw std::invalid_argument("Tree input is too large.");
    }

    if (!values.empty() && !values.front().has_value()) {
        for (std::size_t i = 1; i < values.size(); ++i) {
            if (values[i].has_value()) {
                throw std::invalid_argument(
                    "A non-empty tree cannot have an unreachable root.");
            }
        }
    }
}

int main() {
    try {
        const std::unordered_map<
            std::string,
            std::vector<std::optional<int>>
        > examples{
            {"balanced", {3, 9, 20, std::nullopt, std::nullopt, 15, 7}},
            {"unbalanced", {1, 2, 2, 3, 3, std::nullopt,
                            std::nullopt, 4, 4}},
            {"single", {42}},
            {"skewed", {1, 2, std::nullopt, 3, std::nullopt, 4}},
            {"empty", {}}
        };

        for (const auto& [name, values] : examples) {
            validate(values);
            auto tree = TreeBuilder::fromLevelOrder(values);
            TreeGovernanceAnalyzer analyzer(tree.get());
            MetricsReporter::print(name, analyzer.analyze());
        }

        const std::vector<std::optional<int>> production{
            10, 5, 15, 3, 7, 12, 18,
            1, 4, 6, 8, std::nullopt, 13, 17, 20
        };

        validate(production);
        auto tree = TreeBuilder::fromLevelOrder(production);
        TreeGovernanceAnalyzer analyzer(tree.get());
        const TreeMetrics metrics = analyzer.analyze();

        if (metrics.maximumDepth != 4 ||
            metrics.minimumDepth != 3 ||
            metrics.leafCount != 7 ||
            metrics.balance != BalanceState::Balanced) {
            throw std::runtime_error("Production assertions failed.");
        }

        MetricsReporter::writeJson("tree_analysis_report.json", metrics);

        std::cout << "\nProduction example validated successfully.\n";
        std::cout << "Report written to tree_analysis_report.json\n";
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
