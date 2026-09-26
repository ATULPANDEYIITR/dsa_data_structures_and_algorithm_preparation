/*
 * Day 27 — Linear Search
 * =======================
 *
 * Industry-style case study:
 * A small in-memory incident management system uses sequential records.
 *
 * The system demonstrates:
 * - Basic linear search
 * - Search conditions
 * - First occurrence
 * - Last occurrence
 * - All occurrences
 * - Object/record searching
 * - Predicate-based searches
 * - Validation
 * - Input processing
 * - Statistics
 * - Edge cases
 * - Complexity analysis
 * - Performance considerations
 *
 * Compile:
 *   g++ -std=c++17 -O2 day27_linear_search.cpp -o day27_linear_search
 *
 * Run:
 *   ./day27_linear_search
 */

#include <algorithm>
#include <chrono>
#include <cctype>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

using namespace std;


// ============================================================================
// 1. BASIC LINEAR SEARCH
// ============================================================================

template <typename T>
int linearSearch(const vector<T>& items, const T& target) {
    /*
     * Search sequentially from index 0.
     *
     * The first equality match is returned immediately.
     * If the scan reaches the end, -1 represents "not found".
     */
    for (size_t index = 0; index < items.size(); ++index) {
        if (items[index] == target) {
            return static_cast<int>(index);
        }
    }

    return -1;
}


// ============================================================================
// 2. SEARCH RESULT WITH STATISTICS
// ============================================================================

struct SearchResult {
    bool found;
    int index;
    size_t comparisons;
};

template <typename T>
SearchResult linearSearchWithStatistics(
    const vector<T>& items,
    const T& target
) {
    size_t comparisons = 0;

    for (size_t index = 0; index < items.size(); ++index) {
        ++comparisons;

        if (items[index] == target) {
            return {
                true,
                static_cast<int>(index),
                comparisons
            };
        }
    }

    return {false, -1, comparisons};
}


// ============================================================================
// 3. FIRST AND LAST OCCURRENCE
// ============================================================================

template <typename T>
int firstOccurrence(const vector<T>& items, const T& target) {
    for (size_t index = 0; index < items.size(); ++index) {
        if (items[index] == target) {
            return static_cast<int>(index);
        }
    }

    return -1;
}


template <typename T>
int lastOccurrence(const vector<T>& items, const T& target) {
    int lastIndex = -1;

    for (size_t index = 0; index < items.size(); ++index) {
        if (items[index] == target) {
            lastIndex = static_cast<int>(index);
        }
    }

    return lastIndex;
}


template <typename T>
int lastOccurrenceReverse(const vector<T>& items, const T& target) {
    /*
     * Reverse traversal is useful when the required result is the last match.
     * Once a match is found from the right, no earlier element can replace it.
     */
    for (size_t index = items.size(); index > 0; --index) {
        const size_t actualIndex = index - 1;

        if (items[actualIndex] == target) {
            return static_cast<int>(actualIndex);
        }
    }

    return -1;
}


// ============================================================================
// 4. ALL OCCURRENCES
// ============================================================================

template <typename T>
vector<size_t> allOccurrences(
    const vector<T>& items,
    const T& target
) {
    vector<size_t> positions;

    for (size_t index = 0; index < items.size(); ++index) {
        if (items[index] == target) {
            positions.push_back(index);
        }
    }

    return positions;
}


// ============================================================================
// 5. PREDICATE-BASED SEARCH
// ============================================================================

template <typename T, typename Predicate>
optional<size_t> firstIndexWhere(
    const vector<T>& items,
    Predicate condition
) {
    for (size_t index = 0; index < items.size(); ++index) {
        if (condition(items[index])) {
            return index;
        }
    }

    return nullopt;
}


template <typename T, typename Predicate>
optional<size_t> lastIndexWhere(
    const vector<T>& items,
    Predicate condition
) {
    optional<size_t> result;

    for (size_t index = 0; index < items.size(); ++index) {
        if (condition(items[index])) {
            result = index;
        }
    }

    return result;
}


