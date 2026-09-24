/*
 * Day 12 — Array Fundamentals
 * ============================
 *
 * C++17 industry-style case study:
 *
 * "Inventory Analytics Engine"
 *
 * A small inventory system stores product quantities in an array-like
 * structure and provides:
 *
 *   - indexed access
 *   - traversal
 *   - updates
 *   - linear search
 *   - minimum / maximum
 *   - second-largest distinct quantity
 *   - frequency counting
 *   - reversal
 *   - rotation
 *   - duplicate removal
 *   - positive / negative analysis
 *   - missing quantity detection
 *   - binary search
 *   - prefix sums
 *   - validation
 *   - complexity-aware processing
 *
 * Compile:
 *   g++ -std=c++17 -O2 -Wall -Wextra -pedantic day12.cpp -o day12
 *
 * Run:
 *   ./day12
 */

#include <algorithm>
#include <cassert>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using std::cout;
using std::cin;
using std::map;
using std::optional;
using std::pair;
using std::size_t;
using std::string;
using std::unordered_map;
using std::unordered_set;
using std::vector;

// ============================================================================
// DISPLAY HELPERS
// ============================================================================

void section(const string& title) {
    cout << "\n" << string(78, '=') << "\n";
    cout << title << "\n";
    cout << string(78, '=') << "\n";
}

void subsection(const string& title) {
    cout << "\n" << string(78, '-') << "\n";
    cout << title << "\n";
    cout << string(78, '-') << "\n";
}

template <typename T>
void printVector(const vector<T>& values) {
    cout << "[";

    for (size_t index = 0; index < values.size(); ++index) {
        cout << values[index];

        if (index + 1 < values.size()) {
            cout << ", ";
        }
    }

    cout << "]";
}

// ============================================================================
// INVENTORY ANALYTICS ENGINE
// ============================================================================

class InventoryAnalytics {
private:
    vector<int> quantities;

    /*
     * Centralized validation prevents invalid data from entering the system.
     * Negative inventory may be valid in some accounting models, but this
     * case study treats inventory quantity as a non-negative measurement.
     */
    static void validateNonNegative(const vector<int>& values) {
        for (int value : values) {
            if (value < 0) {
                throw std::invalid_argument(
                    "Inventory quantities cannot be negative."
                );
            }
        }
    }

public:
    explicit InventoryAnalytics(vector<int> input)
        : quantities(std::move(input)) {
        validateNonNegative(quantities);
    }

    const vector<int>& data() const {
        return quantities;
    }

    size_t size() const {
        return quantities.size();
    }

    // ------------------------------------------------------------------------
    // Indexed access
    // ------------------------------------------------------------------------

    int at(size_t index) const {
        if (index >= quantities.size()) {
            throw std::out_of_range("Inventory index is outside the array.");
        }

        return quantities[index];
    }

    // Direct update by index is O(1).
    void update(size_t index, int newQuantity) {
        if (index >= quantities.size()) {
            throw std::out_of_range("Inventory index is outside the array.");
        }

        if (newQuantity < 0) {
            throw std::invalid_argument(
                "Inventory quantity cannot be negative."
            );
        }

        quantities[index] = newQuantity;
    }

    // ------------------------------------------------------------------------
    // Traversal and display
    // ------------------------------------------------------------------------

    void printIndexed() const {
        for (size_t index = 0; index < quantities.size(); ++index) {
            cout << "Product slot " << index
                 << " -> quantity " << quantities[index] << "\n";
        }
    }

    // ------------------------------------------------------------------------
    // Linear search
    // ------------------------------------------------------------------------

    optional<size_t> linearSearch(int target) const {
        for (size_t index = 0; index < quantities.size(); ++index) {
            if (quantities[index] == target) {
                return index;
            }
        }

        return std::nullopt;
    }

    // ------------------------------------------------------------------------
    // Minimum
    // ------------------------------------------------------------------------

    optional<int> minimum() const {
        if (quantities.empty()) {
            return std::nullopt;
        }

        int smallest = quantities.front();

        for (size_t index = 1; index < quantities.size(); ++index) {
            if (quantities[index] < smallest) {
                smallest = quantities[index];
            }
        }

        return smallest;
    }

    // ------------------------------------------------------------------------
    // Maximum
    // ------------------------------------------------------------------------

