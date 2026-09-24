/*
Day 6 — Arrays, Strings and Basic Problem Solving

C++17 case study:
A small Inventory Analysis System.

The system demonstrates:
- arrays and vectors
- string traversal
- indexing
- linear searching
- counting
- maximum and minimum
- sum and average
- reversal
- palindrome checking
- duplicate detection
- second-largest value
- even/odd counting
- validation
- classes and functions
- sorting
- exception handling
- algorithmic complexity
- realistic data processing

Compile:
    g++ -std=c++17 -Wall -Wextra -pedantic day6_arrays_strings.cpp -o day6

Run:
    ./day6
*/

#include <algorithm>
#include <cctype>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

// -----------------------------------------------------------------------------
// Basic array/vector operations
// -----------------------------------------------------------------------------

int findMaximum(const vector<int>& values) {
    if (values.empty()) {
        throw invalid_argument("Cannot find maximum of an empty array.");
    }

    int maximum = values[0];

    for (size_t index = 1; index < values.size(); ++index) {
        if (values[index] > maximum) {
            maximum = values[index];
        }
    }

    return maximum;
}

int findMinimum(const vector<int>& values) {
    if (values.empty()) {
        throw invalid_argument("Cannot find minimum of an empty array.");
    }

    int minimum = values[0];

    for (size_t index = 1; index < values.size(); ++index) {
        if (values[index] < minimum) {
            minimum = values[index];
        }
    }

    return minimum;
}

long long calculateSum(const vector<int>& values) {
    long long total = 0;

    for (int value : values) {
        total += value;
    }

    return total;
}

double calculateAverage(const vector<int>& values) {
    if (values.empty()) {
        throw invalid_argument("Cannot calculate average of an empty array.");
    }

    return static_cast<double>(calculateSum(values)) / values.size();
}

int linearSearch(const vector<int>& values, int target) {
    for (size_t index = 0; index < values.size(); ++index) {
        if (values[index] == target) {
            return static_cast<int>(index);
        }
    }

    return -1;
}

int countOccurrences(const vector<int>& values, int target) {
    int count = 0;

    for (int value : values) {
        if (value == target) {
            ++count;
        }
    }

    return count;
}

vector<int> findAllPositions(const vector<int>& values, int target) {
    vector<int> positions;

    for (size_t index = 0; index < values.size(); ++index) {
        if (values[index] == target) {
            positions.push_back(static_cast<int>(index));
        }
    }

    return positions;
}

// -----------------------------------------------------------------------------
// Reversal and palindrome operations
// -----------------------------------------------------------------------------

void reverseArrayInPlace(vector<int>& values) {
    size_t left = 0;
    size_t right = values.size();

    if (right == 0) {
        return;
    }

    --right;

    while (left < right) {
        swap(values[left], values[right]);
        ++left;
        --right;
    }
}

string reverseString(const string& text) {
    string reversed;
    reversed.reserve(text.size());

    for (auto iterator = text.rbegin(); iterator != text.rend(); ++iterator) {
        reversed.push_back(*iterator);
    }

    return reversed;
}

bool isPalindrome(const string& text) {
    vector<char> normalized;

    for (unsigned char character : text) {
        if (isalnum(character)) {
            normalized.push_back(
                static_cast<char>(tolower(character))
            );
        }
    }

    if (normalized.empty()) {
        return true;
    }

    size_t left = 0;
    size_t right = normalized.size() - 1;

    while (left < right) {
        if (normalized[left] != normalized[right]) {
            return false;
        }

        ++left;
        --right;
    }

    return true;
}

// -----------------------------------------------------------------------------
// Counting and duplicate detection
// -----------------------------------------------------------------------------

map<char, int> countCharacters(const string& text) {
    map<char, int> frequency;

    for (char character : text) {
        ++frequency[character];
    }

    return frequency;
}

