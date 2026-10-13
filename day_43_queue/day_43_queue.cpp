#include <algorithm>
#include <cstddef>
#include <iostream>
#include <optional>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

/*
 * Repository build pipeline case study.
 *
 * A build coordinator queues validation jobs for repository changes.
 * Jobs are processed in FIFO order. The coordinator exposes enqueue,
 * dequeue, front, and rear while tracking job state and rejecting
 * invalid transitions.
 *
 * Compile:
 *   g++ -std=c++17 -Wall -Wextra -pedantic queue_case_study.cpp -o queue_case_study
 */

class QueueEmptyError : public std::runtime_error {
public:
    QueueEmptyError() : std::runtime_error("Queue is empty.") {}
};

class QueueFullError : public std::runtime_error {
public:
    QueueFullError() : std::runtime_error("Queue capacity reached.") {}
};

template <typename T>
class Queue {
private:
    std::queue<T> items_;

public:
    void enqueue(const T& value) {
        items_.push(value);
    }

    T dequeue() {
        if (items_.empty()) {
            throw QueueEmptyError();
        }

        T value = items_.front();
        items_.pop();
        return value;
    }

    const T& front() const {
        if (items_.empty()) {
            throw QueueEmptyError();
        }
        return items_.front();
    }

    const T& rear() const {
        if (items_.empty()) {
            throw QueueEmptyError();
        }
        return items_.back();
    }

    bool empty() const {
        return items_.empty();
    }

    std::size_t size() const {
        return items_.size();
    }
};

struct BuildJob {
    int id;
    std::string repository;
    std::string branch;
    std::string commit;
    std::string checkName;
};

enum class JobState {
    Queued,
    Running,
    Passed,
    Failed
};

std::string stateName(JobState state) {
    switch (state) {
        case JobState::Queued: return "queued";
        case JobState::Running: return "running";
        case JobState::Passed: return "passed";
        case JobState::Failed: return "failed";
    }
    throw std::logic_error("Unknown job state.");
}

class BuildCoordinator {
private:
    Queue<BuildJob> queue_;
    std::unordered_map<int, JobState> states_;
    std::unordered_set<int> knownIds_;
    std::size_t capacity_;

public:
    explicit BuildCoordinator(std::size_t capacity)
        : capacity_(capacity) {
        if (capacity_ == 0) {
            throw std::invalid_argument("Capacity must be positive.");
        }
    }

    void enqueue(BuildJob job) {
        if (job.id <= 0) {
            throw std::invalid_argument("Job ID must be positive.");
        }
        if (job.repository.empty() || job.branch.empty() ||
            job.commit.empty() || job.checkName.empty()) {
            throw std::invalid_argument("Job fields cannot be empty.");
        }
        if (knownIds_.count(job.id) != 0) {
            throw std::invalid_argument("Duplicate job ID.");
        }
        if (queue_.size() >= capacity_) {
            throw QueueFullError();
        }

        // The ID is recorded only after every validation succeeds.
        queue_.enqueue(job);
        knownIds_.insert(job.id);
        states_.emplace(job.id, JobState::Queued);
    }

    BuildJob dequeue() {
        BuildJob job = queue_.dequeue();

        if (states_.at(job.id) != JobState::Queued) {
            throw std::logic_error("Queued job has an invalid state.");
        }

        states_.at(job.id) = JobState::Running;
        return job;
    }

    const BuildJob& front() const {
        return queue_.front();
    }

    const BuildJob& rear() const {
        return queue_.rear();
    }

    void complete(int jobId, bool passed) {
        auto found = states_.find(jobId);
        if (found == states_.end()) {
            throw std::invalid_argument("Unknown job ID.");
        }
        if (found->second != JobState::Running) {
            throw std::logic_error("Only running jobs can be completed.");
        }

        found->second = passed ? JobState::Passed : JobState::Failed;
    }

    JobState stateOf(int jobId) const {
        auto found = states_.find(jobId);
        if (found == states_.end()) {
            throw std::invalid_argument("Unknown job ID.");
        }
        return found->second;
    }

    bool empty() const {
        return queue_.empty();
    }

    std::size_t size() const {
        return queue_.size();
    }
};

void demonstrateStandardQueue() {
    std::cout << "Basic queue operations\n";

    Queue<std::string> queue;
    queue.enqueue("compile");
    queue.enqueue("unit-test");
    queue.enqueue("security-scan");

    std::cout << "Front: " << queue.front() << '\n';
    std::cout << "Rear: " << queue.rear() << '\n';
    std::cout << "Dequeue: " << queue.dequeue() << '\n';
    std::cout << "New front: " << queue.front() << '\n';
    std::cout << "Queue size: " << queue.size() << "\n\n";
}

void demonstrateBuildPipeline() {
    std::cout << "Repository build coordinator\n";

    BuildCoordinator coordinator(4);

    coordinator.enqueue({
        101, "payments-service", "feature/retry-policy",
        "a13f9c2", "compile"
    });
    coordinator.enqueue({
        102, "payments-service", "feature/retry-policy",
        "a13f9c2", "unit-tests"
    });
    coordinator.enqueue({
        103, "payments-service", "feature/retry-policy",
        "a13f9c2", "security-scan"
    });

    std::cout << "Next check: " << coordinator.front().checkName << '\n';
    std::cout << "Last queued check: " << coordinator.rear().checkName << '\n';

    while (!coordinator.empty()) {
        BuildJob job = coordinator.dequeue();

        std::cout << "Running job " << job.id
                  << " for " << job.repository
                  << " [" << job.branch << "]"
                  << ", commit " << job.commit
                  << ", check " << job.checkName << '\n';

        // A failed check is recorded explicitly. It does not reorder
        // remaining jobs or silently disappear from the job history.
        const bool passed = job.checkName != "security-scan";
        coordinator.complete(job.id, passed);

        std::cout << "Result: " << stateName(coordinator.stateOf(job.id))
                  << "\n";
    }

    std::cout << '\n';

    try {
        coordinator.enqueue({
            101, "payments-service", "main", "b47ac80", "compile"
        });
    } catch (const std::exception& error) {
        std::cout << "Rejected invalid submission: "
                  << error.what() << '\n';
    }

    try {
        coordinator.complete(999, true);
    } catch (const std::exception& error) {
        std::cout << "Rejected unknown job completion: "
                  << error.what() << '\n';
    }

    try {
        coordinator.dequeue();
    } catch (const QueueEmptyError& error) {
        std::cout << "Empty queue protection: " << error.what() << '\n';
    }
}

int main() {
    try {
        demonstrateStandardQueue();
        demonstrateBuildPipeline();
    } catch (const std::exception& error) {
        std::cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
