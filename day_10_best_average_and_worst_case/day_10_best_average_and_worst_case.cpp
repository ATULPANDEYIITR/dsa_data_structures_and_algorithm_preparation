/*
 * Day 10 — Best, Average and Worst Case
 *
 * C++17 case study:
 * Performance-aware student record management system.
 *
 * The system demonstrates:
 *   - linear search
 *   - binary search
 *   - sorting
 *   - hash-table lookup
 *   - vector operations
 *   - linked-list operations
 *   - validation
 *   - error handling
 *   - complexity analysis
 *   - performance measurement
 *
 * Compile:
 *   g++ -std=c++17 -O2 day10_complexity.cpp -o day10_complexity
 *
 * Run:
 *   ./day10_complexity
 */

#include <algorithm>
#include <chrono>
#include <functional>
#include <iomanip>
#include <iostream>
#include <list>
#include <optional>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;
using Clock = chrono::high_resolution_clock;


// ============================================================
// 1. DOMAIN MODEL
// ============================================================

struct Student {
    int id;
    string name;
    double score;

    bool operator<(const Student& other) const {
        return id < other.id;
    }
};

ostream& operator<<(ostream& output, const Student& student) {
    output << "{id=" << student.id
           << ", name=" << student.name
           << ", score=" << fixed << setprecision(1)
           << student.score << "}";

    return output;
}


// ============================================================
// 2. VALIDATION
// ============================================================

void validateStudent(const Student& student) {
    if (student.id <= 0) {
        throw invalid_argument("Student ID must be positive.");
    }

    if (student.name.empty()) {
        throw invalid_argument("Student name cannot be empty.");
    }

    if (student.score < 0.0 || student.score > 100.0) {
        throw invalid_argument("Score must be between 0 and 100.");
    }
}


// ============================================================
// 3. LINEAR SEARCH
// ============================================================

int linearSearchById(
    const vector<Student>& students,
    int targetId
) {
    for (size_t index = 0; index < students.size(); ++index) {
        if (students[index].id == targetId) {
            return static_cast<int>(index);
        }
    }

    return -1;
}


// ============================================================
// 4. BINARY SEARCH
// ============================================================