vector<int> findDuplicateValues(const vector<int>& values) {
    unordered_set<int> seen;
    set<int> duplicates;

    for (int value : values) {
        if (seen.find(value) != seen.end()) {
            duplicates.insert(value);
        } else {
            seen.insert(value);
        }
    }

    return vector<int>(duplicates.begin(), duplicates.end());
}

optional<int> findFirstDuplicate(const vector<int>& values) {
    unordered_set<int> seen;

    for (int value : values) {
        if (seen.find(value) != seen.end()) {
            return value;
        }

        seen.insert(value);
    }

    return nullopt;
}

int findSecondLargest(const vector<int>& values) {
    if (values.size() < 2) {
        throw invalid_argument("At least two values are required.");
    }

    optional<int> largest;
    optional<int> secondLargest;

    for (int value : values) {
        if (!largest.has_value() || value > largest.value()) {
            secondLargest = largest;
            largest = value;
        } else if (
            value != largest.value() &&
            (!secondLargest.has_value() || value > secondLargest.value())
        ) {
            secondLargest = value;
        }
    }

    if (!secondLargest.has_value()) {
        throw invalid_argument(
            "At least two distinct values are required."
        );
    }

    return secondLargest.value();
}

pair<int, int> countEvenAndOdd(const vector<int>& values) {
    int evenCount = 0;
    int oddCount = 0;

    for (int value : values) {
        if (value % 2 == 0) {
            ++evenCount;
        } else {
            ++oddCount;
        }
    }

    return {evenCount, oddCount};
}

// -----------------------------------------------------------------------------
// Additional array operations
// -----------------------------------------------------------------------------

vector<int> removeDuplicatesPreservingOrder(const vector<int>& values) {
    unordered_set<int> seen;
    vector<int> result;

    for (int value : values) {
        if (seen.insert(value).second) {
            result.push_back(value);
        }
    }

    return result;
}

vector<int> findCommonValues(
    const vector<int>& first,
    const vector<int>& second
) {
    unordered_set<int> secondSet(second.begin(), second.end());
    set<int> common;

    for (int value : first) {
        if (secondSet.find(value) != secondSet.end()) {
            common.insert(value);
        }
    }

    return vector<int>(common.begin(), common.end());
}

void moveZerosToEnd(vector<int>& values) {
    size_t writePosition = 0;

    for (int value : values) {
        if (value != 0) {
            values[writePosition] = value;
            ++writePosition;
        }
    }

    while (writePosition < values.size()) {
        values[writePosition] = 0;
        ++writePosition;
    }
}

bool isSortedAscending(const vector<int>& values) {
    for (size_t index = 1; index < values.size(); ++index) {
        if (values[index] < values[index - 1]) {
            return false;
        }
    }

    return true;
}

// -----------------------------------------------------------------------------
// Inventory item
// -----------------------------------------------------------------------------

class InventoryItem {
private:
    int productId;
    string productName;
    int quantity;
    double unitPrice;

public:
    InventoryItem(
        int id,
        string name,
        int itemQuantity,
        double price
    )
        : productId(id),
          productName(move(name)),
          quantity(itemQuantity),
          unitPrice(price) {
        if (productId <= 0) {
            throw invalid_argument("Product ID must be positive.");
        }

        if (productName.empty()) {
            throw invalid_argument("Product name cannot be empty.");
        }

        if (quantity < 0) {
            throw invalid_argument("Quantity cannot be negative.");
        }

        if (unitPrice < 0.0) {
            throw invalid_argument("Unit price cannot be negative.");
        }
    }

    int getId() const {
        return productId;
    }

    const string& getName() const {
        return productName;
    }

    int getQuantity() const {
        return quantity;
    }

    double getUnitPrice() const {
        return unitPrice;
    }

    double inventoryValue() const {
        return quantity * unitPrice;
    }

    bool isLowStock(int threshold) const {
        return quantity <= threshold;
    }
};

// -----------------------------------------------------------------------------
// Inventory analysis system
// -----------------------------------------------------------------------------

