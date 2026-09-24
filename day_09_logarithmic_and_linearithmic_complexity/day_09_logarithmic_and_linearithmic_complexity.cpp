/*
 * Day 9 — Logarithmic and Linearithmic Complexity
 *
 * C++17 case study:
 * A high-volume parcel distribution center needs to:
 *
 * 1. Search sorted package identifiers efficiently.
 * 2. Sort incoming package records.
 * 3. Maintain a priority queue for urgent shipments.
 * 4. Find capacity thresholds using binary search.
 * 5. Demonstrate the difference between O(log n), O(n), and O(n log n).
 *
 * The program progressively develops these mechanisms and combines them
 * into an industry-style package processing system.
 */

#include <algorithm>
#include <chrono>
#include <cstddef>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace std;


// ============================================================================
// 1. PACKAGE DATA MODEL
// ============================================================================

struct Package {
    int id;
    int priority;
    int weight;
    string destination;

    bool operator<(const Package& other) const {
        /*
         * Higher priority should be extracted first.
         * If priorities are equal, the smaller package ID gets preference.
         */
        if (priority != other.priority) {
            return priority < other.priority;
        }

        return id > other.id;
    }
};


// ============================================================================
// 2. LINEAR SEARCH
// ============================================================================

int linearSearch(const vector<int>& values, int target) {
    /*
     * Worst-case complexity:
     *     O(n)
     *
     * Every element may need to be inspected.
     */
    for (size_t index = 0; index < values.size(); ++index) {
        if (values[index] == target) {
            return static_cast<int>(index);
        }
    }

    return -1;
}


// ============================================================================
// 3. ITERATIVE BINARY SEARCH
// ============================================================================