int binarySearchById(
    const vector<Student>& sortedStudents,
    int targetId
) {
    int left = 0;
    int right = static_cast<int>(sortedStudents.size()) - 1;

    while (left <= right) {
        const int middle = left + (right - left) / 2;

        if (sortedStudents[middle].id == targetId) {
            return middle;
        }

        if (sortedStudents[middle].id < targetId) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return -1;
}


// ============================================================
// 5. INSERTION SORT
// ============================================================

void insertionSort(vector<Student>& students) {
    /*
     * Insertion sort is useful for demonstrating the difference
     * between input-sensitive and input-insensitive behavior.
     *
     * Best case:
     *     O(n) when already sorted.
     *
     * Worst case:
     *     O(n²) when reverse sorted.
     */
    for (size_t position = 1; position < students.size(); ++position) {
        Student current = students[position];
        int previous = static_cast<int>(position) - 1;

        while (
            previous >= 0 &&
            students[previous].id > current.id
        ) {
            students[previous + 1] = students[previous];
            --previous;
        }

        students[previous + 1] = current;
    }
}


// ============================================================
// 6. MERGE SORT
// ============================================================

void mergeRange(
    vector<Student>& students,
    vector<Student>& temporary,
    int left,
    int middle,
    int right
) {
    int leftIndex = left;
    int rightIndex = middle + 1;
    int outputIndex = left;

    while (leftIndex <= middle && rightIndex <= right) {
        if (students[leftIndex].id <= students[rightIndex].id) {
            temporary[outputIndex++] = students[leftIndex++];
        } else {
            temporary[outputIndex++] = students[rightIndex++];
        }
    }

    while (leftIndex <= middle) {
        temporary[outputIndex++] = students[leftIndex++];
    }

    while (rightIndex <= right) {
        temporary[outputIndex++] = students[rightIndex++];
    }

    for (int index = left; index <= right; ++index) {
        students[index] = temporary[index];
    }
}

void mergeSortRecursive(
    vector<Student>& students,
    vector<Student>& temporary,
    int left,
    int right
) {
    if (left >= right) {
        return;
    }

    const int middle = left + (right - left) / 2;

    mergeSortRecursive(
        students,
        temporary,
        left,
        middle
    );

    mergeSortRecursive(
        students,
        temporary,
        middle + 1,
        right
    );

    mergeRange(
        students,
        temporary,
        left,
        middle,
        right
    );
}

void mergeSort(vector<Student>& students) {
    if (students.size() < 2) {
        return;
    }

    vector<Student> temporary(students.size());

    mergeSortRecursive(
        students,
        temporary,
        0,
        static_cast<int>(students.size()) - 1
    );
}


// ============================================================
// 7. LINKED-LIST MODEL
// ============================================================

class StudentLinkedList {
private:
    struct Node {
        Student student;
        Node* next;

        explicit Node(const Student& value)
            : student(value), next(nullptr) {}
    };

    Node* head = nullptr;
    Node* tail = nullptr;
    size_t count = 0;

public:
    StudentLinkedList() = default;

    ~StudentLinkedList() {
        clear();
    }

    StudentLinkedList(const StudentLinkedList&) = delete;
    StudentLinkedList& operator=(const StudentLinkedList&) = delete;

    void prepend(const Student& student) {
        Node* node = new Node(student);

        node->next = head;
        head = node;

        if (tail == nullptr) {
            tail = node;
        }

        ++count;
    }

    void append(const Student& student) {
        Node* node = new Node(student);

        if (head == nullptr) {
            head = node;
            tail = node;
        } else {
            tail->next = node;
            tail = node;
        }

        ++count;
    }

    optional<Student> findById(int id) const {
        Node* current = head;

        while (current != nullptr) {
            if (current->student.id == id) {
                return current->student;
            }

            current = current->next;
        }

        return nullopt;
    }

    bool deleteById(int id) {
        Node* previous = nullptr;
        Node* current = head;

        while (current != nullptr) {
            if (current->student.id == id) {
                if (previous == nullptr) {
                    head = current->next;
                } else {
                    previous->next = current->next;
                }

                if (current == tail) {
                    tail = previous;
                }

                delete current;
                --count;

                if (count == 0) {
                    head = nullptr;
                    tail = nullptr;
                }

                return true;
            }

            previous = current;
            current = current->next;
        }

        return false;
    }

    size_t size() const {
        return count;
    }

    void print() const {
        Node* current = head;

        while (current != nullptr) {
            cout << current->student << '\n';
            current = current->next;
        }
    }

    void clear() {
        Node* current = head;

        while (current != nullptr) {
            Node* next = current->next;
            delete current;
            current = next;
        }

        head = nullptr;
        tail = nullptr;
        count = 0;
    }
};


// ============================================================
// 8. DATA GENERATION
// ============================================================

vector<Student> generateStudents(size_t count) {
    vector<Student> students;
    students.reserve(count);

    for (size_t index = 0; index < count; ++index) {
        Student student{
            static_cast<int>(index + 1),
            "Student_" + to_string(index + 1),
            static_cast<double>((index * 37) % 101)
        };

        students.push_back(student);
    }

    return students;
}


// ============================================================
// 9. HASH-TABLE INDEX
// ============================================================

class StudentDirectory {
private:
    unordered_map<int, Student> records;

public:
    void insert(const Student& student) {
        validateStudent(student);
        records[student.id] = student;
    }

    optional<Student> find(int id) const {
        auto iterator = records.find(id);

        if (iterator == records.end()) {
            return nullopt;
        }

        return iterator->second;
    }

    bool erase(int id) {
        return records.erase(id) > 0;
    }

    size_t size() const {
        return records.size();
    }
};


// ============================================================
// 10. COMPLEXITY-AWARE RECORD SERVICE
// ============================================================

class StudentRecordService {
private:
    vector<Student> records;

public:
    void addStudent(const Student& student) {
        validateStudent(student);
        records.push_back(student);
    }

    size_t size() const {
        return records.size();
    }

    int linearFind(int id) const {
        return linearSearchById(records, id);
    }

    void sortById() {
        mergeSort(records);
    }

    int binaryFind(int id) const {
        return binarySearchById(records, id);
    }

    const vector<Student>& data() const {
        return records;
    }
};


// ============================================================
// 11. PERFORMANCE MEASUREMENT
// ============================================================

template <typename Function>
double measureMilliseconds(Function operation) {
    const auto start = Clock::now();

    operation();

    const auto end = Clock::now();

    return chrono::duration<double, milli>(end - start).count();
}


// ============================================================
// 12. SEARCH CASE DEMONSTRATION
// ============================================================

void demonstrateSearchCases() {
    cout << "\n" << string(80, '=') << '\n';
    cout << "SEARCH: BEST, AVERAGE AND WORST CASE\n";
    cout << string(80, '=') << '\n';

    vector<int> data{10, 20, 30, 40, 50};

    cout << "Data: ";

    for (int value : data) {
        cout << value << ' ';
    }

    cout << "\n\n";

    cout << "Linear search for first element: "
         << linearSearchById(
                vector<Student>{
                    {10, "A", 90},
                    {20, "B", 80},
                    {30, "C", 70}
                },
                10
            )
         << '\n';

    cout << "Linear search complexity:\n";
    cout << "Best    O(1)\n";
    cout << "Average O(n)\n";
    cout << "Worst   O(n)\n";

    cout << "\nBinary search requires sorted data.\n";
    cout << "Binary search complexity:\n";
    cout << "Best    O(1)\n";
    cout << "Average O(log n)\n";
    cout << "Worst   O(log n)\n";
}


// ============================================================
// 13. ARRAY/VECTOR OPERATIONS
// ============================================================

void demonstrateVectorOperations() {
    cout << "\n" << string(80, '=') << '\n';
    cout << "VECTOR OPERATIONS\n";
    cout << string(80, '=') << '\n';

    vector<int> values{10, 20, 30, 40, 50};

    cout << "values[2]: " << values[2] << '\n';
    cout << "Random access: O(1)\n";

    values[2] = 35;

    cout << "After update: ";

    for (int value : values) {
        cout << value << ' ';
    }

    cout << "\nUpdate complexity: O(1)\n";

    values.push_back(60);

    cout << "After push_back: ";

    for (int value : values) {
        cout << value << ' ';
    }

    cout << "\npush_back: O(1) amortized\n";

    values.insert(values.begin(), 5);

    cout << "After insertion at front: ";

    for (int value : values) {
        cout << value << ' ';
    }

    cout << "\nFront insertion: O(n)\n";
}


// ============================================================
// 14. HASH TABLE OPERATIONS
// ============================================================

void demonstrateHashTable() {
    cout << "\n" << string(80, '=') << '\n';
    cout << "HASH TABLE OPERATIONS\n";
    cout << string(80, '=') << '\n';

    StudentDirectory directory;

    directory.insert({101, "Alice", 91.5});
    directory.insert({102, "Bob", 84.0});
    directory.insert({103, "Carol", 95.0});

    const auto result = directory.find(102);

    if (result.has_value()) {
        cout << "Found: " << result.value() << '\n';
    }

    cout << "Expected lookup: O(1)\n";
    cout << "Worst-case lookup: O(n)\n";

    directory.erase(102);

    cout << "Directory size after deletion: "
         << directory.size()
         << '\n';
}


// ============================================================
// 15. LINKED-LIST OPERATIONS
// ============================================================

void demonstrateLinkedList() {
    cout << "\n" << string(80, '=') << '\n';
    cout << "LINKED LIST OPERATIONS\n";
    cout << string(80, '=') << '\n';

    StudentLinkedList students;

    students.append({1, "Alice", 91});
    students.append({2, "Bob", 84});
    students.prepend({0, "Admin", 99});

    cout << "Student count: "
         << students.size()
         << '\n';

    cout << "\nList contents:\n";
    students.print();

    cout << "\nSearching for ID 2:\n";

    const auto result = students.findById(2);

    if (result.has_value()) {
        cout << result.value() << '\n';
    }

    cout << "Search complexity: O(n)\n";

    cout << "\nDeleting ID 2: "
         << boolalpha
         << students.deleteById(2)
         << '\n';

    cout << "Deletion by value remains O(n) because the predecessor "
            "must first be located.\n";
}


// ============================================================
// 16. SORTING CASE STUDY
// ============================================================

void demonstrateSorting() {
    cout << "\n" << string(80, '=') << '\n';
    cout << "SORTING CASE STUDY\n";
    cout << string(80, '=') << '\n';

    vector<Student> students{
        {104, "David", 78},
        {101, "Alice", 91},
        {105, "Eva", 88},
        {102, "Bob", 84},
        {103, "Carol", 95}
    };

    cout << "Before sorting:\n";

    for (const auto& student : students) {
        cout << student << '\n';
    }

    mergeSort(students);

    cout << "\nAfter merge sort:\n";

    for (const auto& student : students) {
        cout << student << '\n';
    }

    const int targetId = 103;

    const int position = binarySearchById(students, targetId);

    cout << "\nBinary search for ID "
         << targetId
         << " returned index "
         << position
         << ".\n";

    cout << "The sorting step costs O(n log n), while each subsequent "
            "binary search costs O(log n).\n";
}


// ============================================================
// 17. INPUT VALIDATION AND FAILURE CONDITIONS
// ============================================================

void demonstrateValidation() {
    cout << "\n" << string(80, '=') << '\n';
    cout << "VALIDATION AND FAILURE CONDITIONS\n";
    cout << string(80, '=') << '\n';

    vector<Student> invalidStudents{
        {0, "Invalid ID", 80},
        {200, "", 80},
        {201, "Invalid Score", 120}
    };

    for (const auto& student : invalidStudents) {
        try {
            validateStudent(student);
            cout << "Unexpectedly accepted: "
                 << student
                 << '\n';
        } catch (const invalid_argument& error) {
            cout << "Rejected record: "
                 << error.what()
                 << '\n';
        }
    }

    cout << "\nValidation prevents malformed records from entering "
            "the system and protects assumptions made by later algorithms.\n";
}


// ============================================================
// 18. PERFORMANCE COMPARISON
// ============================================================

void demonstratePerformance() {
    cout << "\n" << string(80, '=') << '\n';
    cout << "PERFORMANCE COMPARISON\n";
    cout << string(80, '=') << '\n';

    constexpr size_t dataSize = 5000;

    vector<Student> students = generateStudents(dataSize);

    vector<Student> nearlySorted = students;

    const int searchTarget = static_cast<int>(dataSize);

    const double linearMilliseconds = measureMilliseconds([&]() {
        volatile int result =
            linearSearchById(nearlySorted, searchTarget);

        (void)result;
    });

    vector<Student> sorted = students;

    const double sortMilliseconds = measureMilliseconds([&]() {
        mergeSort(sorted);
    });

    const double binaryMilliseconds = measureMilliseconds([&]() {
        volatile int result =
            binarySearchById(sorted, searchTarget);

        (void)result;
    });

    cout << fixed << setprecision(6);

    cout << "Input size: " << dataSize << '\n';
    cout << "Linear search time: "
         << linearMilliseconds
         << " ms\n";

    cout << "Merge sort time: "
         << sortMilliseconds
         << " ms\n";

    cout << "Binary search time: "
         << binaryMilliseconds
         << " ms\n";

    cout << "\nThese measurements are machine-dependent. "
            "The complexity classifications describe how work grows "
            "as input size increases.\n";
}


// ============================================================
// 19. ARRAY VS LINKED LIST
// ============================================================

void printArrayLinkedListComparison() {
    cout << "\n" << string(80, '=') << '\n';
    cout << "ARRAY/VECTOR VS LINKED LIST\n";
    cout << string(80, '=') << '\n';

    cout << left
         << setw(28) << "Operation"
         << setw(22) << "Vector"
         << "Linked list\n";

    cout << string(65, '-') << '\n';

    cout << setw(28) << "Index access"
         << setw(22) << "O(1)"
         << "O(n)\n";

    cout << setw(28) << "Search"
         << setw(22) << "O(n)"
         << "O(n)\n";

    cout << setw(28) << "Front insertion"
         << setw(22) << "O(n)"
         << "O(1)\n";

    cout << setw(28) << "Append"
         << setw(22) << "O(1) amortized"
         << "O(1) with tail\n";

    cout << setw(28) << "Memory locality"
         << setw(22) << "Usually strong"
         << "Usually weaker\n";

    cout << setw(28) << "Per-element overhead"
         << setw(22) << "Low"
         << "Higher\n";
}


// ============================================================
// 20. COMPLEXITY REFERENCE SHEET
// ============================================================

void printComplexityReferenceSheet() {
    cout << "\n" << string(80, '=') << '\n';
    cout << "COMPLEXITY REFERENCE SHEET\n";
    cout << string(80, '=') << '\n';

    cout << R"(
SEARCH
----------------------------------------------------------------------
Linear search:
    Best       O(1)
    Average    O(n)
    Worst      O(n)
    Space      O(1)

Binary search:
    Best       O(1)
    Average    O(log n)
    Worst      O(log n)
    Space      O(1) iterative
    Requirement: sorted data


SORTING
----------------------------------------------------------------------
Insertion sort:
    Best       O(n)
    Average    O(n²)
    Worst      O(n²)
    Space      O(1)

Merge sort:
    Best       O(n log n)
    Average    O(n log n)
    Worst      O(n log n)
    Space      O(n)


HASH TABLE
----------------------------------------------------------------------
Insert:
    Expected   O(1)
    Worst      O(n)

Lookup:
    Expected   O(1)
    Worst      O(n)

Delete:
    Expected   O(1)
    Worst      O(n)


VECTOR / DYNAMIC ARRAY
----------------------------------------------------------------------
Index access       O(1)
Index update       O(1)
Append             O(1) amortized
Front insertion    O(n)
Front deletion     O(n)
Search             O(n)


LINKED LIST
----------------------------------------------------------------------
Index access       O(n)
Search             O(n)
Prepend            O(1)
Append with tail   O(1)
Delete by value    O(n)
Space              O(n)


COMMON GROWTH ORDER
----------------------------------------------------------------------
O(1)
O(log n)
O(n)
O(n log n)
O(n²)
O(n³)
O(2ⁿ)
O(n!)
)";
}