    optional<int> maximum() const {
        if (quantities.empty()) {
            return std::nullopt;
        }

        int largest = quantities.front();

        for (size_t index = 1; index < quantities.size(); ++index) {
            if (quantities[index] > largest) {
                largest = quantities[index];
            }
        }

        return largest;
    }

    // ------------------------------------------------------------------------
    // Second-largest distinct quantity
    // ------------------------------------------------------------------------

    optional<int> secondLargestDistinct() const {
        optional<int> largest;
        optional<int> secondLargest;

        /*
         * We deliberately avoid sorting because sorting would require
         * O(n log n) time. A single scan solves this in O(n).
         */
        for (int value : quantities) {
            if (!largest.has_value() || value > largest.value()) {
                secondLargest = largest;
                largest = value;
            }
            else if (
                value != largest.value() &&
                (
                    !secondLargest.has_value() ||
                    value > secondLargest.value()
                )
            ) {
                secondLargest = value;
            }
        }

        return secondLargest;
    }

    // ------------------------------------------------------------------------
    // Reverse in place
    // ------------------------------------------------------------------------

    void reverseInPlace() {
        if (quantities.empty()) {
            return;
        }

        size_t left = 0;
        size_t right = quantities.size() - 1;

        while (left < right) {
            std::swap(quantities[left], quantities[right]);
            ++left;
            --right;
        }
    }

    // ------------------------------------------------------------------------
    // Rotate right using the reversal algorithm
    // ------------------------------------------------------------------------

    void rotateRight(long long rotationCount) {
        if (quantities.empty()) {
            return;
        }

        const long long n =
            static_cast<long long>(quantities.size());

        rotationCount %= n;

        // C++ remainder can be negative, so normalize it.
        if (rotationCount < 0) {
            rotationCount += n;
        }

        if (rotationCount == 0) {
            return;
        }

        auto reverseRange = [this](size_t left, size_t right) {
            while (left < right) {
                std::swap(quantities[left], quantities[right]);
                ++left;
                --right;
            }
        };

        reverseRange(0, quantities.size() - 1);
        reverseRange(0, static_cast<size_t>(rotationCount) - 1);
        reverseRange(static_cast<size_t>(rotationCount),
                     quantities.size() - 1);
    }

    // ------------------------------------------------------------------------
    // Frequency counting
    // ------------------------------------------------------------------------

    unordered_map<int, size_t> frequencyCount() const {
        unordered_map<int, size_t> frequencies;

        for (int value : quantities) {
            ++frequencies[value];
        }

        return frequencies;
    }

    // ------------------------------------------------------------------------
    // Remove duplicates while preserving first occurrence
    // ------------------------------------------------------------------------

    void removeDuplicatesPreserveOrder() {
        unordered_set<int> seen;
        vector<int> uniqueValues;

        uniqueValues.reserve(quantities.size());

        for (int value : quantities) {
            if (seen.insert(value).second) {
                uniqueValues.push_back(value);
            }
        }

        quantities = std::move(uniqueValues);
    }

    // ------------------------------------------------------------------------
    // Count positive, negative, and zero values
    // ------------------------------------------------------------------------

    struct SignCounts {
        size_t positive = 0;
        size_t negative = 0;
        size_t zero = 0;
    };

    SignCounts countSigns() const {
        SignCounts counts;

        for (int value : quantities) {
            if (value > 0) {
                ++counts.positive;
            }
            else if (value < 0) {
                ++counts.negative;
            }
            else {
                ++counts.zero;
            }
        }

        return counts;
    }

    // ------------------------------------------------------------------------
    // Binary search
    // ------------------------------------------------------------------------

    optional<size_t> binarySearch(int target) const {
        /*
         * Binary search is valid only when the data is sorted.
         * This method checks the precondition rather than silently producing
         * an incorrect result.
         */
        if (!std::is_sorted(quantities.begin(), quantities.end())) {
            throw std::logic_error(
                "Binary search requires sorted inventory data."
            );
        }

        size_t left = 0;
        size_t right = quantities.size();

        // We use [left, right) as the search interval.
        while (left < right) {
            const size_t middle =
                left + (right - left) / 2;

            if (quantities[middle] == target) {
                return middle;
            }

            if (quantities[middle] < target) {
                left = middle + 1;
            }
            else {
                right = middle;
            }
        }

        return std::nullopt;
    }

    // ------------------------------------------------------------------------
    // Prefix sums
    // ------------------------------------------------------------------------

