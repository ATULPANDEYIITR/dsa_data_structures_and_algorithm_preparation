/*
 * Binary Search on Answer
 * ========================
 *
 * Modern C++17 case study.
 *
 * Scenario:
 *   A logistics and operations platform must determine capacities, processing
 *   speeds, workload limits, and facility spacing without trying every possible
 *   numeric answer.
 *
 * The input arrays themselves do not need to be sorted for most of these
 * problems. Instead, a numeric answer is searched.
 *
 * General pattern:
 *
 *   minimum answer:
 *       false false false true true true
 *
 *   maximum answer:
 *       true true true false false false
 *
 * The decisive property is monotonic feasibility.
 *
 * C++ considerations demonstrated:
 * - strongly typed functions
 * - lambdas
 * - classes
 * - vectors
 * - exceptions
 * - long long arithmetic
 * - overflow-safe midpoint calculation
 * - greedy feasibility checks
 * - early termination
 * - complexity-aware bounds
 * - brute-force validation
 * - modular architecture
 */

#include <algorithm>
#include <cassert>
#include <exception>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

using std::cout;
using std::endl;
using std::function;
using std::invalid_argument;
using std::runtime_error;
using std::size_t;
using std::string;
using std::tuple;
using std::vector;

using int64 = long long;

// -----------------------------------------------------------------------------
// 1. GENERIC ANSWER-SPACE SEARCH
// -----------------------------------------------------------------------------

class AnswerSpaceSearch {
public:
    /*
     * Find the smallest integer x in [low, high] for which feasible(x) is true.
     *
     * The midpoint is calculated as:
     *
     *     low + (high - low) / 2
     *
     * rather than:
     *
     *     (low + high) / 2
     *
     * because low + high can overflow in fixed-width integer arithmetic.
     */
    static int64 firstTrue(
        int64 low,
        int64 high,
        const function<bool(int64)>& feasible
    ) {
        if (low > high) {
            throw invalid_argument("low must not exceed high");
        }

        while (low < high) {
            const int64 mid = low + (high - low) / 2;

            if (feasible(mid)) {
                high = mid;
            } else {
                low = mid + 1;
            }
        }

        return low;
    }

    /*
     * Find the largest integer x in [low, high] for which feasible(x) is true.
     *
     * The upper midpoint is important:
     *
     *     low + (high - low + 1) / 2
     *
     * Without the +1, low and high can remain unchanged when they differ by 1.
     */
    static int64 lastTrue(
        int64 low,
        int64 high,
        const function<bool(int64)>& feasible
    ) {
        if (low > high) {
            throw invalid_argument("low must not exceed high");
        }

        while (low < high) {
            const int64 mid = low + (high - low + 1) / 2;

            if (feasible(mid)) {
                low = mid;
            } else {
                high = mid - 1;
            }
        }

        return low;
    }
};

// -----------------------------------------------------------------------------
// 2. VALIDATION HELPERS
// -----------------------------------------------------------------------------

void requirePositiveVector(
    const vector<int64>& values,
    const string& name
) {
    if (values.empty()) {
        throw invalid_argument(name + " must not be empty");
    }

    for (const int64 value : values) {
        if (value <= 0) {
            throw invalid_argument(
                name + " must contain only positive values"
            );
        }
    }
}

void requireNonNegativeVector(
    const vector<int64>& values,
    const string& name
) {
    if (values.empty()) {
        throw invalid_argument(name + " must not be empty");
    }

    for (const int64 value : values) {
        if (value < 0) {
            throw invalid_argument(
                name + " must contain non-negative values"
            );
        }
    }
}

// -----------------------------------------------------------------------------
// 3. MINIMUM PROCESSING SPEED
// -----------------------------------------------------------------------------

