#include <algorithm>
#include <cstdint>
#include <functional>
#include <iostream>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

struct Incident {
    std::string id;
    std::string service;
    std::string description;
    int severity;
    std::uint64_t arrival;

    Incident(std::string incidentId, std::string affectedService,
             std::string details, int incidentSeverity,
             std::uint64_t arrivalOrder)
        : id(std::move(incidentId)),
          service(std::move(affectedService)),
          description(std::move(details)),
          severity(incidentSeverity),
          arrival(arrivalOrder) {
        if (id.empty() || service.empty() || description.empty()) {
            throw std::invalid_argument("Incident fields cannot be empty.");
        }
        if (severity < 0 || severity > 10) {
            throw std::invalid_argument("Severity must be between 0 and 10.");
        }
    }
};

struct HighestSeverityFirst {
    // priority_queue puts the element considered greatest at its top.
    // Higher severity wins; an earlier arrival wins equal-severity ties.
    bool operator()(const Incident& left, const Incident& right) const {
        if (left.severity != right.severity) {
            return left.severity < right.severity;
        }
        return left.arrival > right.arrival;
    }
};

struct LowestSeverityFirst {
    bool operator()(const Incident& left, const Incident& right) const {
        if (left.severity != right.severity) {
            return left.severity > right.severity;
        }
        return left.arrival > right.arrival;
    }
};

class IncidentDesk {
private:
    std::deque<Incident> immediate_;
    std::priority_queue<Incident, std::vector<Incident>,
                        HighestSeverityFirst> critical_;
    std::priority_queue<Incident, std::vector<Incident>,
                        LowestSeverityFirst> triage_;
    std::unordered_set<std::string> knownIds_;
    std::uint64_t nextArrival_ = 0;

public:
    void submit(const std::string& id, const std::string& service,
                const std::string& description, int severity,
                bool immediate = false) {
        // Validate before mutating any queue so rejected input leaves state intact.
        Incident incident(id, service, description, severity, nextArrival_);

        if (knownIds_.count(id) != 0) {
            throw std::invalid_argument("Duplicate incident identifier: " + id);
        }

        knownIds_.insert(id);
        ++nextArrival_;

        if (immediate) {
            immediate_.push_front(incident);
        }

        critical_.push(incident);
        triage_.push(incident);
    }

    Incident nextImmediate() {
        if (immediate_.empty()) {
            throw std::underflow_error("No immediate incidents.");
        }

        Incident result = immediate_.front();
        immediate_.pop_front();
        knownIds_.erase(result.id);
        return result;
    }

    Incident nextCritical() {
        if (critical_.empty()) {
            throw std::underflow_error("No incidents in severity queue.");
        }

        Incident result = critical_.top();
        critical_.pop();
        knownIds_.erase(result.id);
        return result;
    }

    Incident nextLowestSeverity() {
        if (triage_.empty()) {
            throw std::underflow_error("No incidents in triage queue.");
        }

        Incident result = triage_.top();
        triage_.pop();
        knownIds_.erase(result.id);
        return result;
    }
};

static void printIncident(const Incident& incident) {
    std::cout << incident.id << " | " << incident.service
              << " | severity " << incident.severity
              << " | " << incident.description << '\n';
}

int main() {
    try {
        IncidentDesk desk;

        desk.submit("INC-710", "payments",
                    "Payment authorization failures", 10, true);
        desk.submit("INC-711", "identity",
                    "Elevated login latency", 8, true);
        desk.submit("INC-712", "documentation",
                    "Runbook terminology correction", 2);
        desk.submit("INC-713", "database",
                    "Intermittent connection saturation", 8);
        desk.submit("INC-714", "network",
                    "Packet loss in one region", 6);

        std::cout << "Deque-based immediate intake:\n";
        printIncident(desk.nextImmediate());
        printIncident(desk.nextImmediate());

        std::cout << "\nMax-priority incident dispatch:\n";
        printIncident(desk.nextCritical());
        printIncident(desk.nextCritical());
        printIncident(desk.nextCritical());

        std::cout << "\nMin-priority triage queue example:\n";
        printIncident(desk.nextLowestSeverity());

        try {
            desk.submit("INC-710", "payments",
                        "Duplicate ticket attempt", 5);
        } catch (const std::invalid_argument& error) {
            std::cout << "\nRejected submission: " << error.what() << '\n';
        }

        try {
            desk.submit("INC-799", "payments",
                        "Invalid severity", 11);
        } catch (const std::invalid_argument& error) {
            std::cout << "Rejected submission: " << error.what() << '\n';
        }

    } catch (const std::exception& error) {
        std::cerr << "Incident desk failure: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