    vector<long long> prefixSums() const {
        vector<long long> prefix;
        prefix.reserve(quantities.size());

        long long runningTotal = 0;

        for (int value : quantities) {
            runningTotal += value;
            prefix.push_back(runningTotal);
        }

        return prefix;
    }

    static long long rangeSum(
        const vector<long long>& prefix,
        size_t left,
        size_t right
    ) {
        if (prefix.empty() || left > right || right >= prefix.size()) {
            throw std::out_of_range("Invalid prefix-sum range.");
        }

        if (left == 0) {
            return prefix[right];
        }

        return prefix[right] - prefix[left - 1];
    }
};

// ============================================================================
// SINGLE-MISSING-VALUE ALGORITHM
// ============================================================================

optional<int> findSingleMissingValue(
    const vector<int>& values,
    int n
) {
    /*
     * Expected domain is [0, n] with exactly one missing value.
     *
     * XOR properties:
     *   x ^ x = 0
     *   x ^ 0 = x
     *
     * Every present value and every expected value cancels except the
     * missing one.
     */
    if (n < 0 || values.size() != static_cast<size_t>(n)) {
        return std::nullopt;
    }

    int missing = n;

    for (size_t index = 0; index < values.size(); ++index) {
        missing ^= static_cast<int>(index);
        missing ^= values[index];
    }

    return missing;
}

// ============================================================================
// TESTING HELPERS
// ============================================================================

void require(
    bool condition,
    const string& description
) {
    if (!condition) {
        throw std::runtime_error(
            "Test failed: " + description
        );
    }
}

void runTests() {
    section("Automated verification tests");

    {
        InventoryAnalytics inventory({3, 1, 9, 2});

        require(
            inventory.maximum().value() == 9,
            "maximum"
        );

        require(
            inventory.minimum().value() == 1,
            "minimum"
        );

        require(
            inventory.secondLargestDistinct().value() == 3,
            "second-largest distinct"
        );
    }

    {
        InventoryAnalytics inventory({1, 2, 3, 4});
        inventory.reverseInPlace();

        require(
            inventory.data() == vector<int>({4, 3, 2, 1}),
            "reverse"
        );
    }

    {
        InventoryAnalytics inventory({1, 2, 3, 4, 5});
        inventory.rotateRight(2);

        require(
            inventory.data() == vector<int>({4, 5, 1, 2, 3}),
            "rotation"
        );
    }

    {
        InventoryAnalytics inventory({1, 2, 1, 3, 2});
        inventory.removeDuplicatesPreserveOrder();

        require(
            inventory.data() == vector<int>({1, 2, 3}),
            "duplicate removal"
        );
    }

    {
        InventoryAnalytics inventory({2, 4, 6, 8, 10});

        require(
            inventory.binarySearch(8).value() == 3,
            "binary search"
        );

        require(
            !inventory.binarySearch(9).has_value(),
            "binary search missing value"
        );
    }

    {
        InventoryAnalytics inventory({2, 4, 6});

        const auto prefix = inventory.prefixSums();

        require(
            prefix == vector<long long>({2, 6, 12}),
            "prefix sums"
        );

        require(
            InventoryAnalytics::rangeSum(prefix, 1, 2) == 10,
            "range sum"
        );
    }

    {
        const auto missing =
            findSingleMissingValue({3, 0, 1}, 3);

        require(
            missing.has_value() && missing.value() == 2,
            "single missing value"
        );
    }

    {
        bool caught = false;

        try {
            InventoryAnalytics invalid({10, -5, 20});
        }
        catch (const std::invalid_argument&) {
            caught = true;
        }

        require(caught, "negative inventory validation");
    }

    cout << "All tests passed.\n";
}

// ============================================================================
// MAIN CASE STUDY
// ============================================================================