int binarySearch(const vector<int>& values, int target) {
    /*
     * Precondition:
     *     values must be sorted in ascending order.
     *
     * Every iteration eliminates approximately half of the search space.
     *
     * Time:
     *     O(log n)
     *
     * Auxiliary space:
     *     O(1)
     */
    int left = 0;
    int right = static_cast<int>(values.size()) - 1;

    while (left <= right) {
        // This form avoids overflow in fixed-width integer arithmetic.
        int middle = left + (right - left) / 2;

        if (values[middle] == target) {
            return middle;
        }

        if (values[middle] < target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return -1;
}


// ============================================================================
// 4. BOUNDARY SEARCH
// ============================================================================

int firstOccurrence(const vector<int>& values, int target) {
    int left = 0;
    int right = static_cast<int>(values.size()) - 1;
    int answer = -1;

    while (left <= right) {
        int middle = left + (right - left) / 2;

        if (values[middle] == target) {
            answer = middle;
            right = middle - 1;
        } else if (values[middle] < target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return answer;
}

int lowerBoundIndex(const vector<int>& values, int target) {
    /*
     * First index where values[index] >= target.
     *
     * Equivalent to the conceptual behavior of std::lower_bound.
     */
    int left = 0;
    int right = static_cast<int>(values.size());

    while (left < right) {
        int middle = left + (right - left) / 2;

        if (values[middle] < target) {
            left = middle + 1;
        } else {
            right = middle;
        }
    }

    return left;
}


// ============================================================================
// 5. MERGE SORT
// ============================================================================

void mergeRanges(
    vector<Package>& packages,
    vector<Package>& temporary,
    int left,
    int middle,
    int right
) {
    /*
     * Merge two sorted ranges:
     *
     * [left, middle)
     * [middle, right)
     *
     * Each package is processed once during this merge.
     *
     * Complexity:
     *     O(right - left)
     */
    int i = left;
    int j = middle;
    int k = left;

    while (i < middle && j < right) {
        /*
         * Stable merge:
         * when priorities are equal, keep the left item first.
         */
        if (packages[i].priority >= packages[j].priority) {
            temporary[k++] = packages[i++];
        } else {
            temporary[k++] = packages[j++];
        }
    }

    while (i < middle) {
        temporary[k++] = packages[i++];
    }

    while (j < right) {
        temporary[k++] = packages[j++];
    }

    for (int index = left; index < right; ++index) {
        packages[index] = temporary[index];
    }
}

void mergeSortRecursive(
    vector<Package>& packages,
    vector<Package>& temporary,
    int left,
    int right
) {
    /*
     * Recurrence:
     *
     * T(n) = 2T(n/2) + O(n)
     *
     * Therefore:
     *
     * T(n) = O(n log n)
     */
    if (right - left <= 1) {
        return;
    }

    int middle = left + (right - left) / 2;

    mergeSortRecursive(packages, temporary, left, middle);
    mergeSortRecursive(packages, temporary, middle, right);

    mergeRanges(packages, temporary, left, middle, right);
}

void mergeSort(vector<Package>& packages) {
    if (packages.size() <= 1) {
        return;
    }

    vector<Package> temporary(packages.size());

    mergeSortRecursive(
        packages,
        temporary,
        0,
        static_cast<int>(packages.size())
    );
}


// ============================================================================
// 6. MAX HEAP IMPLEMENTATION
// ============================================================================

class MaxHeap {
private:
    vector<Package> heap;

    static size_t parent(size_t index) {
        return (index - 1) / 2;
    }

    static size_t leftChild(size_t index) {
        return 2 * index + 1;
    }

    static size_t rightChild(size_t index) {
        return 2 * index + 2;
    }

    void siftUp(size_t index) {
        /*
         * A newly inserted item starts at a leaf.
         * It moves upward until the heap property is restored.
         *
         * Complexity:
         *     O(log n)
         */
        while (index > 0) {
            size_t parentIndex = parent(index);

            if (!(heap[parentIndex] < heap[index])) {
                break;
            }

            swap(heap[parentIndex], heap[index]);
            index = parentIndex;
        }
    }

    void siftDown(size_t index) {
        /*
         * After removing the root, the final element replaces it.
         * That element moves downward until the heap property is restored.
         *
         * Complexity:
         *     O(log n)
         */
        while (true) {
            size_t largest = index;
            size_t left = leftChild(index);
            size_t right = rightChild(index);

            if (left < heap.size() && heap[largest] < heap[left]) {
                largest = left;
            }

            if (right < heap.size() && heap[largest] < heap[right]) {
                largest = right;
            }

            if (largest == index) {
                break;
            }

            swap(heap[index], heap[largest]);
            index = largest;
        }
    }

public:
    MaxHeap() = default;

    explicit MaxHeap(const vector<Package>& values)
        : heap(values) {
        buildHeap();
    }

    void buildHeap() {
        /*
         * Leaves already satisfy the heap property.
         *
         * Start from the final internal node.
         *
         * Bottom-up heap construction is O(n), not O(n log n).
         */
        if (heap.empty()) {
            return;
        }

        for (
            int index = static_cast<int>(heap.size() / 2) - 1;
            index >= 0;
            --index
        ) {
            siftDown(static_cast<size_t>(index));
        }
    }

    void push(const Package& package) {
        heap.push_back(package);
        siftUp(heap.size() - 1);
    }

    const Package& top() const {
        if (heap.empty()) {
            throw runtime_error("Cannot access top of an empty heap.");
        }

        return heap.front();
    }

    Package pop() {
        if (heap.empty()) {
            throw runtime_error("Cannot pop from an empty heap.");
        }

        Package result = heap.front();

        heap.front() = heap.back();
        heap.pop_back();

        if (!heap.empty()) {
            siftDown(0);
        }

        return result;
    }

    bool empty() const {
        return heap.empty();
    }

    size_t size() const {
        return heap.size();
    }

    bool isValid() const {
        for (size_t child = 1; child < heap.size(); ++child) {
            size_t parentIndex = parent(child);

            if (heap[parentIndex] < heap[child]) {
                return false;
            }
        }

        return true;
    }
};


// ============================================================================
// 7. BINARY SEARCH ON AN ANSWER SPACE
// ============================================================================

bool canProcessWithinDays(
    const vector<int>& weights,
    int days,
    long long capacity
) {
    int requiredDays = 1;
    long long currentLoad = 0;

    for (int weight : weights) {
        if (currentLoad + weight <= capacity) {
            currentLoad += weight;
        } else {
            ++requiredDays;
            currentLoad = weight;
        }
    }

    return requiredDays <= days;
}

long long minimumShippingCapacity(
    const vector<int>& weights,
    int days
) {
    /*
     * This is a binary search over possible capacity values.
     *
     * Lower bound:
     *     maximum individual package weight
     *
     * Upper bound:
     *     sum of all weights
     *
     * Feasibility is monotonic:
     *
     * If capacity C works, every capacity greater than C also works.
     *
     * Complexity:
     *     O(n log S)
     *
     * where S is the capacity search range.
     */
    if (weights.empty()) {
        throw invalid_argument("Weight list cannot be empty.");
    }

    if (days <= 0) {
        throw invalid_argument("Days must be positive.");
    }

    for (int weight : weights) {
        if (weight <= 0) {
            throw invalid_argument("Package weights must be positive.");
        }
    }

    long long left = *max_element(weights.begin(), weights.end());

    long long right = 0;

    for (int weight : weights) {
        right += weight;
    }

    while (left < right) {
        long long middle = left + (right - left) / 2;

        if (canProcessWithinDays(weights, days, middle)) {
            right = middle;
        } else {
            left = middle + 1;
        }
    }

    return left;
}


// ============================================================================
// 8. PACKAGE DISTRIBUTION CENTER
// ============================================================================

class DistributionCenter {
private:
    vector<Package> packages;
    MaxHeap priorityQueue;

public:
    void addPackage(const Package& package) {
        if (package.id <= 0) {
            throw invalid_argument("Package ID must be positive.");
        }

        if (package.priority < 1 || package.priority > 5) {
            throw invalid_argument("Priority must be between 1 and 5.");
        }

        if (package.weight <= 0) {
            throw invalid_argument("Package weight must be positive.");
        }

        if (package.destination.empty()) {
            throw invalid_argument("Destination cannot be empty.");
        }

        packages.push_back(package);
        priorityQueue.push(package);
    }

    const vector<Package>& getPackages() const {
        return packages;
    }

    vector<int> getSortedIds() const {
        vector<int> ids;

        ids.reserve(packages.size());

        for (const Package& package : packages) {
            ids.push_back(package.id);
        }

        sort(ids.begin(), ids.end());

        return ids;
    }

    vector<Package> sortByPriorityUsingMergeSort() const {
        vector<Package> result = packages;
        mergeSort(result);
        return result;
    }

    Package processNextUrgentPackage() {
        return priorityQueue.pop();
    }

    bool hasUrgentPackages() const {
        return !priorityQueue.empty();
    }

    size_t packageCount() const {
        return packages.size();
    }
};


// ============================================================================
// 9. OUTPUT HELPERS
// ============================================================================

void printPackage(const Package& package) {
    cout
        << "ID=" << package.id
        << ", priority=" << package.priority
        << ", weight=" << package.weight
        << ", destination=" << package.destination
        << '\n';
}

void printComplexityTable() {
    cout << "\n";
    cout << string(78, '=') << '\n';
    cout << "COMPLEXITY TABLE\n";
    cout << string(78, '=') << '\n';

    cout << left
         << setw(25) << "Operation"
         << setw(18) << "Complexity"
         << "Explanation\n";

    cout << string(78, '-') << '\n';

    cout << setw(25) << "Linear search"
         << setw(18) << "O(n)"
         << "May inspect every element\n";

    cout << setw(25) << "Binary search"
         << setw(18) << "O(log n)"
         << "Halves the search space\n";

    cout << setw(25) << "Merge sort"
         << setw(18) << "O(n log n)"
         << "Two halves plus linear merge\n";

    cout << setw(25) << "Heap top"
         << setw(18) << "O(1)"
         << "Root contains highest priority\n";

    cout << setw(25) << "Heap insertion"
         << setw(18) << "O(log n)"
         << "Element can move to root\n";

    cout << setw(25) << "Heap extraction"
         << setw(18) << "O(log n)"
         << "Root replacement moves downward\n";

    cout << setw(25) << "Build heap"
         << setw(18) << "O(n)"
         << "Bottom-up construction\n";

    cout << setw(25) << "Heap sort"
         << setw(18) << "O(n log n)"
         << "Repeated heap extraction\n";
}


// ============================================================================
// 10. CORRECTNESS TESTS
// ============================================================================

void runTests() {
    cout << "\n";
    cout << string(78, '=') << '\n';
    cout << "CORRECTNESS TESTS\n";
    cout << string(78, '=') << '\n';

    vector<int> values = {1, 2, 2, 2, 3, 4, 5};

    if (binarySearch(values, 4) == -1) {
        throw runtime_error("Binary search failed.");
    }

    if (binarySearch(values, 99) != -1) {
        throw runtime_error("Binary search false positive.");
    }

    if (firstOccurrence(values, 2) != 1) {
        throw runtime_error("First occurrence failed.");
    }

    if (lowerBoundIndex(values, 3) != 4) {
        throw runtime_error("Lower bound failed.");
    }

    vector<Package> packages = {
        {1, 3, 10, "Delhi"},
        {2, 5, 5, "Mumbai"},
        {3, 1, 15, "Lucknow"},
        {4, 5, 8, "Pune"},
        {5, 2, 20, "Jaipur"}
    };

    vector<Package> sortedPackages = packages;
    mergeSort(sortedPackages);

    for (size_t index = 1; index < sortedPackages.size(); ++index) {
        if (sortedPackages[index - 1].priority <
            sortedPackages[index].priority) {
            throw runtime_error("Merge sort failed.");
        }
    }

    MaxHeap heap(packages);

    if (!heap.isValid()) {
        throw runtime_error("Heap construction failed.");
    }

    int previousPriority = numeric_limits<int>::max();

    while (!heap.empty()) {
        Package package = heap.pop();

        if (package.priority > previousPriority) {
            throw runtime_error("Heap ordering failed.");
        }

        previousPriority = package.priority;
    }

    vector<int> weights = {1, 2, 3, 4, 5, 6, 7};

    if (minimumShippingCapacity(weights, 3) != 11) {
        throw runtime_error("Shipping-capacity binary search failed.");
    }

    cout << "All correctness tests passed.\n";
}


// ============================================================================
// 11. PERFORMANCE DEMONSTRATION
// ============================================================================

void performanceDemonstration() {
    cout << "\n";
    cout << string(78, '=') << '\n';
    cout << "PERFORMANCE DEMONSTRATION\n";
    cout << string(78, '=') << '\n';

    vector<size_t> sizes = {
        1'000,
        10'000,
        100'000
    };

    mt19937 generator(42);
    uniform_int_distribution<int> distribution(0, 1'000'000);

    for (size_t size : sizes) {
        vector<int> values;
        values.reserve(size);

        for (size_t index = 0; index < size; ++index) {
            values.push_back(distribution(generator));
        }

        vector<int> sortedValues = values;
        sort(sortedValues.begin(), sortedValues.end());

        int target = sortedValues.back();

        auto linearStart = chrono::high_resolution_clock::now();
        volatile int linearResult = linearSearch(values, target);
        (void)linearResult;
        auto linearEnd = chrono::high_resolution_clock::now();

        auto binaryStart = chrono::high_resolution_clock::now();
        volatile int binaryResult = binarySearch(sortedValues, target);
        (void)binaryResult;
        auto binaryEnd = chrono::high_resolution_clock::now();

        auto mergeInput = vector<Package>();
        mergeInput.reserve(size);

        for (size_t index = 0; index < size; ++index) {
            mergeInput.push_back({
                static_cast<int>(index + 1),
                static_cast<int>((index % 5) + 1),
                static_cast<int>((index % 100) + 1),
                "Distribution Center"
            });
        }

        reverse(mergeInput.begin(), mergeInput.end());

        auto mergeStart = chrono::high_resolution_clock::now();
        mergeSort(mergeInput);
        auto mergeEnd = chrono::high_resolution_clock::now();

        auto linearDuration =
            chrono::duration_cast<chrono::microseconds>(
                linearEnd - linearStart
            ).count();

        auto binaryDuration =
            chrono::duration_cast<chrono::microseconds>(
                binaryEnd - binaryStart
            ).count();

        auto mergeDuration =
            chrono::duration_cast<chrono::microseconds>(
                mergeEnd - mergeStart
            ).count();

        cout << "\nn = " << size << '\n';
        cout << "Linear search: " << linearDuration << " microseconds\n";
        cout << "Binary search: " << binaryDuration << " microseconds\n";
        cout << "Merge sort:    " << mergeDuration << " microseconds\n";
    }

    cout << R"(
These measurements are implementation-dependent.

Factors such as CPU architecture, compiler optimization, cache behavior,
memory allocation, branch prediction, and input distribution affect
observed runtime.

Asymptotic complexity describes growth rather than an exact runtime.
)" << '\n';
}


// ============================================================================
// 12. INDUSTRY-STYLE CASE STUDY
// ============================================================================

void runDistributionCenterCaseStudy() {
    cout << "\n";
    cout << string(78, '=') << '\n';
    cout << "INDUSTRY-STYLE DISTRIBUTION CENTER CASE STUDY\n";
    cout << string(78, '=') << '\n';

    DistributionCenter center;

    center.addPackage({101, 3, 12, "Lucknow"});
    center.addPackage({102, 5, 8, "Delhi"});
    center.addPackage({103, 1, 20, "Jaipur"});
    center.addPackage({104, 5, 6, "Mumbai"});
    center.addPackage({105, 2, 15, "Pune"});
    center.addPackage({106, 4, 10, "Bhopal"});

    cout << "\nTotal packages: " << center.packageCount() << '\n';

    vector<int> ids = center.getSortedIds();

    cout << "\nSorted package IDs:\n";

    for (int id : ids) {
        cout << id << ' ';
    }

    cout << '\n';

    int searchId = 104;

    int position = binarySearch(ids, searchId);

    cout << "\nBinary search for package " << searchId << ":\n";

    if (position == -1) {
        cout << "Package not found.\n";
    } else {
        cout
            << "Package found at sorted position "
            << position
            << ".\n";
    }

    cout << "\nPackages sorted by priority using merge sort:\n";

    vector<Package> sortedByPriority =
        center.sortByPriorityUsingMergeSort();

    for (const Package& package : sortedByPriority) {
        printPackage(package);
    }

    cout << "\nUrgent package processing order:\n";

    while (center.hasUrgentPackages()) {
        Package package = center.processNextUrgentPackage();
        printPackage(package);
    }

    vector<int> weights = {
        12,
        8,
        20,
        6,
        15,
        10
    };

    int deliveryDays = 3;

    cout
        << "\nMinimum truck capacity for "
        << deliveryDays
        << " days: "
        << minimumShippingCapacity(weights, deliveryDays)
        << '\n';

    cout << R"(
The case study uses three different complexity patterns:

1. Package ID lookup:
       O(log n)
   after the IDs have been sorted.

2. Priority scheduling:
       O(log n)
   for insertion and extraction using the heap.

3. Batch priority sorting:
       O(n log n)
   using merge sort.

This demonstrates that one system can legitimately use multiple algorithms,
each selected for a different operational requirement.
)" << '\n';
}


// ============================================================================
// 13. MAIN
// ============================================================================

int main() {
    try {
        cout << string(78, '=') << '\n';
        cout << "DAY 9 — LOGARITHMIC AND LINEARITHMIC COMPLEXITY\n";
        cout << string(78, '=') << '\n';

        cout << R"(
Core idea:

O(log n) grows extremely slowly because each operation can remove a
large fraction of the remaining problem.

O(n) grows directly with the input size.

O(n log n) commonly appears when an algorithm has logarithmic levels
and performs linear work across each level.
)" << '\n';

        vector<int> sample = {
            2, 4, 6, 8, 10, 12, 14, 16,
            18, 20, 22, 24, 26, 28, 30
        };

        cout << "\nLinear search result: "
             << linearSearch(sample, 22)
             << '\n';

        cout << "Binary search result: "
             << binarySearch(sample, 22)
             << '\n';

        cout << "First occurrence of 10: "
             << firstOccurrence(sample, 10)
             << '\n';

        printComplexityTable();
        runDistributionCenterCaseStudy();
        runTests();
        performanceDemonstration();

        cout << "\n";
        cout << string(78, '=') << '\n';
        cout << "DAY 9 PROGRAM COMPLETED\n";
        cout << string(78, '=') << '\n';

    } catch (const exception& error) {
        cerr << "Program error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
