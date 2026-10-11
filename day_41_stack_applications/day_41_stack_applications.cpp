#include <algorithm>
#include <cmath>
#include <cctype>
#include <iomanip>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

/*
 * Case study: a configuration editor for repository governance.
 *
 * The editor accepts arithmetic policy expressions, such as
 * "approvals >= 2 && checks == 1", through a small Boolean expression
 * grammar. A stack-based parser constructs an expression tree, which is
 * evaluated against a policy context. A second stack-based component checks
 * configuration delimiters before parsing.
 *
 * Compile: g++ -std=c++17 -Wall -Wextra -pedantic stack_case_study.cpp -o stack_case_study
 */

class DelimiterValidator {
public:
    static bool valid(const std::string& source, std::string& error) {
        std::vector<std::pair<char, std::size_t>> openings;
        const std::unordered_map<char, char> expected{
            {')', '('}, {']', '['}, {'}', '{'}
        };

        for (std::size_t index = 0; index < source.size(); ++index) {
            const char character = source[index];

            if (character == '(' || character == '[' || character == '{') {
                openings.emplace_back(character, index);
            } else if (expected.count(character) != 0) {
                if (openings.empty()) {
                    error = "Unexpected closing delimiter at position " +
                            std::to_string(index);
                    return false;
                }

                const auto opening = openings.back();
                openings.pop_back();

                if (opening.first != expected.at(character)) {
                    error = "Mismatched delimiter at position " +
                            std::to_string(index);
                    return false;
                }
            }
        }

        if (!openings.empty()) {
            error = "Unclosed delimiter at position " +
                    std::to_string(openings.back().second);
            return false;
        }

        return true;
    }
};

enum class TokenType {
    Number,
    Identifier,
    Operator,
    LeftParen,
    RightParen,
    End
};

struct Token {
    TokenType type;
    std::string text;
    std::size_t position;
};

class Lexer {
public:
    explicit Lexer(std::string input) : input_(std::move(input)) {
        if (input_.size() > 4096) {
            throw std::length_error("Policy expression is too long.");
        }
    }

    std::vector<Token> scan() const {
        std::vector<Token> tokens;
        std::size_t index = 0;

        while (index < input_.size()) {
            const unsigned char character =
                static_cast<unsigned char>(input_[index]);

            if (std::isspace(character)) {
                ++index;
                continue;
            }

            if (std::isdigit(character)) {
                const std::size_t start = index;
                while (index < input_.size() &&
                       std::isdigit(static_cast<unsigned char>(input_[index]))) {
                    ++index;
                }

                tokens.push_back({
                    TokenType::Number, input_.substr(start, index - start), start
                });
                continue;
            }

            if (std::isalpha(character) || character == '_') {
                const std::size_t start = index;
                while (index < input_.size()) {
                    const unsigned char current =
                        static_cast<unsigned char>(input_[index]);
                    if (!std::isalnum(current) && current != '_') {
                        break;
                    }
                    ++index;
                }

                tokens.push_back({
                    TokenType::Identifier,
                    input_.substr(start, index - start),
                    start
                });
                continue;
            }

            if (input_[index] == '(') {
                tokens.push_back({TokenType::LeftParen, "(", index++});
                continue;
            }

            if (input_[index] == ')') {
                tokens.push_back({TokenType::RightParen, ")", index++});
                continue;
            }

            std::string operation;
            for (const std::string candidate :
                 {"&&", "||", ">=", "<=", "==", "!=", ">", "<", "!"}) {
                if (input_.compare(index, candidate.size(), candidate) == 0) {
                    operation = candidate;
                    break;
                }
            }

            if (!operation.empty()) {
                tokens.push_back({TokenType::Operator, operation, index});
                index += operation.size();
                continue;
            }

            throw std::runtime_error(
                "Unsupported character at position " + std::to_string(index));
        }

        tokens.push_back({TokenType::End, "", input_.size()});
        return tokens;
    }

private:
    std::string input_;
};

struct Node {
    enum class Kind { Number, Variable, Unary, Binary };

    Kind kind;
    std::string operation;
    double number = 0.0;
    std::unique_ptr<Node> left;
    std::unique_ptr<Node> right;

    explicit Node(double value)
        : kind(Kind::Number), number(value) {}

    explicit Node(std::string variable)
        : kind(Kind::Variable), operation(std::move(variable)) {}

    Node(std::string operation, std::unique_ptr<Node> operand)
        : kind(Kind::Unary),
          operation(std::move(operation)),
          left(std::move(operand)) {}