class ProcessingSystem {
public:
    /*
     * Find the minimum integer speed that processes every workload within
     * the supplied number of hours.
     *
     * For speed s:
     *
     *     required_hours = sum(ceil(workload / s))
     *
     * If speed s is feasible, every larger speed is also feasible.
     */
    static int64 minimumSpeed(
        const vector<int64>& workloads,
        int64 availableHours
    ) {
        requirePositiveVector(workloads, "workloads");

        if (availableHours <= 0) {
            throw invalid_argument("availableHours must be positive");
        }

        const int64 low = 1;
        const int64 high = *std::max_element(
            workloads.begin(),
            workloads.end()
        );

        const auto feasible = [&](int64 speed) {
            int64 requiredHours = 0;

            for (const int64 workload : workloads) {
                // Integer ceiling:
                // ceil(a / b) = (a + b - 1) / b
                //
                // This is safe here because speed <= max workload and the
                // input is constrained to positive int64 values.
                const int64 hours =
                    workload / speed +
                    (workload % speed != 0 ? 1 : 0);

                if (requiredHours >
                    availableHours - hours) {
                    return false;
                }

                requiredHours += hours;
            }

            return requiredHours <= availableHours;
        };

        return AnswerSpaceSearch::firstTrue(
            low,
            high,
            feasible
        );
    }
};

// -----------------------------------------------------------------------------
// 4. SHIPPING CAPACITY
// -----------------------------------------------------------------------------

class ShippingPlanner {
public:
    /*
     * Packages must remain in their original order.
     *
     * For a candidate capacity:
     * - keep adding packages to the current day;
     * - when the next package does not fit, start another day.
     *
     * For non-negative package weights, this greedy feasibility test gives the
     * minimum number of days required for that capacity.
     */
    static bool canShipWithinDays(
        const vector<int64>& weights,
        int64 capacity,
        int64 days
    ) {
        int64 requiredDays = 1;
        int64 currentLoad = 0;

        for (const int64 weight : weights) {
            if (weight > capacity) {
                return false;
            }

            if (currentLoad <= capacity - weight) {
                currentLoad += weight;
            } else {
                ++requiredDays;
                currentLoad = weight;

                if (requiredDays > days) {
                    return false;
                }
            }
        }

        return requiredDays <= days;
    }

    static int64 minimumCapacity(
        const vector<int64>& weights,
        int64 days
    ) {
        requirePositiveVector(weights, "weights");

        if (days <= 0) {
            throw invalid_argument("days must be positive");
        }

        const int64 low = *std::max_element(
            weights.begin(),
            weights.end()
        );

        const int64 high = std::accumulate(
            weights.begin(),
            weights.end(),
            int64{0}
        );

        const auto feasible = [&](int64 capacity) {
            return canShipWithinDays(
                weights,
                capacity,
                days
            );
        };

        return AnswerSpaceSearch::firstTrue(
            low,
            high,
            feasible
        );
    }
};

// -----------------------------------------------------------------------------
// 5. CONTIGUOUS WORK ALLOCATION
// -----------------------------------------------------------------------------

class AllocationPlanner {
public:
    /*
     * Assign contiguous work units to at most `workers` workers while
     * minimizing the largest worker workload.
     *
     * Example:
     *
     *     [7, 2, 5, 10, 8], workers=2
     *
     * One optimal partition is:
     *
     *     [7, 2, 5] | [10, 8]
     *
     * The maximum workload is 18.
     *
     * For candidate limit L, greedily create a new worker only when the next
     * job would exceed L.
     */
    static bool feasible(
        const vector<int64>& work,
        int64 workers,
        int64 limit
    ) {
        int64 workerCount = 1;
        int64 currentLoad = 0;

        for (const int64 item : work) {
            if (item > limit) {
                return false;
            }

            if (currentLoad <= limit - item) {
                currentLoad += item;
            } else {
                ++workerCount;
                currentLoad = item;

                if (workerCount > workers) {
                    return false;
                }
            }
        }

        return true;
    }