// ============================================================================
// 6. REALISTIC DOMAIN MODEL
// ============================================================================

enum class Severity {
    Low,
    Medium,
    High,
    Critical
};


enum class Status {
    Open,
    Investigating,
    Resolved
};


string severityToString(Severity severity) {
    switch (severity) {
        case Severity::Low:
            return "LOW";
        case Severity::Medium:
            return "MEDIUM";
        case Severity::High:
            return "HIGH";
        case Severity::Critical:
            return "CRITICAL";
    }

    return "UNKNOWN";
}


string statusToString(Status status) {
    switch (status) {
        case Status::Open:
            return "OPEN";
        case Status::Investigating:
            return "INVESTIGATING";
        case Status::Resolved:
            return "RESOLVED";
    }

    return "UNKNOWN";
}


struct Incident {
    int incidentId;
    string title;
    string owner;
    Severity severity;
    Status status;
    int priority;
};


ostream& operator<<(ostream& output, const Incident& incident) {
    output
        << "Incident{"
        << "id=" << incident.incidentId
        << ", title=\"" << incident.title << "\""
        << ", owner=\"" << incident.owner << "\""
        << ", severity=" << severityToString(incident.severity)
        << ", status=" << statusToString(incident.status)
        << ", priority=" << incident.priority
        << "}";

    return output;
}


// ============================================================================
// 7. INCIDENT SEARCH OPERATIONS
// ============================================================================

class IncidentRegistry {
private:
    vector<Incident> incidents;

public:
    explicit IncidentRegistry(vector<Incident> initialIncidents)
        : incidents(std::move(initialIncidents)) {}

    const vector<Incident>& getIncidents() const {
        return incidents;
    }

    optional<Incident> findById(int incidentId) const {
        /*
         * This is a classic linear lookup.
         *
         * It is appropriate for a small registry or for demonstrating the
         * algorithm. A production system with very frequent ID lookups could
         * maintain an unordered_map<int, Incident> index.
         */
        for (const Incident& incident : incidents) {
            if (incident.incidentId == incidentId) {
                return incident;
            }
        }

        return nullopt;
    }

    optional<Incident> findFirstCritical() const {
        for (const Incident& incident : incidents) {
            if (incident.severity == Severity::Critical) {
                return incident;
            }
        }

        return nullopt;
    }

    optional<Incident> findFirstOpenHighPriority(int minimumPriority) const {
        for (const Incident& incident : incidents) {
            if (
                incident.status == Status::Open &&
                incident.priority >= minimumPriority
            ) {
                return incident;
            }
        }

        return nullopt;
    }

    vector<Incident> findAllByOwner(string_view owner) const {
        vector<Incident> results;

        for (const Incident& incident : incidents) {
            if (incident.owner == owner) {
                results.push_back(incident);
            }
        }

        return results;
    }

    vector<Incident> findAllBySeverity(Severity severity) const {
        vector<Incident> results;

        for (const Incident& incident : incidents) {
            if (incident.severity == severity) {
                results.push_back(incident);
            }
        }

        return results;
    }

    optional<Incident> findLastResolved() const {
        /*
         * A reverse scan gives the last matching record without having to
         * examine records before the last match.
         */
        for (size_t index = incidents.size(); index > 0; --index) {
            const Incident& incident = incidents[index - 1];

            if (incident.status == Status::Resolved) {
                return incident;
            }
        }

        return nullopt;
    }
};


// ============================================================================
// 8. INPUT VALIDATION
// ============================================================================

int readPositiveInteger(string_view prompt) {
    while (true) {
        cout << prompt;

        int value{};

        if (cin >> value && value > 0) {
            return value;
        }

        cout << "Please enter a positive integer.\n";

        cin.clear();
        cin.ignore(
            numeric_limits<streamsize>::max(),
            '\n'
        );
    }
}