class InventoryAnalyzer {
private:
    vector<InventoryItem> items;

public:
    void addItem(const InventoryItem& item) {
        // IDs are expected to be unique. A linear scan is appropriate for
        // this small educational system; a production-scale system could
        // maintain an unordered_map<int, InventoryItem> for faster lookup.
        if (findItemById(item.getId()).has_value()) {
            throw invalid_argument("Duplicate product ID.");
        }

        items.push_back(item);
    }

    optional<InventoryItem> findItemById(int productId) const {
        for (const auto& item : items) {
            if (item.getId() == productId) {
                return item;
            }
        }

        return nullopt;
    }

    vector<int> quantities() const {
        vector<int> result;

        for (const auto& item : items) {
            result.push_back(item.getQuantity());
        }

        return result;
    }

    double totalInventoryValue() const {
        double total = 0.0;

        for (const auto& item : items) {
            total += item.inventoryValue();
        }

        return total;
    }

    int maximumQuantity() const {
        return findMaximum(quantities());
    }

    int minimumQuantity() const {
        return findMinimum(quantities());
    }

    double averageQuantity() const {
        return calculateAverage(quantities());
    }

    vector<string> lowStockProducts(int threshold) const {
        if (threshold < 0) {
            throw invalid_argument("Stock threshold cannot be negative.");
        }

        vector<string> result;

        for (const auto& item : items) {
            if (item.isLowStock(threshold)) {
                result.push_back(item.getName());
            }
        }

        return result;
    }

    vector<string> duplicateProductNames() const {
        vector<string> names;

        for (const auto& item : items) {
            names.push_back(item.getName());
        }

        unordered_set<string> seen;
        set<string> duplicates;

        for (const string& name : names) {
            if (!seen.insert(name).second) {
                duplicates.insert(name);
            }
        }

        return vector<string>(duplicates.begin(), duplicates.end());
    }

    void printReport() const {
        cout << "\n=== INVENTORY REPORT ===\n";

        cout << left
             << setw(8) << "ID"
             << setw(24) << "Product"
             << setw(10) << "Qty"
             << setw(14) << "Price"
             << setw(16) << "Value"
             << '\n';

        cout << string(72, '-') << '\n';

        cout << fixed << setprecision(2);

        for (const auto& item : items) {
            cout << left
                 << setw(8) << item.getId()
                 << setw(24) << item.getName()
                 << setw(10) << item.getQuantity()
                 << setw(14) << item.getUnitPrice()
                 << setw(16) << item.inventoryValue()
                 << '\n';
        }

        if (!items.empty()) {
            cout << "\nTotal inventory value: "
                 << totalInventoryValue() << '\n';

            cout << "Maximum quantity: "
                 << maximumQuantity() << '\n';

            cout << "Minimum quantity: "
                 << minimumQuantity() << '\n';

            cout << "Average quantity: "
                 << averageQuantity() << '\n';
        }
    }

    size_t size() const {
        return items.size();
    }
};

// -----------------------------------------------------------------------------
// Input parsing utility
// -----------------------------------------------------------------------------

vector<int> parseIntegerList(const string& input) {
    istringstream stream(input);
    vector<int> values;
    int value;

    while (stream >> value) {
        values.push_back(value);
    }

    if (values.empty()) {
        throw invalid_argument("No valid integers were found.");
    }

    return values;
}

// -----------------------------------------------------------------------------
// Display utilities
// -----------------------------------------------------------------------------

void printVector(const vector<int>& values) {
    cout << '[';

    for (size_t index = 0; index < values.size(); ++index) {
        cout << values[index];

        if (index + 1 < values.size()) {
            cout << ", ";
        }
    }

    cout << ']';
}

void printStringVector(const vector<string>& values) {
    cout << '[';

    for (size_t index = 0; index < values.size(); ++index) {
        cout << '"' << values[index] << '"';

        if (index + 1 < values.size()) {
            cout << ", ";
        }
    }

    cout << ']';
}