    static int64 minimumMaximumLoad(
        const vector<int64>& work,
        int64 workers
    ) {
        requireNonNegativeVector(work, "work");

        if (workers <= 0) {
            throw invalid_argument("workers must be positive");
        }

        workers = std::min<int64>(
            workers,
            static_cast<int64>(work.size())
        );

        const int64 low = *std::max_element(
            work.begin(),
            work.end()
        );

        const int64 high = std::accumulate(
            work.begin(),
            work.end(),
            int64{0}
        );

        return AnswerSpaceSearch::firstTrue(
            low,
            high,
            [&](int64 limit) {
                return feasible(
                    work,
                    workers,
                    limit
                );
            }
        );
    }
};

// -----------------------------------------------------------------------------
// 6. MAXIMUM MINIMUM DISTANCE
// -----------------------------------------------------------------------------

class FacilityPlacement {
public:
    /*
     * Place a requested number of facilities at distinct positions.
     *
     * Goal:
     *     maximize the minimum distance between selected facilities.
     *
     * For a candidate distance d:
     *     select the first position;
     *     then always select the earliest position at least d away.
     *
     * This greedy choice leaves as much room as possible for later facilities.
     */
    static bool feasible(
        const vector<int64>& sortedPositions,
        int64 facilities,
        int64 distance
    ) {
        int64 selected = 1;
        int64 last = sortedPositions.front();

        for (size_t i = 1; i < sortedPositions.size(); ++i) {
            if (sortedPositions[i] - last >= distance) {
                ++selected;
                last = sortedPositions[i];

                if (selected >= facilities) {
                    return true;
                }
            }
        }

        return selected >= facilities;
    }

    static int64 maximumMinimumDistance(
        vector<int64> positions,
        int64 facilities
    ) {
        if (positions.empty()) {
            throw invalid_argument(
                "positions must not be empty"
            );
        }

        if (facilities <= 0 ||
            facilities > static_cast<int64>(positions.size())) {
            throw invalid_argument(
                "invalid number of facilities"
            );
        }

        std::sort(
            positions.begin(),
            positions.end()
        );

        positions.erase(
            std::unique(
                positions.begin(),
                positions.end()
            ),
            positions.end()
        );

        if (facilities >
            static_cast<int64>(positions.size())) {
            throw invalid_argument(
                "facilities require distinct positions"
            );
        }

        const int64 low = 0;
        const int64 high =
            positions.back() - positions.front();

        return AnswerSpaceSearch::lastTrue(
            low,
            high,
            [&](int64 distance) {
                return feasible(
                    positions,
                    facilities,
                    distance
                );
            }
        );
    }
};

// -----------------------------------------------------------------------------
// 7. BRUTE-FORCE REFERENCE FOR TESTING
// -----------------------------------------------------------------------------

class ReferenceAlgorithms {
public:
    /*
     * This intentionally slower implementation tries every possible capacity.
     *
     * It is useful for testing because an optimized algorithm should be
     * compared against a simple reference implementation on small inputs.
     */
    static int64 bruteForceShippingCapacity(
        const vector<int64>& weights,
        int64 days
    ) {
        requirePositiveVector(weights, "weights");

        const int64 low = *std::max_element(
            weights.begin(),
            weights.end()
        );

        const int64 high = std::accumulate(
            weights.begin(),
            weights.end(),
            int64{0}
        );

        for (int64 capacity = low;
             capacity <= high;
             ++capacity) {

            if (ShippingPlanner::canShipWithinDays(
                    weights,
                    capacity,
                    days)) {
                return capacity;
            }
        }

        throw runtime_error("No feasible capacity found");
    }
};

// -----------------------------------------------------------------------------
// 8. TRACE SUPPORT
// -----------------------------------------------------------------------------

struct SearchStep {
    int64 low;
    int64 mid;
    int64 high;
    bool feasible;
};

class TraceableSearch {
public:
    static tuple<int64, vector<SearchStep>> firstTrueWithTrace(
        int64 low,
        int64 high,
        const function<bool(int64)>& feasible
    ) {
        vector<SearchStep> trace;

        while (low < high) {
            const int64 oldLow = low;
            const int64 oldHigh = high;
            const int64 mid = low + (high - low) / 2;
            const bool result = feasible(mid);

            trace.push_back({
                oldLow,
                mid,
                oldHigh,
                result
            });

            if (result) {
                high = mid;
            } else {
                low = mid + 1;
            }
        }

        return {low, trace};
    }
};