    Node(std::string operation,
         std::unique_ptr<Node> left,
         std::unique_ptr<Node> right)
        : kind(Kind::Binary),
          operation(std::move(operation)),
          left(std::move(left)),
          right(std::move(right)) {}
};

class PolicyExpressionParser {
public:
    explicit PolicyExpressionParser(const std::string& expression)
        : tokens_(Lexer(expression).scan()) {}

    std::unique_ptr<Node> parse() {
        auto expression = parseOr();
        if (current().type != TokenType::End) {
            throw std::runtime_error(
                "Unexpected token at position " +
                std::to_string(current().position));
        }
        return expression;
    }

private:
    std::vector<Token> tokens_;
    std::size_t cursor_ = 0;

    const Token& current() const {
        return tokens_.at(cursor_);
    }

    bool accept(TokenType type, const std::string& text = "") {
        if (current().type != type ||
            (!text.empty() && current().text != text)) {
            return false;
        }
        ++cursor_;
        return true;
    }

    void require(TokenType type, const std::string& text) {
        if (!accept(type, text)) {
            throw std::runtime_error(
                "Expected '" + text + "' at position " +
                std::to_string(current().position));
        }
    }

    std::unique_ptr<Node> parseOr() {
        auto left = parseAnd();
        while (accept(TokenType::Operator, "||")) {
            left = std::make_unique<Node>(
                "||", std::move(left), parseAnd());
        }
        return left;
    }

    std::unique_ptr<Node> parseAnd() {
        auto left = parseComparison();
        while (accept(TokenType::Operator, "&&")) {
            left = std::make_unique<Node>(
                "&&", std::move(left), parseComparison());
        }
        return left;
    }

    std::unique_ptr<Node> parseComparison() {
        auto left = parseUnary();

        if (current().type == TokenType::Operator &&
            current().text != "!" && current().text != "&&" &&
            current().text != "||") {
            const std::string operation = current().text;
            ++cursor_;
            return std::make_unique<Node>(
                operation, std::move(left), parseUnary());
        }

        return left;
    }

    std::unique_ptr<Node> parseUnary() {
        if (accept(TokenType::Operator, "!")) {
            return std::make_unique<Node>("!", parseUnary());
        }
        return parsePrimary();
    }

    std::unique_ptr<Node> parsePrimary() {
        if (current().type == TokenType::Number) {
            const double value = std::stod(current().text);
            ++cursor_;
            return std::make_unique<Node>(value);
        }

        if (current().type == TokenType::Identifier) {
            std::string name = current().text;
            ++cursor_;
            return std::make_unique<Node>(std::move(name));
        }

        if (accept(TokenType::LeftParen)) {
            auto expression = parseOr();
            require(TokenType::RightParen, ")");
            return expression;
        }

        throw std::runtime_error(
            "Expected a number, policy variable, or '(' at position " +
            std::to_string(current().position));
    }
};

class PolicyContext {
public:
    std::unordered_map<std::string, double> values;

    double get(const std::string& name) const {
        const auto iterator = values.find(name);
        if (iterator == values.end()) {
            throw std::runtime_error("Unknown policy variable: " + name);
        }
        return iterator->second;
    }
};

double evaluate(const Node& node, const PolicyContext& context) {
    if (node.kind == Node::Kind::Number) {
        return node.number;
    }

    if (node.kind == Node::Kind::Variable) {
        return context.get(node.operation);
    }

    const double left = evaluate(*node.left, context);

    if (node.kind == Node::Kind::Unary) {
        if (node.operation == "!") {
            return left == 0.0 ? 1.0 : 0.0;
        }
        throw std::runtime_error("Unsupported unary operator.");
    }

    // Boolean operators short-circuit, so unnecessary branches are not evaluated.
    if (node.operation == "&&" && left == 0.0) {
        return 0.0;
    }
    if (node.operation == "||" && left != 0.0) {
        return 1.0;
    }

    const double right = evaluate(*node.right, context);

    if (node.operation == "&&") return right != 0.0 ? 1.0 : 0.0;
    if (node.operation == "||") return right != 0.0 ? 1.0 : 0.0;
    if (node.operation == ">") return left > right ? 1.0 : 0.0;
    if (node.operation == "<") return left < right ? 1.0 : 0.0;
    if (node.operation == ">=") return left >= right ? 1.0 : 0.0;
    if (node.operation == "<=") return left <= right ? 1.0 : 0.0;
    if (node.operation == "==") return left == right ? 1.0 : 0.0;
    if (node.operation == "!=") return left != right ? 1.0 : 0.0;

    throw std::runtime_error("Unsupported binary operator: " + node.operation);
}