void demonstrateInputValidation() {
    cout << "\n" << string(72, '=') << '\n';
    cout << "INPUT VALIDATION\n";
    cout << string(72, '=') << '\n';

    /*
     * Interactive input is intentionally kept separate from the main
     * algorithm so that search logic remains deterministic and testable.
     */
    cout << "Validation is demonstrated through a safe helper.\n";
}


// ============================================================================
// 9. SAMPLE DATA
// ============================================================================

vector<Incident> createSampleIncidents() {
    return {
        {
            1001,
            "Authentication anomaly",
            "Asha",
            Severity::High,
            Status::Open,
            8
        },
        {
            1002,
            "Database connection failure",
            "Rahul",
            Severity::Critical,
            Status::Investigating,
            10
        },
        {
            1003,
            "Expired certificate",
            "Asha",
            Severity::Medium,
            Status::Resolved,
            5
        },
        {
            1004,
            "Suspicious network activity",
            "Meera",
            Severity::Critical,
            Status::Open,
            9
        },
        {
            1005,
            "Storage threshold exceeded",
            "Rahul",
            Severity::High,
            Status::Resolved,
            7
        },
        {
            1006,
            "Service restart",
            "Asha",
            Severity::Low,
            Status::Resolved,
            2
        }
    };
}


// ============================================================================
// 10. DISPLAY HELPERS
// ============================================================================

void printIncidents(const vector<Incident>& incidents) {
    for (const Incident& incident : incidents) {
        cout << "  " << incident << '\n';
    }
}


void printPositions(const vector<size_t>& positions) {
    cout << "[";

    for (size_t index = 0; index < positions.size(); ++index) {
        cout << positions[index];

        if (index + 1 < positions.size()) {
            cout << ", ";
        }
    }

    cout << "]\n";
}


// ============================================================================
// 11. BASIC CASE STUDY
// ============================================================================

void demonstrateBasicLinearSearch() {
    cout << "\n" << string(72, '=') << '\n';
    cout << "1. BASIC LINEAR SEARCH\n";
    cout << string(72, '=') << '\n';

    const vector<int> values{17, 4, 9, 23, 11, 8};

    cout << "Data: ";

    for (int value : values) {
        cout << value << ' ';
    }

    cout << '\n';

    cout << "Index of 23: "
         << linearSearch(values, 23)
         << '\n';

    cout << "Index of 99: "
         << linearSearch(values, 99)
         << '\n';
}


// ============================================================================
// 12. DUPLICATES
// ============================================================================

void demonstrateDuplicates() {
    cout << "\n" << string(72, '=') << '\n';
    cout << "2. DUPLICATE VALUES\n";
    cout << string(72, '=') << '\n';

    const vector<int> values{5, 8, 5, 2, 5, 9, 5};

    cout << "First occurrence of 5: "
         << firstOccurrence(values, 5)
         << '\n';

    cout << "Last occurrence of 5: "
         << lastOccurrence(values, 5)
         << '\n';

    cout << "Last occurrence using reverse scan: "
         << lastOccurrenceReverse(values, 5)
         << '\n';

    cout << "All occurrences of 5: ";
    printPositions(allOccurrences(values, 5));
}


// ============================================================================
// 13. SEARCH CONDITIONS
// ============================================================================

void demonstrateSearchConditions() {
    cout << "\n" << string(72, '=') << '\n';
    cout << "3. SEARCH CONDITIONS\n";
    cout << string(72, '=') << '\n';

    const vector<int> values{4, 7, 12, 15, 22, 31};

    const auto firstEven = firstIndexWhere(
        values,
        [](int value) {
            return value % 2 == 0;
        }
    );

    const auto lastDivisibleByThree = lastIndexWhere(
        values,
        [](int value) {
            return value % 3 == 0;
        }
    );

    cout << "First even index: ";

    if (firstEven.has_value()) {
        cout << *firstEven;
    } else {
        cout << "not found";
    }

    cout << '\n';

    cout << "Last index divisible by 3: ";

    if (lastDivisibleByThree.has_value()) {
        cout << *lastDivisibleByThree;
    } else {
        cout << "not found";
    }

    cout << '\n';
}