// -----------------------------------------------------------------------------
// 9. SYSTEM-LEVEL CASE STUDY
// -----------------------------------------------------------------------------

struct Project {
    string name;
    int64 effort;
};

class OperationsSystem {
private:
    vector<Project> projects;

public:
    explicit OperationsSystem(vector<Project> input)
        : projects(std::move(input)) {
        if (projects.empty()) {
            throw invalid_argument(
                "project list must not be empty"
            );
        }

        for (const auto& project : projects) {
            if (project.name.empty() ||
                project.effort < 0) {
                throw invalid_argument(
                    "invalid project"
                );
            }
        }
    }

    /*
     * The project order is preserved. This models a situation in which a
     * pipeline cannot arbitrarily reorder work.
     */
    int64 calculateEngineerCapacity(
        int64 engineers
    ) const {
        vector<int64> effort;

        for (const auto& project : projects) {
            effort.push_back(project.effort);
        }

        return AllocationPlanner::minimumMaximumLoad(
            effort,
            engineers
        );
    }

    void printProjectPlan() const {
        cout << "Projects:\n";

        for (const auto& project : projects) {
            cout << "  "
                 << std::setw(12)
                 << project.name
                 << " effort="
                 << project.effort
                 << '\n';
        }
    }
};

// -----------------------------------------------------------------------------
// 10. COMPLEXITY REPORT
// -----------------------------------------------------------------------------

void printComplexityReport() {
    cout << "\nComplexity model:\n";
    cout << "  Binary search: O(log R) feasibility calls\n";
    cout << "  Shipping feasibility: O(n)\n";
    cout << "  Processing-speed feasibility: O(n)\n";
    cout << "  Allocation feasibility: O(n)\n";
    cout << "  Distance feasibility: O(n)\n";
    cout << "  Complete answer-space algorithms: O(n log R)\n";
    cout << "  Additional storage is generally O(1), excluding copied/sorted input.\n";
}

// -----------------------------------------------------------------------------
// 11. TESTS
// -----------------------------------------------------------------------------

void runTests() {
    assert(
        ProcessingSystem::minimumSpeed(
            {3, 6, 7, 11},
            8
        ) == 4
    );

    assert(
        ProcessingSystem::minimumSpeed(
            {30, 11, 23, 4, 20},
            5
        ) == 30
    );

    assert(
        ShippingPlanner::minimumCapacity(
            {1, 2, 3, 1, 1},
            4
        ) == 3
    );

    assert(
        ShippingPlanner::minimumCapacity(
            {3, 2, 2, 4, 1, 4},
            3
        ) == 6
    );

    assert(
        AllocationPlanner::minimumMaximumLoad(
            {7, 2, 5, 10, 8},
            2
        ) == 18
    );

    assert(
        AllocationPlanner::minimumMaximumLoad(
            {1, 2, 3, 4, 5},
            2
        ) == 9
    );

    assert(
        FacilityPlacement::maximumMinimumDistance(
            {1, 2, 4, 8, 9},
            3
        ) == 3
    );

    const vector<vector<int64>> testWeights = {
        {1, 2, 3},
        {2, 2, 2, 2},
        {5, 1, 1, 1},
        {7, 3, 4, 2}
    };

    const vector<int64> testDays = {
        2,
        2,
        3,
        2
    };

    for (size_t i = 0; i < testWeights.size(); ++i) {
        const int64 optimized =
            ShippingPlanner::minimumCapacity(
                testWeights[i],
                testDays[i]
            );

        const int64 reference =
            ReferenceAlgorithms::bruteForceShippingCapacity(
                testWeights[i],
                testDays[i]
            );

        assert(optimized == reference);
    }

    cout << "All C++ tests passed.\n";
}

// -----------------------------------------------------------------------------
// 12. ERROR HANDLING TESTS
// -----------------------------------------------------------------------------