// ============================================================
// 21. CORRECTNESS TESTS
// ============================================================

void runCorrectnessTests() {
    cout << "\n" << string(80, '=') << '\n';
    cout << "CORRECTNESS TESTS\n";
    cout << string(80, '=') << '\n';

    vector<Student> students{
        {7, "A", 70},
        {2, "B", 80},
        {9, "C", 90},
        {1, "D", 60},
        {5, "E", 75}
    };

    vector<Student> sortedStudents = students;

    mergeSort(sortedStudents);

    for (size_t index = 1; index < sortedStudents.size(); ++index) {
        if (sortedStudents[index - 1].id >
            sortedStudents[index].id) {
            throw runtime_error("Merge sort correctness test failed.");
        }
    }

    if (linearSearchById(students, 7) == -1) {
        throw runtime_error("Linear search test failed.");
    }

    if (binarySearchById(sortedStudents, 7) == -1) {
        throw runtime_error("Binary search test failed.");
    }

    StudentDirectory directory;

    directory.insert({100, "Test", 90});

    if (!directory.find(100).has_value()) {
        throw runtime_error("Hash-table lookup test failed.");
    }

    if (!directory.erase(100)) {
        throw runtime_error("Hash-table deletion test failed.");
    }

    StudentLinkedList list;

    list.append({1, "A", 90});
    list.append({2, "B", 80});
    list.prepend({0, "C", 70});

    if (!list.findById(2).has_value()) {
        throw runtime_error("Linked-list search test failed.");
    }

    if (!list.deleteById(2)) {
        throw runtime_error("Linked-list deletion test failed.");
    }

    cout << "All correctness tests passed.\n";
}


// ============================================================
// 22. MAIN
// ============================================================

int main() {
    try {
        cout << string(80, '=') << '\n';
        cout << "DAY 10 — BEST, AVERAGE AND WORST CASE\n";
        cout << "C++ INDUSTRY-STYLE CASE STUDY\n";
        cout << string(80, '=') << '\n';

        demonstrateSearchCases();
        demonstrateVectorOperations();
        demonstrateHashTable();
        demonstrateLinkedList();
        demonstrateSorting();
        demonstrateValidation();
        demonstratePerformance();
        printArrayLinkedListComparison();
        printComplexityReferenceSheet();
        runCorrectnessTests();

        cout << "\n" << string(80, '=') << '\n';
        cout << "END OF DAY 10\n";
        cout << string(80, '=') << '\n';

        return 0;
    } catch (const exception& error) {
        cerr << "Fatal error: "
             << error.what()
             << '\n';

        return 1;
    }
}
