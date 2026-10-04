#include <iostream>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

/*
 * Technical case study:
 * A deployment pipeline maintains an ordered list of pending build jobs.
 *
 * The list is singly linked because the pipeline primarily processes jobs
 * from the front and occasionally inserts or removes jobs by position.
 *
 * Positions are zero-based.
 */

struct Job {
    int id;
    std::string name;
    int priority;

    Job(int id, std::string name, int priority)
        : id(id), name(std::move(name)), priority(priority) {}
};

class JobList {
private:
    struct Node {
        Job job;
        std::unique_ptr<Node> next;

        explicit Node(Job value) : job(std::move(value)), next(nullptr) {}
    };

    std::unique_ptr<Node> head_;
    std::size_t size_ = 0;

    void validateInsertPosition(std::size_t position) const {
        if (position > size_) {
            throw std::out_of_range("Insertion position exceeds list size");
        }
    }

    void validateDeletePosition(std::size_t position) const {
        if (position >= size_) {
            throw std::out_of_range("Deletion position does not exist");
        }
    }

public:
    JobList() = default;

    JobList(const JobList&) = delete;
    JobList& operator=(const JobList&) = delete;

    std::size_t size() const {
        return size_;
    }

    bool empty() const {
        return head_ == nullptr;
    }

    /*
     * The new node takes ownership of the old head.  This makes the
     * pointer update explicit while unique_ptr automatically releases
     * the removed node when its ownership ends.
     */
    void insertBeginning(Job job) {
        auto node = std::make_unique<Node>(std::move(job));
        node->next = std::move(head_);
        head_ = std::move(node);
        ++size_;
    }

    /*
     * With only a head pointer, reaching the tail requires traversal.
     * A separate tail pointer could make insertion O(1), but that design
     * would require maintaining the tail during every relevant deletion.
     */
    void insertEnd(Job job) {
        auto node = std::make_unique<Node>(std::move(job));

        if (!head_) {
            head_ = std::move(node);
            ++size_;
            return;
        }

        Node* current = head_.get();

        while (current->next) {
            current = current->next.get();
        }

        current->next = std::move(node);
        ++size_;
    }

    void insertPosition(std::size_t position, Job job) {
        validateInsertPosition(position);

        if (position == 0) {
            insertBeginning(std::move(job));
            return;
        }

        if (position == size_) {
            insertEnd(std::move(job));
            return;
        }

        Node* previous = head_.get();

        for (std::size_t i = 1; i < position; ++i) {
            previous = previous->next.get();
        }

        auto node = std::make_unique<Node>(std::move(job));

        // Transfer ownership in this order so no node is lost.
        node->next = std::move(previous->next);
        previous->next = std::move(node);

        ++size_;
    }

    Job deleteFirst() {
        if (!head_) {
            throw std::underflow_error("Cannot delete from an empty job list");
        }

        Job removed = std::move(head_->job);
        head_ = std::move(head_->next);
        --size_;

        return removed;
    }

    Job deleteLast() {
        if (!head_) {
            throw std::underflow_error("Cannot delete from an empty job list");
        }

        if (!head_->next) {
            return deleteFirst();
        }

        Node* previous = head_.get();

        while (previous->next && previous->next->next) {
            previous = previous->next.get();
        }

        Job removed = std::move(previous->next->job);
        previous->next.reset();
        --size_;

        return removed;
    }

    std::optional<Job> deleteById(int id) {
        if (!head_) {
            return std::nullopt;
        }

        if (head_->job.id == id) {
            return deleteFirst();
        }

        Node* previous = head_.get();

        while (previous->next) {
            if (previous->next->job.id == id) {
                auto removed = std::move(previous->next);
                previous->next = std::move(removed->next);
                --size_;

                return std::move(removed->job);
            }

            previous = previous->next.get();
        }

        return std::nullopt;
    }

    Job deletePosition(std::size_t position) {
        validateDeletePosition(position);

        if (position == 0) {
            return deleteFirst();
        }

        Node* previous = head_.get();

        for (std::size_t i = 1; i < position; ++i) {
            previous = previous->next.get();
        }

        auto removed = std::move(previous->next);
        previous->next = std::move(removed->next);
        --size_;

        return std::move(removed->job);
    }

    std::optional<std::size_t> findById(int id) const {
        const Node* current = head_.get();
        std::size_t position = 0;

        while (current) {
            if (current->job.id == id) {
                return position;
            }

            current = current->next.get();
            ++position;
        }

        return std::nullopt;
    }