void demonstrateValidation() {
    cout << "\nValidation examples:\n";

    try {
        ShippingPlanner::minimumCapacity({}, 3);
    } catch (const std::exception& error) {
        cout << "Expected error: "
             << error.what()
             << '\n';
    }

    try {
        ProcessingSystem::minimumSpeed(
            {10, 20},
            0
        );
    } catch (const std::exception& error) {
        cout << "Expected error: "
             << error.what()
             << '\n';
    }

    try {
        FacilityPlacement::maximumMinimumDistance(
            {1, 2},
            3
        );
    } catch (const std::exception& error) {
        cout << "Expected error: "
             << error.what()
             << '\n';
    }
}

// -----------------------------------------------------------------------------
// 13. MAIN
// -----------------------------------------------------------------------------

int main() {
    try {
        cout << "BINARY SEARCH ON ANSWER\n";
        cout << "======================\n";

        // ---------------------------------------------------------------------
        // Processing speed
        // ---------------------------------------------------------------------

        const vector<int64> workloads = {
            3, 6, 7, 11
        };

        const int64 hours = 8;

        const int64 speed =
            ProcessingSystem::minimumSpeed(
                workloads,
                hours
            );

        cout << "\nMinimum processing speed: "
             << speed
             << '\n';

        // ---------------------------------------------------------------------
        // Shipping capacity
        // ---------------------------------------------------------------------

        const vector<int64> packages = {
            3, 2, 2, 4, 1, 4
        };

        const int64 deliveryDays = 3;

        const int64 capacity =
            ShippingPlanner::minimumCapacity(
                packages,
                deliveryDays
            );

        cout << "Minimum shipping capacity: "
             << capacity
             << '\n';

        // ---------------------------------------------------------------------
        // Allocation
        // ---------------------------------------------------------------------

        const vector<int64> projectEffort = {
            7, 2, 5, 10, 8
        };

        const int64 engineers = 2;

        const int64 engineerCapacity =
            AllocationPlanner::minimumMaximumLoad(
                projectEffort,
                engineers
            );

        cout << "Minimum maximum engineer workload: "
             << engineerCapacity
             << '\n';

        // ---------------------------------------------------------------------
        // Facility placement
        // ---------------------------------------------------------------------

        const vector<int64> locations = {
            1, 2, 4, 8, 9
        };

        const int64 facilities = 3;

        const int64 spacing =
            FacilityPlacement::maximumMinimumDistance(
                locations,
                facilities
            );

        cout << "Maximum minimum facility distance: "
             << spacing
             << '\n';

        // ---------------------------------------------------------------------
        // Industry-style operations system
        // ---------------------------------------------------------------------

        cout << "\nOperations system:\n";

        OperationsSystem system({
            {"Planning", 120},
            {"Design", 80},
            {"Development", 200},
            {"Testing", 150},
            {"Deployment", 90},
            {"Monitoring", 60}
        });

        system.printProjectPlan();

        const int64 maximumEngineerLoad =
            system.calculateEngineerCapacity(3);

        cout << "Three-engineer minimum maximum load: "
             << maximumEngineerLoad
             << '\n';

        // ---------------------------------------------------------------------
        // Trace a simple search
        // ---------------------------------------------------------------------

        cout << "\nBinary-search trace:\n";

        auto [answer, trace] =
            TraceableSearch::firstTrueWithTrace(
                1,
                100,
                [](int64 value) {
                    return value >= 73;
                }
            );

        for (const auto& step : trace) {
            cout << "low="
                 << step.low
                 << ", mid="
                 << step.mid
                 << ", high="
                 << step.high
                 << ", feasible="
                 << std::boolalpha
                 << step.feasible
                 << '\n';
        }

        cout << "Trace answer: "
             << answer
             << '\n';

        printComplexityReport();
        demonstrateValidation();
        runTests();

        cout << "\nCase study completed successfully.\n";
    }
    catch (const std::exception& error) {
        std::cerr << "Fatal error: "
                  << error.what()
                  << '\n';

        return 1;
    }

    return 0;
}
