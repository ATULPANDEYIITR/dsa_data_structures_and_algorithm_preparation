#include <algorithm>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#include <optional>
#include <limits>

using namespace std;

enum class HeapMode {
    MIN,
    MAX
};

struct Job {
    string id;
    int priority;
    int executionTime;

    Job(string identifier, int p, int duration)
        : id(move(identifier)),
          priority(p),
          executionTime(duration) {
        if (id.empty()) {
            throw invalid_argument("Job ID cannot be empty.");
        }

        if (executionTime < 0) {
            throw invalid_argument("Execution time cannot be negative.");
        }
    }
};

class BinaryHeap {
private:
    vector<Job> data;
    HeapMode mode;

    bool higherPriority(const Job& a, const Job& b) const {
        if (a.priority == b.priority) {
            return a.id < b.id;
        }

        if (mode == HeapMode::MIN) {
            return a.priority < b.priority;
        }

        return a.priority > b.priority;
    }

    static int parent(int index) {
        return (index - 1) / 2;
    }

    static int leftChild(int index) {
        return 2 * index + 1;
    }

    static int rightChild(int index) {
        return 2 * index + 2;
    }

    void siftUp(int index) {
        while (index > 0) {
            int p = parent(index);

            if (!higherPriority(data[index], data[p])) {
                break;
            }

            swap(data[index], data[p]);
            index = p;
        }
    }

    void siftDown(int index) {
        const int n = static_cast<int>(data.size());

        while (true) {
            int best = index;
            int left = leftChild(index);
            int right = rightChild(index);

            if (
                left < n &&
                higherPriority(data[left], data[best])
            ) {
                best = left;
            }

            if (
                right < n &&
                higherPriority(data[right], data[best])
            ) {
                best = right;
            }

            if (best == index) {
                break;
            }

            swap(data[index], data[best]);
            index = best;
        }
    }

public:
    explicit BinaryHeap(
        HeapMode heapMode = HeapMode::MIN
    ) : mode(heapMode) {}

    BinaryHeap(
        const vector<Job>& values,
        HeapMode heapMode
    ) : data(values), mode(heapMode) {
        buildHeap();
    }

    int size() const {
        return static_cast<int>(data.size());
    }

    bool empty() const {
        return data.empty();
    }

    void buildHeap() {
        for (
            int i = static_cast<int>(data.size()) / 2 - 1;
            i >= 0;
            --i
        ) {
            siftDown(i);
        }
    }

    void insert(const Job& job) {
        if (job.id.empty() || job.executionTime < 0) {
            throw invalid_argument("Invalid job.");
        }

        data.push_back(job);
        siftUp(size() - 1);

        if (!validate()) {
            throw logic_error("Heap invariant violated.");
        }
    }

    const Job& peek() const {
        if (empty()) {
            throw underflow_error("Cannot inspect empty heap.");
        }

        return data.front();
    }

    Job extract() {
        if (empty()) {
            throw underflow_error("Cannot extract from empty heap.");
        }

        Job result = data.front();

        data.front() = move(data.back());
        data.pop_back();

        if (!empty()) {
            siftDown(0);
        }

        if (!validate()) {
            throw logic_error("Heap invariant violated.");
        }

        return result;
    }

    bool validate() const {
        for (int i = 0; i < size(); ++i) {
            int left = leftChild(i);
            int right = rightChild(i);

            if (
                left < size() &&
                higherPriority(data[left], data[i])
            ) {
                return false;
            }

            if (
                right < size() &&
                higherPriority(data[right], data[i])
            ) {
                return false;
            }
        }

        return true;
    }

    void displayArray() const {
        cout << "[";

        for (int i = 0; i < size(); ++i) {
            cout << data[i].id
                 << ":" << data[i].priority;

            if (i + 1 < size()) {
                cout << ", ";
            }
        }

        cout << "]\n";
    }

    void displayRelationships() const {
        for (int i = 0; i < size(); ++i) {
            cout << "Index " << i
                 << " | Job: " << data[i].id
                 << " | Parent: ";

            int p = parent(i);

            if (i == 0) {
                cout << "None";
            } else {
                cout << data[p].id;
            }

            int left = leftChild(i);
            int right = rightChild(i);

            cout << " | Left: ";

            if (left < size()) {
                cout << data[left].id;
            } else {
                cout << "None";
            }

            cout << " | Right: ";

            if (right < size()) {
                cout << data[right].id;
            } else {
                cout << "None";
            }

            cout << '\n';
        }
    }

    vector<Job> sortedExtraction() const {
        BinaryHeap copy = *this;
        vector<Job> result;

        while (!copy.empty()) {
            result.push_back(copy.extract());
        }

        return result;
    }
};

void printJobs(const vector<Job>& jobs) {
    for (const auto& job : jobs) {
        cout << job.id
             << " (priority " << job.priority << ") ";
    }

    cout << '\n';
}

int main() {
    try {
        vector<Job> jobs = {
            {"database-backup", 4, 20},
            {"security-scan", 10, 15},
            {"report", 3, 10},
            {"monitoring", 8, 5},
            {"deployment", 6, 25},
            {"incident", 12, 8},
            {"cleanup", 2, 12}
        };

        cout << "MIN HEAP\n";

        BinaryHeap minHeap(jobs, HeapMode::MIN);
        minHeap.displayArray();

        cout << "\nTREE RELATIONSHIPS\n";
        minHeap.displayRelationships();

        cout << "\nMINIMUM JOB\n";
        cout << minHeap.peek().id << '\n';

        cout << "\nINSERTION\n";
        minHeap.insert(Job("audit", 1, 7));
        minHeap.displayArray();

        cout << "\nEXTRACTION\n";
        cout << minHeap.extract().id << '\n';
        minHeap.displayArray();

        cout << "\nMIN HEAP SORTED EXTRACTION\n";
        printJobs(minHeap.sortedExtraction());

        cout << "\nMAX HEAP\n";

        BinaryHeap maxHeap(jobs, HeapMode::MAX);
        maxHeap.displayArray();

        cout << "MAXIMUM JOB: "
             << maxHeap.peek().id << '\n';

        cout << "\nMAX HEAP EXTRACTION\n";
        printJobs(maxHeap.sortedExtraction());

        cout << "\nVALIDATION\n";
        cout << "Min heap: "
             << (minHeap.validate() ? "VALID" : "INVALID")
             << '\n';

        cout << "Max heap: "
             << (maxHeap.validate() ? "VALID" : "INVALID")
             << '\n';

        cout << "\nEDGE CASES\n";

        BinaryHeap emptyHeap;

        try {
            emptyHeap.extract();
        } catch (const underflow_error& error) {
            cout << "Expected error: " << error.what() << '\n';
        }

        BinaryHeap singleHeap;
        singleHeap.insert(Job("single", 5, 1));

        cout << "Single element: "
             << singleHeap.extract().id << '\n';

        vector<Job> duplicates = {
            {"a", 5, 1},
            {"b", 5, 1},
            {"c", -2, 1},
            {"d", 5, 1}
        };

        BinaryHeap duplicateHeap(
            duplicates,
            HeapMode::MIN
        );

        cout << "Duplicate priorities:\n";
        printJobs(duplicateHeap.sortedExtraction());

        cout << "\nALL CHECKS PASSED.\n";

    } catch (const exception& error) {
        cerr << "ERROR: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