int main() {
    try {
        section("DAY 12 — ARRAY FUNDAMENTALS");
        cout << "Industry case study: Inventory Analytics Engine\n";

        // --------------------------------------------------------------------
        // Initial data
        // --------------------------------------------------------------------

        subsection("1. Inventory initialization");

        InventoryAnalytics inventory({
            42, 18, 75, 30, 18, 55, 90, 12, 75, 30
        });

        cout << "Inventory quantities: ";
        printVector(inventory.data());
        cout << "\n";

        cout << "Number of product slots: "
             << inventory.size() << "\n";

        // --------------------------------------------------------------------
        // Indexing
        // --------------------------------------------------------------------

        subsection("2. Indexed access");

        cout << "Quantity at index 0: "
             << inventory.at(0) << "\n";

        cout << "Quantity at index 4: "
             << inventory.at(4) << "\n";

        // --------------------------------------------------------------------
        // Traversal
        // --------------------------------------------------------------------

        subsection("3. Traversal");

        inventory.printIndexed();

        // --------------------------------------------------------------------
        // Updating
        // --------------------------------------------------------------------

        subsection("4. Updating an inventory slot");

        cout << "Before update: "
             << inventory.at(2) << "\n";

        inventory.update(2, 80);

        cout << "After update: "
             << inventory.at(2) << "\n";

        // --------------------------------------------------------------------
        // Linear search
        // --------------------------------------------------------------------

        subsection("5. Linear search");

        const auto found = inventory.linearSearch(55);

        if (found.has_value()) {
            cout << "Quantity 55 found at index "
                 << found.value() << "\n";
        }
        else {
            cout << "Quantity 55 not found.\n";
        }

        const auto absent = inventory.linearSearch(999);

        cout << "Searching for 999: "
             << (absent.has_value() ? "found" : "not found")
             << "\n";

        // --------------------------------------------------------------------
        // Minimum / maximum
        // --------------------------------------------------------------------

        subsection("6. Minimum and maximum");

        cout << "Minimum quantity: "
             << inventory.minimum().value() << "\n";

        cout << "Maximum quantity: "
             << inventory.maximum().value() << "\n";

        // --------------------------------------------------------------------
        // Second largest
        // --------------------------------------------------------------------

        subsection("7. Second-largest distinct quantity");

        const auto secondLargest =
            inventory.secondLargestDistinct();

        if (secondLargest.has_value()) {
            cout << "Second-largest distinct quantity: "
                 << secondLargest.value() << "\n";
        }
        else {
            cout << "There is no second-largest distinct quantity.\n";
        }

        // --------------------------------------------------------------------
        // Frequency counting
        // --------------------------------------------------------------------

        subsection("8. Frequency counting");

        const auto frequencies =
            inventory.frequencyCount();

        /*
         * unordered_map does not guarantee output order. That is acceptable
         * because frequency counting cares about key/value relationships,
         * not key order.
         */
        for (const auto& [value, frequency] : frequencies) {
            cout << "Quantity " << value
                 << " occurs " << frequency << " time(s)\n";
        }

        // --------------------------------------------------------------------
        // Positive / negative / zero analysis
        // --------------------------------------------------------------------

        subsection("9. Sign analysis");

        const auto signCounts = inventory.countSigns();

        cout << "Positive values: "
             << signCounts.positive << "\n";

        cout << "Negative values: "
             << signCounts.negative << "\n";

        cout << "Zero values: "
             << signCounts.zero << "\n";

        // --------------------------------------------------------------------
        // Prefix sums
        // --------------------------------------------------------------------

        subsection("10. Prefix sums");

        const auto prefix = inventory.prefixSums();

        cout << "Prefix sums: ";
        printVector(prefix);
        cout << "\n";

        if (!prefix.empty()) {
            cout << "Sum of slots 2..5: "
                 << InventoryAnalytics::rangeSum(prefix, 2, 5)
                 << "\n";
        }

        // --------------------------------------------------------------------
        // Duplicate removal
        // --------------------------------------------------------------------

        subsection("11. Duplicate removal");

        InventoryAnalytics uniqueInventory = inventory;

        cout << "Before duplicate removal: ";
        printVector(uniqueInventory.data());
        cout << "\n";

        uniqueInventory.removeDuplicatesPreserveOrder();

        cout << "After duplicate removal: ";
        printVector(uniqueInventory.data());
        cout << "\n";

        // --------------------------------------------------------------------
        // Reverse
        // --------------------------------------------------------------------

        subsection("12. Reverse array");

        InventoryAnalytics reversedInventory({
            10, 20, 30, 40, 50
        });

        cout << "Before: ";
        printVector(reversedInventory.data());
        cout << "\n";

        reversedInventory.reverseInPlace();

        cout << "After: ";
        printVector(reversedInventory.data());
        cout << "\n";

        // --------------------------------------------------------------------
        // Rotation
        // --------------------------------------------------------------------

        subsection("13. Rotate array");

        InventoryAnalytics rotatedInventory({
            1, 2, 3, 4, 5
        });

        rotatedInventory.rotateRight(2);

        cout << "Rotated right by 2: ";
        printVector(rotatedInventory.data());
        cout << "\n";

        // --------------------------------------------------------------------
        // Binary search
        // --------------------------------------------------------------------

        subsection("14. Binary search");

        InventoryAnalytics sortedInventory({
            5, 12, 18, 24, 31, 42, 57, 80
        });

        cout << "Sorted quantities: ";
        printVector(sortedInventory.data());
        cout << "\n";

        const auto binaryResult =
            sortedInventory.binarySearch(42);

        cout << "Searching for 42: ";

        if (binaryResult.has_value()) {
            cout << "found at index "
                 << binaryResult.value() << "\n";
        }
        else {
            cout << "not found\n";
        }

        // --------------------------------------------------------------------
        // Missing values
        // --------------------------------------------------------------------

        subsection("15. Missing value detection");

        const vector<int> sequence = {
            0, 1, 3, 4, 5
        };

        cout << "Sequence: ";
        printVector(sequence);
        cout << "\n";

        const auto missing =
            findSingleMissingValue(sequence, 5);

        if (missing.has_value()) {
            cout << "Missing value: "
                 << missing.value() << "\n";
        }

        // --------------------------------------------------------------------
        // Edge conditions
        // --------------------------------------------------------------------

        subsection("16. Edge conditions");

        InventoryAnalytics emptyInventory({});

        cout << "Empty inventory size: "
             << emptyInventory.size() << "\n";

        cout << "Empty minimum exists: "
             << (emptyInventory.minimum().has_value() ? "yes" : "no")
             << "\n";

        cout << "Empty maximum exists: "
             << (emptyInventory.maximum().has_value() ? "yes" : "no")
             << "\n";

        try {
            emptyInventory.at(0);
        }
        catch (const std::out_of_range& error) {
            cout << "Invalid index handled: "
                 << error.what() << "\n";
        }

        try {
            InventoryAnalytics unsorted({
                10, 4, 7, 2
            });

            unsorted.binarySearch(7);
        }
        catch (const std::logic_error& error) {
            cout << "Binary-search precondition handled: "
                 << error.what() << "\n";
        }

        // --------------------------------------------------------------------
        // Complexity discussion
        // --------------------------------------------------------------------

        subsection("17. Complexity reference");

        cout << std::left
             << std::setw(35) << "Operation"
             << std::setw(18) << "Time"
             << "Extra space\n";

        cout << string(70, '-') << "\n";

        const vector<tuple<string, string, string>> complexity = {
            {"Index access", "O(1)", "O(1)"},
            {"Update", "O(1)", "O(1)"},
            {"Traversal", "O(n)", "O(1)"},
            {"Linear search", "O(n)", "O(1)"},
            {"Minimum", "O(n)", "O(1)"},
            {"Maximum", "O(n)", "O(1)"},
            {"Second-largest", "O(n)", "O(1)"},
            {"Frequency counting", "O(n) average", "O(k)"},
            {"Reverse", "O(n)", "O(1)"},
            {"Rotation", "O(n)", "O(1)"},
            {"Duplicate removal", "O(n) average", "O(k)"},
            {"Binary search", "O(log n)", "O(1)"},
            {"Prefix sums", "O(n)", "O(n)"}
        };

        for (const auto& [operation, time, space] : complexity) {
            cout << std::left
                 << std::setw(35) << operation
                 << std::setw(18) << time
                 << space << "\n";
        }

        // --------------------------------------------------------------------
        // Automated verification
        // --------------------------------------------------------------------

        runTests();

        section("Practice checklist");

        const vector<string> practiceTasks = {
            "Maximum element",
            "Minimum element",
            "Second-largest element",
            "Reverse array",
            "Rotate array",
            "Remove duplicates",
            "Count positive/negative values",
            "Find missing values"
        };

        for (size_t index = 0; index < practiceTasks.size(); ++index) {
            cout << index + 1 << ". "
                 << practiceTasks[index] << "\n";
        }

        cout << "\nDay 12 case study completed successfully.\n";

        return 0;
    }
    catch (const std::exception& error) {
        std::cerr << "Fatal error: "
                  << error.what() << "\n";
        return 1;
    }
}