void printCharacterFrequency(const map<char, int>& frequency) {
    cout << '{';

    bool first = true;

    for (const auto& [character, count] : frequency) {
        if (!first) {
            cout << ", ";
        }

        cout << "'" << character << "': " << count;
        first = false;
    }

    cout << '}';
}

// -----------------------------------------------------------------------------
// Case study demonstration
// -----------------------------------------------------------------------------

void demonstrateCaseStudy() {
    cout << "\n============================================================\n";
    cout << "DAY 6 — INVENTORY ANALYSIS CASE STUDY\n";
    cout << "============================================================\n";

    InventoryAnalyzer inventory;

    inventory.addItem(
        InventoryItem(101, "Keyboard", 24, 1499.00)
    );

    inventory.addItem(
        InventoryItem(102, "Mouse", 42, 799.00)
    );

    inventory.addItem(
        InventoryItem(103, "Monitor", 8, 12999.00)
    );

    inventory.addItem(
        InventoryItem(104, "USB Cable", 60, 299.00)
    );

    inventory.addItem(
        InventoryItem(105, "Laptop Stand", 8, 1899.00)
    );

    inventory.printReport();

    cout << "\nLow-stock products at threshold 10: ";
    printStringVector(inventory.lowStockProducts(10));
    cout << '\n';

    cout << "Inventory item count: "
         << inventory.size() << '\n';

    cout << "\nSearch product ID 103:\n";

    optional<InventoryItem> monitor = inventory.findItemById(103);

    if (monitor.has_value()) {
        cout << "Found: " << monitor->getName()
             << ", quantity=" << monitor->getQuantity()
             << ", price=" << monitor->getUnitPrice()
             << '\n';
    } else {
        cout << "Product not found.\n";
    }

    cout << "\nSearch product ID 999:\n";

    optional<InventoryItem> missing = inventory.findItemById(999);

    if (!missing.has_value()) {
        cout << "Product 999 was not found. This is a normal search miss.\n";
    }
}

// -----------------------------------------------------------------------------
// Fundamental demonstrations
// -----------------------------------------------------------------------------

void demonstrateFundamentals() {
    cout << "\n=== FUNDAMENTAL ARRAY OPERATIONS ===\n";

    vector<int> values = {10, 20, 30, 40, 50};

    cout << "Array: ";
    printVector(values);
    cout << '\n';

    cout << "Index 0: " << values[0] << '\n';
    cout << "Last element: " << values[values.size() - 1] << '\n';

    cout << "Traversal: ";

    for (size_t index = 0; index < values.size(); ++index) {
        cout << values[index] << ' ';
    }

    cout << '\n';

    values[2] = 35;

    cout << "After changing index 2: ";
    printVector(values);
    cout << '\n';

    cout << "Maximum: " << findMaximum(values) << '\n';
    cout << "Minimum: " << findMinimum(values) << '\n';
    cout << "Sum: " << calculateSum(values) << '\n';
    cout << "Average: " << calculateAverage(values) << '\n';

    cout << "\n=== STRING OPERATIONS ===\n";

    string text = "Algorithm";

    cout << "String: " << text << '\n';
    cout << "First character: " << text[0] << '\n';
    cout << "Last character: " << text[text.size() - 1] << '\n';

    cout << "Characters: ";

    for (char character : text) {
        cout << character << ' ';
    }

    cout << '\n';

    cout << "Reversed: " << reverseString(text) << '\n';
    cout << "Palindrome 'racecar': "
         << boolalpha << isPalindrome("racecar") << '\n';
    cout << "Palindrome 'hello': "
         << isPalindrome("hello") << '\n';

    cout << "\nCharacter frequency for 'banana': ";
    printCharacterFrequency(countCharacters("banana"));
    cout << '\n';
}

// -----------------------------------------------------------------------------
// Edge-case demonstration
// -----------------------------------------------------------------------------