struct MergeRequest {
    std::string id;
    std::string sourceBranch;
    std::string targetBranch;
    bool draft = false;
    bool closed = false;
    bool sourceSynchronized = true;
    bool hasConflicts = false;
    int requiredApprovals = 2;
    int latestEligibleApprovals = 0;
    bool allRequiredChecksPassed = false;
    bool allDiscussionsResolved = false;
    bool linearHistoryRequired = true;
    bool proposedMergeIsLinear = true;
    bool targetBranchProtected = true;
};

struct Eligibility {
    bool eligible;
    std::vector<std::string> blockers;
};

Eligibility evaluateMergeEligibility(const MergeRequest& request) {
    Eligibility result{true, {}};

    auto block = [&result](const std::string& reason) {
        result.eligible = false;
        result.blockers.push_back(reason);
    };

    if (request.sourceBranch.empty() || request.targetBranch.empty()) {
        block("Source and target branches must be specified.");
    }
    if (request.sourceBranch == request.targetBranch) {
        block("Source and target branches must differ.");
    }
    if (request.closed) block("Pull Request is closed.");
    if (request.draft) block("Draft Pull Requests cannot be merged.");
    if (!request.sourceSynchronized) block("Source branch must be synchronized.");
    if (request.hasConflicts) block("Merge conflicts must be resolved.");
    if (request.requiredApprovals < 0 ||
        request.latestEligibleApprovals < 0) {
        block("Approval counts cannot be negative.");
    } else if (request.latestEligibleApprovals < request.requiredApprovals) {
        block("Insufficient eligible approvals.");
    }
    if (!request.allRequiredChecksPassed) block("Required checks have not passed.");
    if (!request.allDiscussionsResolved) block("Review discussions remain unresolved.");
    if (request.linearHistoryRequired && !request.proposedMergeIsLinear) {
        block("The proposed merge violates the linear-history policy.");
    }
    if (!request.targetBranchProtected) {
        block("This governance evaluation requires a protected target branch.");
    }

    return result;
}

int main() {
    try {
        std::cout << "Repository policy expression evaluator\n";

        std::string expression =
            "approvals >= 2 && checks == 1 && !conflicts";

        std::string delimiterError;
        if (!DelimiterValidator::valid(expression, delimiterError)) {
            throw std::runtime_error(delimiterError);
        }

        PolicyContext context;
        context.values = {
            {"approvals", 2},
            {"checks", 1},
            {"conflicts", 0}
        };

        PolicyExpressionParser parser(expression);
        const auto syntaxTree = parser.parse();
        const bool policySatisfied = evaluate(*syntaxTree, context) != 0.0;

        std::cout << "Policy: " << expression << '\n';
        std::cout << "Satisfied: "
                  << std::boolalpha << policySatisfied << '\n';

        MergeRequest request{
            "PR-248",
            "feature/review-dashboard",
            "main",
            false,
            false,
            true,
            false,
            2,
            2,
            true,
            true,
            true,
            true,
            true
        };

        const Eligibility eligibility = evaluateMergeEligibility(request);

        std::cout << "\nMerge eligibility for " << request.id << '\n';
        if (eligibility.eligible) {
            std::cout << "All modeled merge conditions are satisfied.\n";
        } else {
            for (const std::string& blocker : eligibility.blockers) {
                std::cout << "- " << blocker << '\n';
            }
        }

        request.latestEligibleApprovals = 1;
        request.sourceSynchronized = false;

        const Eligibility blocked = evaluateMergeEligibility(request);
        std::cout << "\nAfter an approval becomes stale and the branch changes:\n";
        for (const std::string& blocker : blocked.blockers) {
            std::cout << "- " << blocker << '\n';
        }

        std::cout << "\nEnter a policy expression, or press Enter to finish: ";
        std::string customExpression;
        if (std::getline(std::cin, customExpression) &&
            !customExpression.empty()) {
            if (!DelimiterValidator::valid(customExpression, delimiterError)) {
                std::cout << "Invalid delimiters: " << delimiterError << '\n';
            } else {
                PolicyExpressionParser customParser(customExpression);
                const auto customTree = customParser.parse();
                std::cout << "Result: "
                          << evaluate(*customTree, context) << '\n';
            }
        }
    } catch (const std::exception& error) {
        std::cerr << "Policy evaluation failed: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
