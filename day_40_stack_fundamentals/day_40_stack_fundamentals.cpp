#include <cassert>
#include <cstddef>
#include <iostream>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// Stack operations are constant time when the top is maintained directly.
// This program models a production incident response console where the
// latest unresolved incident is the next one handled.

class StackUnderflow : public std::runtime_error {
public:
    explicit StackUnderflow(const std::string& message)
        : std::runtime_error(message) {}
};

class StackOverflow : public std::runtime_error {
public:
    explicit StackOverflow(const std::string& message)
        : std::runtime_error(message) {}
};

template <typename T>
class ArrayStack {
private:
    std::vector<T> values_;
    std::size_t capacity_;

public:
    explicit ArrayStack(std::size_t capacity = static_cast<std::size_t>(-1))
        : capacity_(capacity) {
        if (capacity_ != static_cast<std::size_t>(-1)) {
            values_.reserve(capacity_);
        }
    }

    void push(const T& value) {
        if (values_.size() >= capacity_) {
            throw StackOverflow("Incident stack capacity reached.");
        }
        values_.push_back(value);
    }

    T pop() {
        if (empty()) {
            throw StackUnderflow("No incident is available to pop.");
        }

        T value = std::move(values_.back());
        values_.pop_back();
        return value;
    }

    const T& peek() const {
        if (empty()) {
            throw StackUnderflow("No incident is available to inspect.");
        }
        return values_.back();
    }

    bool empty() const noexcept {
        return values_.empty();
    }

    std::size_t size() const noexcept {
        return values_.size();
    }
};

template <typename T>
class LinkedStack {
private:
    struct Node {
        T value;
        std::unique_ptr<Node> next;

        explicit Node(T item) : value(std::move(item)), next(nullptr) {}
    };

    std::unique_ptr<Node> top_;
    std::size_t size_ = 0;

public:
    LinkedStack() = default;
    LinkedStack(const LinkedStack&) = delete;
    LinkedStack& operator=(const LinkedStack&) = delete;

    void push(T value) {
        auto node = std::make_unique<Node>(std::move(value));
        node->next = std::move(top_);
        top_ = std::move(node);
        ++size_;
    }

    T pop() {
        if (empty()) {
            throw StackUnderflow("No linked incident is available.");
        }

        auto removed = std::move(top_);
        top_ = std::move(removed->next);
        --size_;
        return std::move(removed->value);
    }

    const T& peek() const {
        if (empty()) {
            throw StackUnderflow("No linked incident is available to inspect.");
        }
        return top_->value;
    }

    bool empty() const noexcept {
        return size_ == 0;
    }

    std::size_t size() const noexcept {
        return size_;
    }
};

struct Incident {
    std::string id;
    std::string service;
    int severity;

    Incident(std::string incident_id, std::string affected_service, int level)
        : id(std::move(incident_id)),
          service(std::move(affected_service)),
          severity(level) {
        if (id.empty() || service.empty()) {
            throw std::invalid_argument("Incident ID and service are required.");
        }
        if (severity < 1 || severity > 5) {
            throw std::invalid_argument("Severity must be between 1 and 5.");
        }
    }
};

class IncidentConsole {
private:
    LinkedStack<Incident> unresolved_;

public:
    void report(Incident incident) {
        unresolved_.push(std::move(incident));
    }

    std::optional<Incident> resolve_latest() {
        if (unresolved_.empty()) {
            return std::nullopt;
        }
        return unresolved_.pop();
    }

    const Incident& latest() const {
        return unresolved_.peek();
    }

    bool has_incidents() const noexcept {
        return !unresolved_.empty();
    }

    std::size_t unresolved_count() const noexcept {
        return unresolved_.size();
    }
};

int main() {
    try {
        std::cout << "ARRAY STACK: INCIDENT TRIAGE\n";

        ArrayStack<std::string> alerts(3);
        alerts.push("Database connection failures");
        alerts.push("Payment latency");
        alerts.push("Authentication errors");

        std::cout << "Latest alert: " << alerts.peek() << '\n';
        std::cout << "Handling: " << alerts.pop() << '\n';
        std::cout << "Remaining alerts: " << alerts.size() << '\n';

        std::cout << "\nLINKED STACK: INCIDENT RECORDS\n";
        IncidentConsole console;

        console.report(Incident("INC-401", "Identity Service", 3));
        console.report(Incident("INC-402", "Payment API", 5));
        console.report(Incident("INC-403", "Order Service", 4));

        const Incident& newest = console.latest();
        std::cout << "Top incident: " << newest.id
                  << ", service=" << newest.service
                  << ", severity=" << newest.severity << '\n';

        while (console.has_incidents()) {
            std::optional<Incident> incident = console.resolve_latest();
            if (incident.has_value()) {
                std::cout << "Resolving " << incident->id
                          << " for " << incident->service << '\n';
            }
        }

        std::cout << "Unresolved count: "
                  << console.unresolved_count() << '\n';

        std::cout << "\nEDGE CASES\n";
        LinkedStack<int> empty_stack;
        try {
            empty_stack.pop();
        } catch (const StackUnderflow& error) {
            std::cout << "Underflow handled: " << error.what() << '\n';
        }

        ArrayStack<int> bounded(1);
        bounded.push(99);
        try {
            bounded.push(100);
        } catch (const StackOverflow& error) {
            std::cout << "Overflow handled: " << error.what() << '\n';
        }

        try {
            Incident invalid("INC-BAD", "Monitoring", 9);
            console.report(std::move(invalid));
        } catch (const std::invalid_argument& error) {
            std::cout << "Invalid incident rejected: " << error.what() << '\n';
        }

        // Assertions verify LIFO behavior independently of console output.
        ArrayStack<int> checks(3);
        checks.push(10);
        checks.push(20);
        assert(checks.peek() == 20);
        assert(checks.pop() == 20);
        assert(checks.pop() == 10);
        assert(checks.empty());

        std::cout << "\nAll stack checks passed.\n";
        std::cout << "Array push: amortized O(1); linked push: O(1).\n";
        std::cout << "Both implementations provide O(1) pop and peek.\n";
    } catch (const std::exception& error) {
        std::cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