void demonstrateEdgeCases() {
    cout << "\n=== EDGE CASES ===\n";

    vector<int> empty;
    vector<int> oneValue = {42};
    vector<int> allEqual = {7, 7, 7, 7};
    vector<int> negatives = {-10, -4, -25};

    cout << "Empty array size: " << empty.size() << '\n';
    cout << "One value maximum: " << findMaximum(oneValue) << '\n';
    cout << "All equal second-largest: ";

    try {
        cout << findSecondLargest(allEqual) << '\n';
    } catch (const exception& error) {
        cout << "Handled error: " << error.what() << '\n';
    }

    cout << "Negative minimum: "
         << findMinimum(negatives) << '\n';

    cout << "Empty string palindrome: "
         << isPalindrome("") << '\n';

    cout << "One-character palindrome: "
         << isPalindrome("x") << '\n';
}

// -----------------------------------------------------------------------------
// Test suite
// -----------------------------------------------------------------------------

void runTests() {
    cout << "\n=== TEST SUITE ===\n";

    const vector<int> numbers = {4, 2, 9, 2, 7};

    if (findMaximum(numbers) != 9) {
        throw runtime_error("Maximum test failed.");
    }

    if (findMinimum(numbers) != 2) {
        throw runtime_error("Minimum test failed.");
    }

    if (calculateSum(numbers) != 24) {
        throw runtime_error("Sum test failed.");
    }

    if (calculateAverage(numbers) != 4.8) {
        throw runtime_error("Average test failed.");
    }

    if (linearSearch(numbers, 9) != 2) {
        throw runtime_error("Search test failed.");
    }

    if (linearSearch(numbers, 100) != -1) {
        throw runtime_error("Missing search test failed.");
    }

    if (countOccurrences(numbers, 2) != 2) {
        throw runtime_error("Count test failed.");
    }

    if (findAllPositions(numbers, 2) != vector<int>({1, 3})) {
        throw runtime_error("Position test failed.");
    }

    vector<int> reversed = numbers;
    reverseArrayInPlace(reversed);

    if (reversed != vector<int>({7, 2, 9, 2, 4})) {
        throw runtime_error("Array reversal test failed.");
    }

    if (reverseString("hello") != "olleh") {
        throw runtime_error("String reversal test failed.");
    }

    if (!isPalindrome("racecar")) {
        throw runtime_error("Palindrome test failed.");
    }

    if (isPalindrome("python")) {
        throw runtime_error("Non-palindrome test failed.");
    }

    if (findDuplicateValues(numbers) != vector<int>({2})) {
        throw runtime_error("Duplicate test failed.");
    }

    optional<int> firstDuplicate = findFirstDuplicate(numbers);

    if (!firstDuplicate.has_value() || firstDuplicate.value() != 2) {
        throw runtime_error("First duplicate test failed.");
    }

    if (findSecondLargest(numbers) != 7) {
        throw runtime_error("Second-largest test failed.");
    }

    auto [evenCount, oddCount] = countEvenAndOdd(
        vector<int>{1, 2, 3, 4, 6}
    );

    if (evenCount != 3 || oddCount != 2) {
        throw runtime_error("Even/odd test failed.");
    }

    if (!isSortedAscending(vector<int>{1, 2, 2, 5})) {
        throw runtime_error("Sorted test failed.");
    }

    if (isSortedAscending(vector<int>{1, 4, 2})) {
        throw runtime_error("Unsorted test failed.");
    }

    vector<int> zeros = {0, 1, 0, 3, 12};
    moveZerosToEnd(zeros);

    if (zeros != vector<int>({1, 3, 12, 0, 0})) {
        throw runtime_error("Zero movement test failed.");
    }

    cout << "All tests passed.\n";
}

// -----------------------------------------------------------------------------
// Complexity reference
// -----------------------------------------------------------------------------