// ============================================================================
// 14. INCIDENT CASE STUDY
// ============================================================================

void demonstrateIncidentRegistry(const IncidentRegistry& registry) {
    cout << "\n" << string(72, '=') << '\n';
    cout << "4. INCIDENT REGISTRY CASE STUDY\n";
    cout << string(72, '=') << '\n';

    cout << "Incident records:\n";
    printIncidents(registry.getIncidents());

    cout << "\nSearch by incident ID 1004:\n";

    const auto incident = registry.findById(1004);

    if (incident.has_value()) {
        cout << *incident << '\n';
    } else {
        cout << "Incident not found.\n";
    }

    cout << "\nSearch by incident ID 9999:\n";

    const auto missing = registry.findById(9999);

    if (missing.has_value()) {
        cout << *missing << '\n';
    } else {
        cout << "Incident not found.\n";
    }

    cout << "\nFirst critical incident:\n";

    const auto critical = registry.findFirstCritical();

    if (critical.has_value()) {
        cout << *critical << '\n';
    }

    cout << "\nFirst open incident with priority >= 9:\n";

    const auto urgent = registry.findFirstOpenHighPriority(9);

    if (urgent.has_value()) {
        cout << *urgent << '\n';
    }

    cout << "\nAll incidents owned by Asha:\n";
    printIncidents(registry.findAllByOwner("Asha"));

    cout << "\nAll critical incidents:\n";
    printIncidents(
        registry.findAllBySeverity(Severity::Critical)
    );

    cout << "\nLast resolved incident:\n";

    const auto lastResolved = registry.findLastResolved();

    if (lastResolved.has_value()) {
        cout << *lastResolved << '\n';
    }
}


// ============================================================================
// 15. COMPLEXITY DEMONSTRATION
// ============================================================================

void demonstrateComparisonCounts() {
    cout << "\n" << string(72, '=') << '\n';
    cout << "5. COMPARISON COUNTS\n";
    cout << string(72, '=') << '\n';

    const vector<int> values{10, 20, 30, 40, 50};

    for (int target : {10, 30, 50, 99}) {
        const SearchResult result =
            linearSearchWithStatistics(values, target);

        cout
            << "target=" << setw(2) << target
            << " found=" << boolalpha << result.found
            << " index=" << setw(2) << result.index
            << " comparisons=" << result.comparisons
            << '\n';
    }

    cout << noboolalpha;
}


// ============================================================================
// 16. SORTED LINEAR SEARCH
// ============================================================================

int sortedLinearSearch(
    const vector<int>& values,
    int target
) {
    for (size_t index = 0; index < values.size(); ++index) {
        if (values[index] == target) {
            return static_cast<int>(index);
        }

        if (values[index] > target) {
            return -1;
        }
    }

    return -1;
}


void demonstrateSortedLinearSearch() {
    cout << "\n" << string(72, '=') << '\n';
    cout << "6. SORTED-DATA EARLY EXIT\n";
    cout << string(72, '=') << '\n';

    const vector<int> values{4, 8, 13, 21, 29, 35};

    cout << "Search 21: "
         << sortedLinearSearch(values, 21)
         << '\n';

    cout << "Search 20: "
         << sortedLinearSearch(values, 20)
         << '\n';

    cout << "Search 40: "
         << sortedLinearSearch(values, 40)
         << '\n';

    cout
        << "Sorted order enables early termination, but worst-case time "
        << "remains O(n).\n";
}


// ============================================================================
// 17. BINARY SEARCH FOR COMPARISON
// ============================================================================