    /*
     * A linked list should not silently develop a cycle or an incorrect
     * size counter.  Floyd's algorithm checks for a cycle, while the
     * second traversal verifies the recorded size.
     */
    void validateIntegrity() const {
        const Node* slow = head_.get();
        const Node* fast = head_.get();

        while (fast && fast->next) {
            slow = slow->next.get();
            fast = fast->next->next.get();

            if (slow == fast) {
                throw std::logic_error("Cycle detected in job list");
            }
        }

        std::size_t counted = 0;
        const Node* current = head_.get();

        while (current) {
            ++counted;
            current = current->next.get();
        }

        if (counted != size_) {
            throw std::logic_error("Stored size does not match linked nodes");
        }
    }

    void print() const {
        const Node* current = head_.get();

        if (!current) {
            std::cout << "EMPTY\n";
            return;
        }

        while (current) {
            std::cout << "[" << current->job.id
                      << ":" << current->job.name
                      << ",priority=" << current->job.priority << "]";

            if (current->next) {
                std::cout << " -> ";
            }

            current = current->next.get();
        }

        std::cout << '\n';
    }
};

void printOperation(const std::string& label, const JobList& jobs) {
    jobs.validateIntegrity();
    std::cout << label << "\n";
    jobs.print();
    std::cout << "size=" << jobs.size() << "\n\n";
}

Job makeJob(int id, const std::string& name, int priority) {
    if (id <= 0) {
        throw std::invalid_argument("Job ID must be positive");
    }

    if (name.empty()) {
        throw std::invalid_argument("Job name cannot be empty");
    }

    if (priority < 1 || priority > 5) {
        throw std::invalid_argument("Priority must be between 1 and 5");
    }

    return Job(id, name, priority);
}

int main() {
    try {
        JobList jobs;

        printOperation("Initial list", jobs);

        jobs.insertBeginning(makeJob(100, "security-scan", 5));
        printOperation("Insert at beginning", jobs);

        jobs.insertEnd(makeJob(103, "package-build", 2));
        printOperation("Insert at end", jobs);

        jobs.insertPosition(
            1,
            makeJob(101, "unit-tests", 4)
        );
        printOperation("Insert at position 1", jobs);

        jobs.insertPosition(
            2,
            makeJob(102, "integration-tests", 4)
        );
        printOperation("Insert at position 2", jobs);

        Job first = jobs.deleteFirst();
        std::cout << "Deleted first: " << first.id << "\n";
        printOperation("After deleting first", jobs);

        Job last = jobs.deleteLast();
        std::cout << "Deleted last: " << last.id << "\n";
        printOperation("After deleting last", jobs);

        auto removedById = jobs.deleteById(101);

        if (removedById) {
            std::cout << "Deleted by value/id: " << removedById->id << "\n";
        } else {
            std::cout << "Requested job ID was not found\n";
        }

        printOperation("After deletion by ID", jobs);

        jobs.insertEnd(makeJob(104, "deployment", 3));
        jobs.insertEnd(makeJob(105, "post-deploy-check", 3));

        Job removedAtPosition = jobs.deletePosition(1);
        std::cout << "Deleted position 1: " << removedAtPosition.id << "\n";
        printOperation("After position deletion", jobs);

        auto found = jobs.findById(104);
        if (found) {
            std::cout << "Job 104 is at position " << *found << "\n";
        }

        /*
         * Edge cases are intentionally exercised because linked-list
         * bugs frequently occur at the empty-list and one-node boundaries.
         */
        JobList single;
        single.insertBeginning(makeJob(200, "single-job", 1));
        std::cout << "\nOne-node list: ";
        single.print();

        Job singleRemoved = single.deleteLast();
        std::cout << "deleteLast on one-node list removed "
                  << singleRemoved.id << "\n";
        single.validateIntegrity();

        try {
            single.deleteFirst();
        } catch (const std::exception& error) {
            std::cout << "Expected empty-list failure: "
                      << error.what() << "\n";
        }

        try {
            jobs.deletePosition(jobs.size());
        } catch (const std::exception& error) {
            std::cout << "Expected invalid-position failure: "
                      << error.what() << "\n";
        }

        std::cout << "\nComplexity:\n";
        std::cout << "insertBeginning: O(1)\n";
        std::cout << "insertEnd:       O(n) with head-only representation\n";
        std::cout << "insertPosition:  O(n) worst case\n";
        std::cout << "deleteFirst:     O(1)\n";
        std::cout << "deleteLast:      O(n)\n";
        std::cout << "deleteById:      O(n)\n";
        std::cout << "deletePosition:  O(n) worst case\n";

    } catch (const std::exception& error) {
        std::cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