void printComplexityReference() {
    cout << "\n=== COMPLEXITY REFERENCE ===\n";

    cout << left
         << setw(34) << "Operation"
         << setw(16) << "Time"
         << "Extra space\n";

    cout << string(65, '-') << '\n';

    cout << setw(34) << "Array traversal"
         << setw(16) << "O(n)"
         << "O(1)\n";

    cout << setw(34) << "Linear search"
         << setw(16) << "O(n)"
         << "O(1)\n";

    cout << setw(34) << "Maximum/minimum"
         << setw(16) << "O(n)"
         << "O(1)\n";

    cout << setw(34) << "Two-pointer reversal"
         << setw(16) << "O(n)"
         << "O(1)\n";

    cout << setw(34) << "Character frequency"
         << setw(16) << "O(n)"
         << "O(k)\n";

    cout << setw(34) << "Duplicate detection"
         << setw(16) << "O(n) average"
         << "O(n)\n";

    cout << setw(34) << "Naive pair comparison"
         << setw(16) << "O(n^2)"
         << "O(1)\n";
}

// -----------------------------------------------------------------------------
// Main
// -----------------------------------------------------------------------------

int main() {
    try {
        demonstrateFundamentals();

        cout << "\n=== SEARCHING ===\n";

        vector<int> searchValues = {5, 9, 2, 9, 7, 9};

        cout << "Array: ";
        printVector(searchValues);
        cout << '\n';

        cout << "Index of 7: "
             << linearSearch(searchValues, 7) << '\n';

        cout << "Occurrences of 9: "
             << countOccurrences(searchValues, 9) << '\n';

        cout << "Positions of 9: ";
        printVector(findAllPositions(searchValues, 9));
        cout << '\n';

        cout << "\n=== DUPLICATES ===\n";

        vector<int> duplicateValues = {4, 7, 4, 2, 7, 7, 9};

        cout << "Duplicate values: ";
        printVector(findDuplicateValues(duplicateValues));
        cout << '\n';

        optional<int> duplicate = findFirstDuplicate(duplicateValues);

        cout << "First duplicate: ";

        if (duplicate.has_value()) {
            cout << duplicate.value();
        } else {
            cout << "none";
        }

        cout << '\n';

        cout << "\n=== SECOND LARGEST ===\n";
        cout << "Second distinct-largest of [10, 20, 20, 5, 15]: "
             << findSecondLargest({10, 20, 20, 5, 15})
             << '\n';

        cout << "\n=== EVEN AND ODD ===\n";

        auto [evenCount, oddCount] =
            countEvenAndOdd({1, 2, 3, 4, 5, 6});

        cout << "Even count: " << evenCount << '\n';
        cout << "Odd count: " << oddCount << '\n';

        cout << "\n=== ADDITIONAL ARRAY OPERATIONS ===\n";

        vector<int> valuesWithDuplicates = {4, 2, 4, 1, 2, 3};

        cout << "Without duplicates: ";
        printVector(removeDuplicatesPreservingOrder(valuesWithDuplicates));
        cout << '\n';

        cout << "Common values: ";
        printVector(findCommonValues(
            {1, 2, 3, 4},
            {3, 4, 5, 6}
        ));
        cout << '\n';

        vector<int> zeros = {0, 4, 0, 5, 2, 0, 8};
        moveZerosToEnd(zeros);

        cout << "Zeros moved to end: ";
        printVector(zeros);
        cout << '\n';

        cout << "\n=== STRING PROBLEMS ===\n";

        cout << "Reverse: "
             << reverseString("programming") << '\n';

        cout << "Palindrome: "
             << boolalpha
             << isPalindrome("Never odd or even")
             << '\n';

        cout << "Character frequencies: ";
        printCharacterFrequency(
            countCharacters("data structures")
        );
        cout << '\n';

        demonstrateCaseStudy();
        demonstrateEdgeCases();
        printComplexityReference();
        runTests();

        cout << "\nProgram completed successfully.\n";
    } catch (const exception& error) {
        cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