int binarySearch(
    const vector<int>& values,
    int target
) {
    int left = 0;
    int right = static_cast<int>(values.size()) - 1;

    while (left <= right) {
        const int middle = left + (right - left) / 2;

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


void demonstrateBinarySearchComparison() {
    cout << "\n" << string(72, '=') << '\n';
    cout << "7. BINARY SEARCH COMPARISON\n";
    cout << string(72, '=') << '\n';

    const vector<int> values{
        3, 8, 12, 17, 24, 31, 45, 51
    };

    cout << "Linear search result: "
         << linearSearch(values, 24)
         << '\n';

    cout << "Binary search result: "
         << binarySearch(values, 24)
         << '\n';

    cout
        << "Linear search works without sorted input; "
        << "binary search requires suitable sorted input.\n";
}


// ============================================================================
// 18. EDGE CASES
// ============================================================================

void demonstrateEdgeCases() {
    cout << "\n" << string(72, '=') << '\n';
    cout << "8. EDGE CASES\n";
    cout << string(72, '=') << '\n';

    const vector<int> empty{};
    const vector<int> singleton{10};
    const vector<int> duplicates{7, 7, 7, 7};

    cout << "Empty search: "
         << linearSearch(empty, 10)
         << '\n';

    cout << "Singleton match: "
         << linearSearch(singleton, 10)
         << '\n';

    cout << "Singleton miss: "
         << linearSearch(singleton, 20)
         << '\n';

    cout << "All duplicate positions: ";
    printPositions(allOccurrences(duplicates, 7));

    cout << "Missing duplicate target: ";
    printPositions(allOccurrences(duplicates, 8));
}


// ============================================================================
// 19. PERFORMANCE BENCHMARK
// ============================================================================

void demonstratePerformance() {
    cout << "\n" << string(72, '=') << '\n';
    cout << "9. PERFORMANCE BENCHMARK\n";
    cout << string(72, '=') << '\n';

    cout
        << left
        << setw(12) << "Size"
        << setw(16) << "Comparisons"
        << setw(20) << "Time (microseconds)"
        << '\n';

    cout << string(48, '-') << '\n';

    /*
     * The target is placed at the last index to produce a worst-case
     * successful search.
     *
     * Timings are machine-dependent. The number of comparisons is the more
     * important algorithmic observation.
     */
    for (size_t size : {100u, 10'000u, 100'000u}) {
        vector<int> values(size);

        for (size_t index = 0; index < size; ++index) {
            values[index] = static_cast<int>(index);
        }

        const int target = values.back();

        const auto start =
            chrono::steady_clock::now();

        const SearchResult result =
            linearSearchWithStatistics(values, target);

        const auto finish =
            chrono::steady_clock::now();

        const auto elapsed =
            chrono::duration_cast<chrono::microseconds>(
                finish - start
            ).count();

        cout
            << left
            << setw(12) << size
            << setw(16) << result.comparisons
            << setw(20) << elapsed
            << '\n';
    }

    cout
        << "\nThe timing depends on hardware, compiler, optimization, "
        << "memory behavior, and runtime conditions.\n";
}


// ============================================================================
// 20. SECURITY AND PRODUCTION CONSIDERATIONS
// ============================================================================

void demonstrateProductionConsiderations() {
    cout << "\n" << string(72, '=') << '\n';
    cout << "10. PRODUCTION CONSIDERATIONS\n";
    cout << string(72, '=') << '\n';

    cout << R"(
Linear search is an algorithm, not an authorization mechanism.

For production systems:
- Validate external input before converting it into search parameters.
- Enforce authorization before returning sensitive records.
- Avoid logging confidential search terms unnecessarily.
- Consider worst-case O(n) work when users can trigger many searches.
- Use database indexes for persistent high-volume lookup operations.
- Use an unordered_map or another index when repeated exact-key lookups
  justify the additional memory and maintenance cost.
- Preserve a clear search contract: first match, last match, all matches,
  existence, or another explicitly defined result.
- Avoid modifying a collection while another operation assumes stable indices.
- Measure real workloads before replacing a simple algorithm with a more
  complex data structure.
)" << '\n';
}


// ============================================================================
// 21. UNIT TESTS
// ============================================================================

void require(bool condition, const string& message) {
    if (!condition) {
        throw runtime_error("Test failed: " + message);
    }
}


void runTests() {
    require(
        linearSearch(vector<int>{}, 10) == -1,
        "empty search"
    );

    require(
        linearSearch(vector<int>{10}, 10) == 0,
        "singleton match"
    );

    require(
        linearSearch(vector<int>{10}, 20) == -1,
        "singleton miss"
    );

    require(
        firstOccurrence(
            vector<int>{1, 2, 1, 3, 1},
            1
        ) == 0,
        "first occurrence"
    );

    require(
        lastOccurrence(
            vector<int>{1, 2, 1, 3, 1},
            1
        ) == 4,
        "last occurrence"
    );

    require(
        lastOccurrenceReverse(
            vector<int>{1, 2, 1, 3, 1},
            1
        ) == 4,
        "reverse last occurrence"
    );

    const auto positions =
        allOccurrences(
            vector<int>{1, 2, 1, 3, 1},
            1
        );

    require(
        positions == vector<size_t>{0, 2, 4},
        "all occurrences"
    );

    const vector<int> values{1, 3, 4, 7};

    const auto firstEven =
        firstIndexWhere(
            values,
            [](int value) {
                return value % 2 == 0;
            }
        );

    require(
        firstEven.has_value() && *firstEven == 2,
        "predicate search"
    );

    const auto noEven =
        firstIndexWhere(
            vector<int>{1, 3, 5},
            [](int value) {
                return value % 2 == 0;
            }
        );

    require(
        !noEven.has_value(),
        "predicate missing"
    );

    const SearchResult statistics =
        linearSearchWithStatistics(
            vector<int>{10, 20, 30},
            30
        );

    require(
        statistics.found &&
        statistics.index == 2 &&
        statistics.comparisons == 3,
        "statistics"
    );

    IncidentRegistry registry(createSampleIncidents());

    const auto incident = registry.findById(1004);

    require(
        incident.has_value() &&
        incident->incidentId == 1004,
        "incident lookup"
    );

    const auto missing = registry.findById(9999);

    require(
        !missing.has_value(),
        "missing incident"
    );

    const auto critical = registry.findFirstCritical();

    require(
        critical.has_value() &&
        critical->severity == Severity::Critical,
        "critical search"
    );

    const auto ownerResults =
        registry.findAllByOwner("Asha");

    require(
        ownerResults.size() == 3,
        "owner search"
    );

    cout << "\nAll C++ tests passed.\n";
}


// ============================================================================
// 22. MAIN
// ============================================================================

int main() {
    try {
        cout << string(72, '=') << '\n';
        cout << "DAY 27 — LINEAR SEARCH\n";
        cout << string(72, '=') << '\n';

        cout
            << "Sequential search, search conditions, first occurrence, "
            << "last occurrence, and complexity analysis.\n";

        demonstrateBasicLinearSearch();
        demonstrateDuplicates();
        demonstrateSearchConditions();

        const IncidentRegistry registry(
            createSampleIncidents()
        );

        demonstrateIncidentRegistry(registry);
        demonstrateComparisonCounts();
        demonstrateSortedLinearSearch();
        demonstrateBinarySearchComparison();
        demonstrateEdgeCases();
        demonstratePerformance();
        demonstrateProductionConsiderations();
        demonstrateInputValidation();

        runTests();

        cout << "\nProgram completed successfully.\n";
        return 0;
    }
    catch (const exception& error) {
        cerr
            << "Program error: "
            << error.what()
            << '\n';

        return 1;
    }
}
