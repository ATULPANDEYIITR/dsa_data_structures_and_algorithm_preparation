#include <algorithm>
#include <cassert>
#include <chrono>
#include <cmath>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <optional>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

/*
    Day 28 — Binary Search
    =======================

    Industry-style case study:
    A logistics company needs to manage a large ordered collection of
    shipment records and answer different search questions efficiently.

    The program progressively develops:
    1. Exact identifier search
    2. Duplicate-aware boundary searches
    3. Lower and upper bounds
    4. Descending-order search
    5. Rotated inventory partitions
    6. Binary search on a feasible shipping capacity
    7. Validation, testing, edge cases, and performance measurement

    C++17 or later.
    Standard library only.
*/

using namespace std;

// ---------------------------------------------------------------------------
// 1. BASIC BINARY SEARCH
// ---------------------------------------------------------------------------

int binarySearchExact(const vector<int>& values, int target) {
    int left = 0;
    int right = static_cast<int>(values.size()) - 1;

    while (left <= right) {
        // This midpoint form avoids left + right overflow in fixed-width
        // integer arithmetic.
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

// ---------------------------------------------------------------------------
// 2. LOWER BOUND
// ---------------------------------------------------------------------------

int lowerBound(const vector<int>& values, int target) {
    // Search interval is [left, right).
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

// ---------------------------------------------------------------------------
// 3. UPPER BOUND
// ---------------------------------------------------------------------------

int upperBound(const vector<int>& values, int target) {
    // Find the first position whose value is strictly greater than target.
    int left = 0;
    int right = static_cast<int>(values.size());

    while (left < right) {
        int middle = left + (right - left) / 2;

        if (values[middle] <= target) {
            left = middle + 1;
        } else {
            right = middle;
        }
    }

    return left;
}

// ---------------------------------------------------------------------------
// 4. DUPLICATE-AWARE SEARCH
// ---------------------------------------------------------------------------

int firstOccurrence(const vector<int>& values, int target) {
    int position = lowerBound(values, target);

    if (position < static_cast<int>(values.size()) &&
        values[position] == target) {
        return position;
    }

    return -1;
}

int lastOccurrence(const vector<int>& values, int target) {
    int position = upperBound(values, target) - 1;

    if (position >= 0 && values[position] == target) {
        return position;
    }

    return -1;
}

// ---------------------------------------------------------------------------
// 5. DESCENDING SEARCH
// ---------------------------------------------------------------------------

int binarySearchDescending(const vector<int>& values, int target) {
    int left = 0;
    int right = static_cast<int>(values.size()) - 1;

    while (left <= right) {
        int middle = left + (right - left) / 2;

        if (values[middle] == target) {
            return middle;
        }

        if (values[middle] > target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return -1;
}

// ---------------------------------------------------------------------------
// 6. ROTATED SORTED ARRAY
// ---------------------------------------------------------------------------

int searchRotatedSorted(const vector<int>& values, int target) {
    int left = 0;
    int right = static_cast<int>(values.size()) - 1;

    while (left <= right) {
        int middle = left + (right - left) / 2;

        if (values[middle] == target) {
            return middle;
        }

        // At least one half is sorted when all values are distinct.
        if (values[left] <= values[middle]) {
            if (values[left] <= target && target < values[middle]) {
                right = middle - 1;
            } else {
                left = middle + 1;
            }
        } else {
            if (values[middle] < target && target <= values[right]) {
                left = middle + 1;
            } else {
                right = middle - 1;
            }
        }
    }

    return -1;
}

bool searchRotatedWithDuplicates(
    const vector<int>& values,
    int target
) {
    int left = 0;
    int right = static_cast<int>(values.size()) - 1;

    while (left <= right) {
        int middle = left + (right - left) / 2;

        if (values[middle] == target) {
            return true;
        }

        // Duplicates can make the sorted half ambiguous.
        if (values[left] == values[middle] &&
            values[middle] == values[right]) {
            ++left;
            --right;
            continue;
        }

        if (values[left] <= values[middle]) {
            if (values[left] <= target && target < values[middle]) {
                right = middle - 1;
            } else {
                left = middle + 1;
            }
        } else {
            if (values[middle] < target && target <= values[right]) {
                left = middle + 1;
            } else {
                right = middle - 1;
            }
        }
    }

    return false;
}

// ---------------------------------------------------------------------------
// 7. SHIPPING DOMAIN MODEL
// ---------------------------------------------------------------------------

struct Shipment {
    int shipmentId;
    int weight;
    string destination;
};

class ShipmentRegistry {
private:
    vector<Shipment> shipments;

public:
    explicit ShipmentRegistry(vector<Shipment> records)
        : shipments(std::move(records)) {
        validate();
    }

    void validate() const {
        for (size_t index = 1; index < shipments.size(); ++index) {
            if (shipments[index - 1].shipmentId >=
                shipments[index].shipmentId) {
                throw invalid_argument(
                    "Shipment IDs must be strictly increasing."
                );
            }
        }

        for (const Shipment& shipment : shipments) {
            if (shipment.shipmentId < 0) {
                throw invalid_argument(
                    "Shipment ID cannot be negative."
                );
            }

            if (shipment.weight <= 0) {
                throw invalid_argument(
                    "Shipment weight must be positive."
                );

            if (shipment.destination.empty()) {
                throw invalid_argument(
                    "Shipment destination cannot be empty."
                );
            }
        }
    }

    int findShipmentIndex(int shipmentId) const {
        int left = 0;
        int right = static_cast<int>(shipments.size()) - 1;

        while (left <= right) {
            int middle = left + (right - left) / 2;

            if (shipments[middle].shipmentId == shipmentId) {
                return middle;
            }

            if (shipments[middle].shipmentId < shipmentId) {
                left = middle + 1;
            } else {
                right = middle - 1;
            }
        }

        return -1;
    }

    optional<Shipment> findShipment(int shipmentId) const {
        int index = findShipmentIndex(shipmentId);

        if (index == -1) {
            return nullopt;
        }

        return shipments[index];
    }

    int countShipmentIdsInRange(int firstId, int lastId) const {
        if (firstId > lastId) {
            return 0;
        }

        int first = lowerBound(
            shipmentIds(),
            firstId
        );

        int afterLast = upperBound(
            shipmentIds(),
            lastId
        );

        return afterLast - first;
    }

    vector<int> shipmentIds() const {
        vector<int> ids;
        ids.reserve(shipments.size());

        for (const Shipment& shipment : shipments) {
            ids.push_back(shipment.shipmentId);
        }

        return ids;
    }

    const vector<Shipment>& records() const {
        return shipments;
    }
};

// ---------------------------------------------------------------------------
// 8. SHIPPING CAPACITY AS A BINARY SEARCH PROBLEM
// ---------------------------------------------------------------------------

bool canShipWithinDays(
    const vector<int>& weights,
    int days,
    long long capacity
) {
    if (days <= 0) {
        return false;
    }

    int usedDays = 1;
    long long currentLoad = 0;

    for (int weight : weights) {
        if (weight < 0) {
            return false;
        }

        if (currentLoad + weight <= capacity) {
            currentLoad += weight;
        } else {
            ++usedDays;
            currentLoad = weight;

            if (usedDays > days) {
                return false;
            }
        }
    }

    return true;
}

long long minimumShippingCapacity(
    const vector<int>& weights,
    int days
) {
    if (days <= 0) {
        throw invalid_argument("days must be positive.");
    }

    if (weights.empty()) {
        return 0;
    }

    int maximumWeight = 0;
    long long totalWeight = 0;

    for (int weight : weights) {
        if (weight <= 0) {
            throw invalid_argument(
                "Every shipment weight must be positive."
            );
        }

        maximumWeight = max(maximumWeight, weight);
        totalWeight += weight;
    }

    long long left = maximumWeight;
    long long right = totalWeight;

    // Feasibility is monotonic:
    // insufficient capacity -> sufficient capacity -> always sufficient.
    while (left < right) {
        long long middle = left + (right - left) / 2;

        if (canShipWithinDays(weights, days, middle)) {
            right = middle;
        } else {
            left = middle + 1;
        }
    }

    return left;
}

// ---------------------------------------------------------------------------
// 9. GENERIC FIRST-TRUE SEARCH
// ---------------------------------------------------------------------------

template <typename Predicate>
long long firstTrue(
    long long low,
    long long high,
    Predicate predicate
) {
    long long left = low;
    long long right = high;
    long long answer = -1;

    while (left <= right) {
        long long middle = left + (right - left) / 2;

        if (predicate(middle)) {
            answer = middle;
            right = middle - 1;
        } else {
            left = middle + 1;
        }
    }

    return answer;
}

// ---------------------------------------------------------------------------
// 10. PEAK SEARCH
// ---------------------------------------------------------------------------

int findPeak(const vector<int>& values) {
    if (values.empty()) {
        return -1;
    }

    int left = 0;
    int right = static_cast<int>(values.size()) - 1;

    while (left < right) {
        int middle = left + (right - left) / 2;

        if (values[middle] < values[middle + 1]) {
            left = middle + 1;
        } else {
            right = middle;
        }
    }

    return left;
}

// ---------------------------------------------------------------------------
// 11. SORTED MATRIX SEARCH
// ---------------------------------------------------------------------------

pair<int, int> searchSortedMatrix(
    const vector<vector<int>>& matrix,
    int target
) {
    if (matrix.empty() || matrix[0].empty()) {
        return {-1, -1};
    }

    const int columns = static_cast<int>(matrix[0].size());

    for (const auto& row : matrix) {
        if (static_cast<int>(row.size()) != columns) {
            throw invalid_argument(
                "Matrix must be rectangular."
            );
        }
    }

    int left = 0;
    int right = static_cast<int>(matrix.size()) * columns - 1;

    while (left <= right) {
        int middle = left + (right - left) / 2;
        int row = middle / columns;
        int column = middle % columns;

        int current = matrix[row][column];

        if (current == target) {
            return {row, column};
        }

        if (current < target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return {-1, -1};
}

// ---------------------------------------------------------------------------
// 12. INTEGER SQUARE ROOT
// ---------------------------------------------------------------------------

long long integerSquareRoot(long long number) {
    if (number < 0) {
        throw invalid_argument(
            "Square root requires a non-negative number."
        );
    }

    if (number < 2) {
        return number;
    }

    long long left = 1;
    long long right = number / 2;
    long long answer = 1;

    while (left <= right) {
        long long middle = left + (right - left) / 2;

        // Division avoids middle * middle overflow.
        if (middle <= number / middle) {
            answer = middle;
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return answer;
}

// ---------------------------------------------------------------------------
// 13. PERFORMANCE REFERENCE SEARCH
// ---------------------------------------------------------------------------

int linearSearch(
    const vector<int>& values,
    int target
) {
    for (int index = 0;
         index < static_cast<int>(values.size());
         ++index) {
        if (values[index] == target) {
            return index;
        }
    }

    return -1;
}

// ---------------------------------------------------------------------------
// 14. TESTING
// ---------------------------------------------------------------------------

void runDeterministicTests() {
    cout << "\n=== Deterministic Tests ===\n";

    assert(binarySearchExact({}, 5) == -1);
    assert(binarySearchExact({5}, 5) == 0);
    assert(binarySearchExact({5}, 4) == -1);

    vector<int> values{1, 2, 2, 2, 3, 4, 4, 9};

    assert(lowerBound(values, 0) == 0);
    assert(lowerBound(values, 2) == 1);
    assert(lowerBound(values, 3) == 4);
    assert(lowerBound(values, 10) == 8);

    assert(upperBound(values, 2) == 4);
    assert(upperBound(values, 4) == 7);
    assert(upperBound(values, 10) == 8);

    assert(firstOccurrence(values, 2) == 1);
    assert(lastOccurrence(values, 2) == 3);
    assert(firstOccurrence(values, 8) == -1);
    assert(lastOccurrence(values, 8) == -1);

    vector<int> descending{100, 90, 80, 70, 60, 50};
    assert(binarySearchDescending(descending, 70) == 3);

    vector<int> rotated{40, 50, 60, 70, 10, 20, 30};
    assert(searchRotatedSorted(rotated, 10) == 4);
    assert(searchRotatedSorted(rotated, 70) == 3);
    assert(searchRotatedSorted(rotated, 99) == -1);

    vector<int> rotatedDuplicates{2, 5, 6, 0, 0, 1, 2};
    assert(searchRotatedWithDuplicates(rotatedDuplicates, 0));
    assert(!searchRotatedWithDuplicates(rotatedDuplicates, 3));

    assert(findPeak({1, 3, 8, 12, 9, 4, 2}) == 3);

    assert(minimumShippingCapacity(
        {1, 2, 3, 1, 1},
        4
    ) == 3);

    assert(integerSquareRoot(0) == 0);
    assert(integerSquareRoot(1) == 1);
    assert(integerSquareRoot(15) == 3);
    assert(integerSquareRoot(16) == 4);
    assert(integerSquareRoot(17) == 4);

    vector<vector<int>> matrix{
        {1, 3, 5, 7},
        {10, 11, 16, 20},
        {23, 30, 34, 60}
    };

    assert(searchSortedMatrix(matrix, 16) == make_pair(1, 2));
    assert(searchSortedMatrix(matrix, 13) == make_pair(-1, -1));

    cout << "All deterministic tests passed.\n";
}

// ---------------------------------------------------------------------------
// 15. RANDOMIZED TESTING
// ---------------------------------------------------------------------------

void runRandomizedTests(int iterations = 500) {
    cout << "\n=== Randomized Tests ===\n";

    mt19937 generator(28);
    uniform_int_distribution<int> valueDistribution(-20, 20);
    uniform_int_distribution<int> lengthDistribution(0, 100);
    uniform_int_distribution<int> targetDistribution(-25, 25);

    for (int iteration = 0; iteration < iterations; ++iteration) {
        int length = lengthDistribution(generator);
        vector<int> values;

        values.reserve(length);

        for (int index = 0; index < length; ++index) {
            values.push_back(valueDistribution(generator));
        }

        sort(values.begin(), values.end());

        int target = targetDistribution(generator);

        int exact = binarySearchExact(values, target);

        auto standard = lower_bound(
            values.begin(),
            values.end(),
            target
        );

        bool exists =
            standard != values.end() &&
            *standard == target;

        if (exists) {
            assert(exact != -1);
            assert(values[exact] == target);
        } else {
            assert(exact == -1);
        }

        int expectedFirst =
            static_cast<int>(
                lower_bound(
                    values.begin(),
                    values.end(),
                    target
                ) - values.begin()
            );

        int expectedUpper =
            static_cast<int>(
                upper_bound(
                    values.begin(),
                    values.end(),
                    target
                ) - values.begin()
            );

        assert(lowerBound(values, target) == expectedFirst);
        assert(upperBound(values, target) == expectedUpper);

        int expectedLast = expectedUpper - 1;

        if (expectedLast >= 0 && values[expectedLast] == target) {
            assert(lastOccurrence(values, target) == expectedLast);
        } else {
            assert(lastOccurrence(values, target) == -1);
        }
    }

    cout << "All randomized tests passed.\n";
}

// ---------------------------------------------------------------------------
// 16. INDUSTRY CASE STUDY
// ---------------------------------------------------------------------------

void runShipmentCaseStudy() {
    cout << "\n=== Logistics Shipment Registry Case Study ===\n";

    /*
        The registry is deliberately sorted by shipment ID.
        This ordering is the data invariant that enables logarithmic lookup.
    */
    vector<Shipment> records{
        {1001, 120, "Delhi"},
        {1008, 250, "Mumbai"},
        {1014, 180, "Pune"},
        {1022, 400, "Bengaluru"},
        {1030, 150, "Hyderabad"},
        {1041, 320, "Chennai"},
        {1050, 220, "Kolkata"}
    };

    ShipmentRegistry registry(records);

    cout << "Searching for shipment ID 1022...\n";

    auto shipment = registry.findShipment(1022);

    if (shipment.has_value()) {
        cout << "Found shipment: "
             << shipment->shipmentId
             << ", weight=" << shipment->weight
             << ", destination=" << shipment->destination
             << '\n';
    }

    cout << "Searching for missing shipment ID 9999...\n";

    auto missing = registry.findShipment(9999);

    cout << "Result: "
         << (missing.has_value() ? "found" : "not found")
         << '\n';

    cout << "Shipments with IDs in [1010, 1040]: "
         << registry.countShipmentIdsInRange(1010, 1040)
         << '\n';

    /*
        Capacity planning is a different use of binary search.

        We do not search an existing array.
        Instead, we search the possible capacity values.

        Example:
            Capacity too small -> cannot ship within required days.
            Capacity large enough -> can ship.
            Larger capacities remain feasible.

        This creates a monotonic predicate.
    */
    vector<int> packageWeights{
        1, 2, 3, 1, 1, 4, 2, 3
    };

    int days = 4;

    long long capacity =
        minimumShippingCapacity(packageWeights, days);

    cout << "Minimum capacity for "
         << days
         << " days: "
         << capacity
         << '\n';

    /*
        Validate a candidate capacity directly.
        This is useful for debugging the binary-search predicate.
    */
    cout << "Capacity " << capacity - 1
         << " feasible: "
         << boolalpha
         << canShipWithinDays(
                packageWeights,
                days,
                capacity - 1
            )
         << '\n';

    cout << "Capacity " << capacity
         << " feasible: "
         << canShipWithinDays(
                packageWeights,
                days,
                capacity
            )
         << '\n';
}

// ---------------------------------------------------------------------------
// 17. EDGE CASES AND FAILURE CONDITIONS
// ---------------------------------------------------------------------------

void demonstrateEdgeCases() {
    cout << "\n=== Edge Cases ===\n";

    cout << "Empty exact search: "
         << binarySearchExact({}, 10)
         << '\n';

    cout << "Single-element match: "
         << binarySearchExact({10}, 10)
         << '\n';

    cout << "Single-element miss: "
         << binarySearchExact({10}, 20)
         << '\n';

    vector<int> duplicates{5, 5, 5, 5, 5};

    cout << "First duplicate: "
         << firstOccurrence(duplicates, 5)
         << '\n';

    cout << "Last duplicate: "
         << lastOccurrence(duplicates, 5)
         << '\n';

    vector<int> negativeValues{-20, -10, -5, 0, 7, 15};

    cout << "Negative target: "
         << binarySearchExact(negativeValues, -10)
         << '\n';

    try {
        minimumShippingCapacity({1, 2, 3}, 0);
    } catch (const exception& error) {
        cout << "Caught invalid days: "
             << error.what()
             << '\n';
    }

    try {
        ShipmentRegistry invalidRegistry({
            {200, 100, "Delhi"},
            {100, 100, "Mumbai"}
        });
    } catch (const exception& error) {
        cout << "Caught invalid registry: "
             << error.what()
             << '\n';
    }
}

// ---------------------------------------------------------------------------
// 18. GENERIC MONOTONIC PREDICATE EXAMPLE
// ---------------------------------------------------------------------------

void demonstrateFirstTrue() {
    cout << "\n=== First True Predicate ===\n";

    const long long threshold = 73;

    long long result = firstTrue(
        0,
        100,
        [threshold](long long value) {
            return value >= threshold;
        }
    );

    cout << "First integer satisfying x >= 73: "
         << result
         << '\n';

    /*
        The critical property is not "numbers are sorted" in the ordinary
        array sense. The predicate's truth values must have one transition:

            false false false true true true

        If the predicate oscillates:

            false true false true

        binary search cannot safely eliminate half the range.
    */
}

// ---------------------------------------------------------------------------
// 19. PERFORMANCE
// ---------------------------------------------------------------------------

void benchmarkSearches() {
    cout << "\n=== Performance Measurement ===\n";

    constexpr int elementCount = 2'000'000;

    vector<int> values(elementCount);

    iota(values.begin(), values.end(), 0);

    const int target = elementCount - 1;

    auto startLinear = chrono::steady_clock::now();

    int linearResult = linearSearch(values, target);

    auto endLinear = chrono::steady_clock::now();

    auto startBinary = chrono::steady_clock::now();

    int binaryResult = binarySearchExact(values, target);

    auto endBinary = chrono::steady_clock::now();

    auto linearDuration =
        chrono::duration<double, milli>(
            endLinear - startLinear
        ).count();

    auto binaryDuration =
        chrono::duration<double, milli>(
            endBinary - startBinary
        ).count();

    cout << fixed << setprecision(4);

    cout << "Linear result: "
         << linearResult
         << ", time: "
         << linearDuration
         << " ms\n";

    cout << "Binary result: "
         << binaryResult
         << ", time: "
         << binaryDuration
         << " ms\n";

    /*
        Timing depends on CPU, compiler, optimization settings, memory
        hierarchy, operating-system load, and runtime conditions.

        Complexity is the stable engineering property:
            Linear search -> O(n)
            Binary search -> O(log n)
    */
}

// ---------------------------------------------------------------------------
// 20. MAIN
// ---------------------------------------------------------------------------

int main() {
    try {
        cout << "Day 28 — Binary Search\n";
        cout << "======================\n";

        cout << "\n=== Exact Search ===\n";

        vector<int> values{
            2, 5, 8, 12, 16, 21, 27, 35
        };

        for (int target : {2, 16, 35, 10}) {
            cout << "target=" << target
                 << ", index="
                 << binarySearchExact(values, target)
                 << '\n';
        }

        cout << "\n=== Bounds ===\n";

        vector<int> duplicateValues{
            1, 2, 2, 2, 3, 4, 4, 9
        };

        cout << "lower_bound(2): "
             << lowerBound(duplicateValues, 2)
             << '\n';

        cout << "upper_bound(2): "
             << upperBound(duplicateValues, 2)
             << '\n';

        cout << "first occurrence of 2: "
             << firstOccurrence(duplicateValues, 2)
             << '\n';

        cout << "last occurrence of 2: "
             << lastOccurrence(duplicateValues, 2)
             << '\n';

        cout << "\n=== Descending Array ===\n";

        vector<int> descending{
            100, 90, 80, 70, 60, 50
        };

        cout << "Index of 70: "
             << binarySearchDescending(descending, 70)
             << '\n';

        cout << "\n=== Rotated Array ===\n";

        vector<int> rotated{
            40, 50, 60, 70, 10, 20, 30
        };

        for (int target : {10, 70, 30, 99}) {
            cout << "target=" << target
                 << ", index="
                 << searchRotatedSorted(rotated, target)
                 << '\n';
        }

        cout << "\n=== Nearly Sorted Array ===\n";

        vector<int> nearlySorted{
            10, 30, 20, 50, 40, 60
        };

        /*
            A nearly sorted array is not handled by ordinary binary search.
            The specialized algorithm examines middle-1, middle, and middle+1.
        */
        for (int target : {10, 20, 40, 60, 99}) {
            int index = -1;

            int left = 0;
            int right =
                static_cast<int>(nearlySorted.size()) - 1;

            while (left <= right) {
                int middle =
                    left + (right - left) / 2;

                if (nearlySorted[middle] == target) {
                    index = middle;
                    break;
                }

                if (middle - 1 >= left &&
                    nearlySorted[middle - 1] == target) {
                    index = middle - 1;
                    break;
                }

                if (middle + 1 <= right &&
                    nearlySorted[middle + 1] == target) {
                    index = middle + 1;
                    break;
                }

                if (target < nearlySorted[middle]) {
                    right = middle - 2;
                } else {
                    left = middle + 2;
                }
            }

            cout << "target=" << target
                 << ", index=" << index
                 << '\n';
        }

        cout << "\n=== Peak Search ===\n";

        vector<int> mountain{
            1, 3, 8, 12, 9, 4, 2
        };

        int peakIndex = findPeak(mountain);

        cout << "Peak index: "
             << peakIndex
             << ", value: "
             << mountain[peakIndex]
             << '\n';

        cout << "\n=== Integer Square Root ===\n";

        for (long long number : {0LL, 1LL, 2LL, 15LL, 16LL, 17LL, 100LL}) {
            cout << "floor(sqrt("
                 << number
                 << "))="
                 << integerSquareRoot(number)
                 << '\n';
        }

        cout << "\n=== Matrix Search ===\n";

        vector<vector<int>> matrix{
            {1, 3, 5, 7},
            {10, 11, 16, 20},
            {23, 30, 34, 60}
        };

        auto matrixResult =
            searchSortedMatrix(matrix, 16);

        cout << "16 -> row="
             << matrixResult.first
             << ", column="
             << matrixResult.second
             << '\n';

        runShipmentCaseStudy();
        demonstrateFirstTrue();
        demonstrateEdgeCases();
        runDeterministicTests();
        runRandomizedTests();
        benchmarkSearches();

        cout << "\n=== Complexity Reference ===\n";
        cout << "Exact search: O(log n) time, O(1) auxiliary space\n";
        cout << "First/last occurrence: O(log n), O(1)\n";
        cout << "Lower/upper bound: O(log n), O(1)\n";
        cout << "Rotated distinct array: O(log n), O(1)\n";
        cout << "Rotated array with duplicates: O(n) worst case\n";
        cout << "Shipping capacity: O(n log S)\n";
        cout << "where S is the numeric capacity search range.\n";

        cout << "\nProgram completed successfully.\n";
        return 0;
    } catch (const exception& error) {
        cerr << "Fatal error: "
             << error.what()
             << '\n';

        return 1;
    }
}
