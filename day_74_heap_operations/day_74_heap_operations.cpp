#include <algorithm>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#include <limits>
#include <random>
#include <cassert>

using namespace std;

enum class HeapType {
    MIN_HEAP,
    MAX_HEAP
};

class HeapException : public runtime_error {
public:
    explicit HeapException(const string& message)
        : runtime_error(message) {}
};

class BinaryHeap {
private:
    vector<int> data;
    HeapType type;

    bool preferred(int a, int b) const {
        return type == HeapType::MIN_HEAP ? a < b : a > b;
    }

    void siftUp(size_t index) {
        while (index > 0) {
            size_t parent = (index - 1) / 2;

            if (!preferred(data[index], data[parent])) {
                break;
            }

            swap(data[index], data[parent]);
            index = parent;
        }
    }

    void siftDown(size_t index) {
        const size_t n = data.size();

        while (true) {
            size_t best = index;
            size_t left = 2 * index + 1;
            size_t right = 2 * index + 2;

            if (
                left < n &&
                preferred(data[left], data[best])
            ) {
                best = left;
            }

            if (
                right < n &&
                preferred(data[right], data[best])
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
        HeapType heapType = HeapType::MIN_HEAP
    ) : type(heapType) {}

    BinaryHeap(
        const vector<int>& values,
        HeapType heapType
    ) : data(values), type(heapType) {
        heapify();
    }

    size_t size() const {
        return data.size();
    }

    bool empty() const {
        return data.empty();
    }

    void insert(int value) {
        data.push_back(value);
        siftUp(data.size() - 1);
    }

    int peek() const {
        if (empty()) {
            throw HeapException("Cannot inspect empty heap.");
        }

        return data.front();
    }

    int extract() {
        if (empty()) {
            throw HeapException("Cannot extract from empty heap.");
        }

        int result = data.front();

        if (data.size() == 1) {
            data.pop_back();
            return result;
        }

        data.front() = data.back();
        data.pop_back();

        siftDown(0);

        return result;
    }

    // Floyd's bottom-up heap construction.
    void heapify() {
        if (data.size() < 2) {
            return;
        }

        for (
            int i = static_cast<int>(data.size() / 2) - 1;
            i >= 0;
            --i
        ) {
            siftDown(static_cast<size_t>(i));
        }
    }

    bool validate() const {
        for (size_t i = 1; i < data.size(); ++i) {
            size_t parent = (i - 1) / 2;

            if (preferred(data[i], data[parent])) {
                return false;
            }
        }

        return true;
    }

    vector<int> getData() const {
        return data;
    }

    void print(const string& label) const {
        cout << label << ": ";

        for (int value : data) {
            cout << value << " ";
        }

        cout << '\n';
    }
};

class RepositoryTaskScheduler {
private:
    BinaryHeap urgentTasks;
    BinaryHeap lowPriorityTasks;

public:
    RepositoryTaskScheduler()
        : urgentTasks(HeapType::MAX_HEAP),
          lowPriorityTasks(HeapType::MIN_HEAP) {}

    void addTask(int priority) {
        if (priority < 1 || priority > 100) {
            throw invalid_argument(
                "Priority must be between 1 and 100."
            );
        }

        urgentTasks.insert(priority);
        lowPriorityTasks.insert(priority);
    }

    int processMostUrgent() {
        return urgentTasks.extract();
    }

    int processLeastUrgent() {
        return lowPriorityTasks.extract();
    }

    void printState() const {
        urgentTasks.print("Maximum priority heap");
        lowPriorityTasks.print("Minimum priority heap");
    }
};

void demonstrateBasicOperations() {
    cout << "\n=== BASIC HEAP OPERATIONS ===\n";

    vector<int> values = {
        45, 12, 30, 8, 25, 60, 18, 8
    };

    BinaryHeap minHeap(values, HeapType::MIN_HEAP);
    BinaryHeap maxHeap(values, HeapType::MAX_HEAP);

    minHeap.print("Min heap");
    maxHeap.print("Max heap");

    cout << "Minimum: " << minHeap.peek() << '\n';
    cout << "Maximum: " << maxHeap.peek() << '\n';

    minHeap.insert(5);
    maxHeap.insert(75);

    cout << "After insertion:\n";
    minHeap.print("Min heap");
    maxHeap.print("Max heap");

    cout << "Extract minimum: "
         << minHeap.extract() << '\n';

    cout << "Extract maximum: "
         << maxHeap.extract() << '\n';

    assert(minHeap.validate());
    assert(maxHeap.validate());
}

void demonstrateSorting() {
    cout << "\n=== HEAP SORT ===\n";

    vector<int> values = {
        34, 12, 5, 78, 23, 9, 56
    };

    BinaryHeap heap(values, HeapType::MIN_HEAP);

    vector<int> sorted;

    while (!heap.empty()) {
        sorted.push_back(heap.extract());
    }

    for (int value : sorted) {
        cout << value << " ";
    }

    cout << '\n';

    assert(is_sorted(sorted.begin(), sorted.end()));
}

void demonstrateScheduler() {
    cout << "\n=== PRIORITY SCHEDULER ===\n";

    RepositoryTaskScheduler scheduler;

    for (int priority : {20, 90, 45, 70, 10, 85}) {
        scheduler.addTask(priority);
    }

    scheduler.printState();

    cout << "Most urgent task: "
         << scheduler.processMostUrgent() << '\n';

    cout << "Least urgent task: "
         << scheduler.processLeastUrgent() << '\n';
}

void demonstrateFailures() {
    cout << "\n=== FAILURE HANDLING ===\n";

    BinaryHeap heap(HeapType::MIN_HEAP);

    try {
        heap.extract();
    } catch (const HeapException& error) {
        cout << "Expected error: " << error.what() << '\n';
    }

    try {
        RepositoryTaskScheduler scheduler;
        scheduler.addTask(150);
    } catch (const invalid_argument& error) {
        cout << "Validation error: " << error.what() << '\n';
    }
}

int main() {
    try {
        demonstrateBasicOperations();
        demonstrateSorting();
        demonstrateScheduler();
        demonstrateFailures();

        cout << "\nAll heap tests passed.\n";

    } catch (const exception& error) {
        cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
