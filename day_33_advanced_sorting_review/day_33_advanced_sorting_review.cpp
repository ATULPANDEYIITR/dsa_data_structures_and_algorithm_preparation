#include <algorithm>
#include <chrono>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <optional>
#include <queue>
#include <random>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

/*
 * Advanced Sorting Review
 *
 * Technical case study:
 *
 * A release-engineering system receives batches of integer metrics produced
 * by build and deployment pipelines. The system must:
 *
 * - sort metrics reliably;
 * - exploit small bounded integer domains with counting sort;
 * - provide deterministic O(n log n) worst-case behavior with heap sort;
 * - detect duplicate measurements;
 * - merge maintenance windows;
 * - schedule non-overlapping engineering jobs;
 * - calculate kth-largest metrics without fully sorting every record;
 * - preserve record order when a stable sort is required.
 *
 * The program is intentionally implemented as a coherent C++ system rather
 * than as a collection of isolated syntax examples.
 *
 * Compile:
 *   g++ -std=c++17 -O2 advanced_sorting_review.cpp -o sorting_review
 */


namespace sorting_review {

using IntVector = std::vector<int>;


// ---------------------------------------------------------------------------
// Validation and common utilities
// ---------------------------------------------------------------------------

void validate_integer_data(const IntVector& values) {
    // int already provides a fixed numeric type in this program. The runtime
    // validation focuses on domain constraints rather than type conversion.
    if (values.size() > 10'000'000) {
        throw std::length_error(
            "dataset exceeds the case-study safety limit"
        );
    }
}

bool is_sorted_non_decreasing(const IntVector& values) {
    return std::is_sorted(values.begin(), values.end());
}

bool contains_same_values(
    const IntVector& original,
    const IntVector& result
) {
    if (original.size() != result.size()) {
        return false;
    }

    IntVector left = original;
    IntVector right = result;

    std::sort(left.begin(), left.end());
    std::sort(right.begin(), right.end());

    return left == right;
}

void verify_sort(
    const std::function<IntVector(const IntVector&)>& sorter,
    const IntVector& input,
    const std::string& name
) {
    const IntVector result = sorter(input);

    if (!is_sorted_non_decreasing(result)) {
        throw std::runtime_error(name + " returned unsorted data");
    }

    if (!contains_same_values(input, result)) {
        throw std::runtime_error(
            name + " changed the input multiset"
        );
    }
}


// ---------------------------------------------------------------------------
// Counting sort
// ---------------------------------------------------------------------------

IntVector counting_sort(
    const IntVector& values,
    std::size_t maximum_range_ratio = 50
) {
    validate_integer_data(values);

    if (values.empty()) {
        return {};
    }

    const auto [minimum_iterator, maximum_iterator] =
        std::minmax_element(values.begin(), values.end());

    const long long minimum = *minimum_iterator;
    const long long maximum = *maximum_iterator;

    const long long range = maximum - minimum + 1;

    if (range <= 0) {
        throw std::overflow_error(
            "integer range overflowed"
        );
    }

    /*
     * Counting sort uses O(k) auxiliary memory. Without a range guard,
     * values such as {-2'000'000'000, 2'000'000'000} would make the algorithm
     * request an impractical count array even though n is only two.
     */
    const unsigned long long allowed =
        static_cast<unsigned long long>(values.size())
        * maximum_range_ratio;

    if (static_cast<unsigned long long>(range) >
        std::max<unsigned long long>(1, allowed)) {
        throw std::invalid_argument(
            "counting sort rejected a sparse numeric range"
        );
    }

    std::vector<std::size_t> counts(
        static_cast<std::size_t>(range),
        0
    );

    for (int value : values) {
        const auto offset =
            static_cast<std::size_t>(
                static_cast<long long>(value) - minimum
            );

        ++counts[offset];
    }

    /*
     * Prefix sums turn frequencies into final exclusive/end positions.
     * These positions allow a stable placement pass.
     */
    for (std::size_t i = 1; i < counts.size(); ++i) {
        counts[i] += counts[i - 1];
    }

    IntVector result(values.size());

    /*
     * Reverse traversal is what preserves the order of equal values.
     * Counting sort therefore becomes suitable for records when their key
     * range is sufficiently small.
     */
    for (auto iterator = values.rbegin();
         iterator != values.rend();
         ++iterator) {

        const int value = *iterator;

        const auto offset =
            static_cast<std::size_t>(
                static_cast<long long>(value) - minimum
            );

        --counts[offset];
        result[counts[offset]] = value;
    }

    return result;
}


// ---------------------------------------------------------------------------
// Heap sort
// ---------------------------------------------------------------------------

IntVector heap_sort(const IntVector& values) {
    validate_integer_data(values);

    IntVector data = values;

    /*
     * sift_down maintains the max-heap property for one subtree.
     *
     * For a zero-based array:
     * left child  = 2 * root + 1
     * right child = 2 * root + 2
     */
    const auto sift_down =
        [&data](std::size_t root, std::size_t heap_size) {
            while (true) {
                const std::size_t left = root * 2 + 1;
                const std::size_t right = root * 2 + 2;

                std::size_t largest = root;

                if (left < heap_size &&
                    data[left] > data[largest]) {
                    largest = left;
                }

                if (right < heap_size &&
                    data[right] > data[largest]) {
                    largest = right;
                }

                if (largest == root) {
                    break;
                }

                std::swap(data[root], data[largest]);
                root = largest;
            }
        };

    /*
     * Leaf nodes already satisfy the heap property. Building from the final
     * internal node toward the root therefore constructs the complete heap
     * in linear time.
     */
    if (data.size() >= 2) {
        for (std::size_t index = data.size() / 2;
             index-- > 0;) {
            sift_down(index, data.size());
        }
    }

    /*
     * The maximum element is at data[0]. Moving it to the end creates the
     * sorted suffix and reduces the active heap by one element.
     */
    for (std::size_t end = data.size(); end-- > 1;) {
        std::swap(data[0], data[end]);
        sift_down(0, end);
    }

    return data;
}


// ---------------------------------------------------------------------------
// Stable record sorting
// ---------------------------------------------------------------------------

struct BuildMetric {
    int priority;
    int original_sequence;
    std::string pipeline;
    int value;
};

std::vector<BuildMetric> stable_priority_sort(
    std::vector<BuildMetric> records
) {
    /*
     * std::stable_sort guarantees that records with equal priority retain
     * their original relative order. This matters when priority is only one
     * part of a larger record-processing policy.
     */
    std::stable_sort(
        records.begin(),
        records.end(),
        [](const BuildMetric& left, const BuildMetric& right) {
            return left.priority < right.priority;
        }
    );

    return records;
}


// ---------------------------------------------------------------------------
// Sorting-based problem solving: duplicate detection
// ---------------------------------------------------------------------------

bool contains_duplicate_by_sorting(const IntVector& values) {
    IntVector data = values;
    std::sort(data.begin(), data.end());

    for (std::size_t i = 1; i < data.size(); ++i) {
        if (data[i] == data[i - 1]) {
            return true;
        }
    }

    return false;
}


// ---------------------------------------------------------------------------
// Sorting-based problem solving: two-sum
// ---------------------------------------------------------------------------

std::optional<std::pair<int, int>> two_sum_sorted(
    const IntVector& values,
    long long target
) {
    IntVector data = values;
    std::sort(data.begin(), data.end());

    std::size_t left = 0;

    if (data.empty()) {
        return std::nullopt;
    }

    std::size_t right = data.size() - 1;

    while (left < right) {
        const long long total =
            static_cast<long long>(data[left])
            + static_cast<long long>(data[right]);

        if (total == target) {
            return std::make_pair(
                data[left],
                data[right]
            );
        }

        if (total < target) {
            ++left;
        } else {
            --right;
        }
    }

    return std::nullopt;
}


// ---------------------------------------------------------------------------
// Sorting-based problem solving: interval merging
// ---------------------------------------------------------------------------

struct Interval {
    int start;
    int end;
};

std::vector<Interval> merge_intervals(
    std::vector<Interval> intervals
) {
    for (const Interval& interval : intervals) {
        if (interval.start > interval.end) {
            throw std::invalid_argument(
                "interval start exceeds interval end"
            );
        }
    }

    std::sort(
        intervals.begin(),
        intervals.end(),
        [](const Interval& left, const Interval& right) {
            if (left.start != right.start) {
                return left.start < right.start;
            }

            return left.end < right.end;
        }
    );

    if (intervals.empty()) {
        return {};
    }

    std::vector<Interval> merged;
    merged.push_back(intervals.front());

    for (std::size_t i = 1; i < intervals.size(); ++i) {
        Interval& current = merged.back();
        const Interval& next = intervals[i];

        if (next.start <= current.end) {
            current.end = std::max(
                current.end,
                next.end
            );
        } else {
            merged.push_back(next);
        }
    }

    return merged;
}


// ---------------------------------------------------------------------------
// Sorting-based problem solving: interval scheduling
// ---------------------------------------------------------------------------

struct EngineeringJob {
    std::string name;
    int start;
    int finish;
};

std::vector<EngineeringJob> select_non_overlapping_jobs(
    std::vector<EngineeringJob> jobs
) {
    for (const auto& job : jobs) {
        if (job.start > job.finish) {
            throw std::invalid_argument(
                "engineering job has invalid time range"
            );
        }
    }

    /*
     * Earliest-finish-time ordering is the key structure behind the greedy
     * interval-scheduling solution.
     */
    std::sort(
        jobs.begin(),
        jobs.end(),
        [](const EngineeringJob& left,
           const EngineeringJob& right) {
            return left.finish < right.finish;
        }
    );

    std::vector<EngineeringJob> selected;

    bool has_previous = false;
    int previous_finish = 0;

    for (const auto& job : jobs) {
        if (!has_previous || job.start >= previous_finish) {
            selected.push_back(job);
            previous_finish = job.finish;
            has_previous = true;
        }
    }

    return selected;
}


// ---------------------------------------------------------------------------
// kth-largest problem using a bounded heap
// ---------------------------------------------------------------------------

int kth_largest_with_heap(
    const IntVector& values,
    std::size_t k
) {
    if (k == 0 || k > values.size()) {
        throw std::out_of_range(
            "k must be between one and the number of values"
        );
    }

    /*
     * A min-heap of size k contains the k largest values seen so far.
     * Its root is the smallest among those k candidates, which is exactly
     * the kth-largest value.
     */
    std::priority_queue<
        int,
        std::vector<int>,
        std::greater<int>
    > candidates;

    for (int value : values) {
        if (candidates.size() < k) {
            candidates.push(value);
        } else if (value > candidates.top()) {
            candidates.pop();
            candidates.push(value);
        }
    }

    return candidates.top();
}


// ---------------------------------------------------------------------------
// Repository metric case study
// ---------------------------------------------------------------------------

class ReleaseMetricsEngine {
public:
    explicit ReleaseMetricsEngine(
        std::string release_name
    )
        : release_name_(std::move(release_name)) {}

    void ingest(const IntVector& metrics) {
        validate_integer_data(metrics);

        metrics_ = metrics;
    }

    const std::string& release_name() const {
        return release_name_;
    }

    IntVector sorted_with_counting_sort() const {
        return counting_sort(metrics_);
    }

    IntVector sorted_with_heap_sort() const {
        return heap_sort(metrics_);
    }

    bool has_duplicate_metrics() const {
        return contains_duplicate_by_sorting(metrics_);
    }

    std::optional<std::pair<int, int>> find_pair_with_target(
        long long target
    ) const {
        return two_sum_sorted(metrics_, target);
    }

    int kth_largest(std::size_t k) const {
        return kth_largest_with_heap(metrics_, k);
    }

private:
    std::string release_name_;
    IntVector metrics_;
};


// ---------------------------------------------------------------------------
// Benchmark infrastructure
// ---------------------------------------------------------------------------

struct BenchmarkResult {
    std::string algorithm;
    double milliseconds;
};

BenchmarkResult benchmark_sort(
    const std::string& name,
    const std::function<IntVector(const IntVector&)>& sorter,
    const IntVector& data
) {
    const auto start = std::chrono::steady_clock::now();

    const IntVector result = sorter(data);

    const auto finish = std::chrono::steady_clock::now();

    if (!is_sorted_non_decreasing(result)) {
        throw std::runtime_error(
            name + " failed benchmark validation"
        );
    }

    const std::chrono::duration<double, std::milli> elapsed =
        finish - start;

    return {
        name,
        elapsed.count()
    };
}

IntVector make_benchmark_data(
    std::size_t size,
    int maximum
) {
    std::mt19937 generator(42);
    std::uniform_int_distribution<int> distribution(
        0,
        maximum
    );

    IntVector data(size);

    for (int& value : data) {
        value = distribution(generator);
    }

    return data;
}


// ---------------------------------------------------------------------------
// Demonstration functions
// ---------------------------------------------------------------------------

void demonstrate_counting_sort() {
    const IntVector data{
        7, -2, 5, 5, 0, -2, 3, 9, 1
    };

    std::cout << "\nCounting sort\n";
    std::cout << "Input: ";

    for (int value : data) {
        std::cout << value << ' ';
    }

    std::cout << "\nOutput: ";

    for (int value : counting_sort(data)) {
        std::cout << value << ' ';
    }

    std::cout << '\n';

    /*
     * This deliberately demonstrates why numeric range matters. A two-item
     * dataset can still make counting sort inappropriate if its keys are
     * extremely far apart.
     */
    try {
        counting_sort({1, 1'000'000'000});
    } catch (const std::exception& error) {
        std::cout
            << "Sparse-range protection: "
            << error.what()
            << '\n';
    }
}

void demonstrate_heap_sort() {
    const IntVector data{
        19, 3, 14, 7, 2, 18, 11, 5
    };

    const IntVector result = heap_sort(data);

    std::cout << "\nHeap sort\n";
    std::cout << "Output: ";

    for (int value : result) {
        std::cout << value << ' ';
    }

    std::cout << '\n';
}

void demonstrate_stability() {
    const std::vector<BuildMetric> records{
        {2, 0, "API", 500},
        {1, 1, "WEB", 700},
        {2, 2, "API", 300},
        {1, 3, "DB", 900},
        {2, 4, "WEB", 200}
    };

    const auto sorted = stable_priority_sort(records);

    std::cout << "\nStable priority sorting\n";

    for (const auto& record : sorted) {
        std::cout
            << "priority=" << record.priority
            << ", original_sequence=" << record.original_sequence
            << ", pipeline=" << record.pipeline
            << ", value=" << record.value
            << '\n';
    }
}

void demonstrate_problem_solving() {
    std::cout << "\nSorting-based problem solving\n";

    const IntVector duplicate_data{
        4, 9, 1, 4, 7
    };

    std::cout
        << "Duplicate detected: "
        << std::boolalpha
        << contains_duplicate_by_sorting(duplicate_data)
        << '\n';

    const auto pair = two_sum_sorted(
        {10, 3, 7, 2, 15},
        9
    );

    if (pair.has_value()) {
        std::cout
            << "Two-sum pair: "
            << pair->first
            << " + "
            << pair->second
            << '\n';
    }

    const auto merged = merge_intervals({
        {1, 5},
        {2, 7},
        {10, 12},
        {11, 15}
    });

    std::cout << "Merged intervals: ";

    for (const auto& interval : merged) {
        std::cout
            << '['
            << interval.start
            << ','
            << interval.end
            << "] ";
    }

    std::cout << '\n';

    const auto jobs = select_non_overlapping_jobs({
        {"API maintenance", 1, 3},
        {"database migration", 3, 5},
        {"security review", 0, 2},
        {"release validation", 5, 7},
        {"performance test", 4, 6}
    });

    std::cout << "Selected engineering jobs: ";

    for (const auto& job : jobs) {
        std::cout << job.name << " | ";
    }

    std::cout << '\n';

    std::cout
        << "2nd largest metric: "
        << kth_largest_with_heap(
            {91, 13, 55, 72, 40, 99},
            2
        )
        << '\n';
}

void demonstrate_case_study() {
    ReleaseMetricsEngine engine(
        "release-2026-10"
    );

    engine.ingest({
        18, 7, 18, 4, 11, 7, 3, 15, 9, 11
    });

    std::cout << "\nRelease metrics case study\n";
    std::cout
        << "Release: "
        << engine.release_name()
        << '\n';

    std::cout
        << "Duplicate metrics: "
        << std::boolalpha
        << engine.has_duplicate_metrics()
        << '\n';

    std::cout << "Counting-sort result: ";

    for (int value : engine.sorted_with_counting_sort()) {
        std::cout << value << ' ';
    }

    std::cout << "\nHeap-sort result: ";

    for (int value : engine.sorted_with_heap_sort()) {
        std::cout << value << ' ';
    }

    std::cout << '\n';

    std::cout
        << "3rd largest metric: "
        << engine.kth_largest(3)
        << '\n';

    const auto pair =
        engine.find_pair_with_target(22);

    if (pair.has_value()) {
        std::cout
            << "Metrics summing to 22: "
            << pair->first
            << " + "
            << pair->second
            << '\n';
    }
}

void demonstrate_benchmarks() {
    /*
     * A bounded integer domain is deliberately chosen so counting sort has
     * an opportunity to exploit O(n + k), while heap sort maintains its
     * O(n log n) guarantee independently of the key distribution.
     */
    const IntVector data =
        make_benchmark_data(100'000, 10'000);

    std::vector<BenchmarkResult> results;

    results.push_back(
        benchmark_sort(
            "Counting Sort",
            [](const IntVector& values) {
                return counting_sort(values);
            },
            data
        )
    );

    results.push_back(
        benchmark_sort(
            "Heap Sort",
            [](const IntVector& values) {
                return heap_sort(values);
            },
            data
        )
    );

    std::cout << "\nBenchmark for 100,000 bounded integer metrics\n";

    for (const auto& result : results) {
        std::cout
            << "  "
            << std::left
            << std::setw(16)
            << result.algorithm
            << std::right
            << std::fixed
            << std::setprecision(3)
            << result.milliseconds
            << " ms\n";
    }
}


// ---------------------------------------------------------------------------
// Deterministic correctness suite
// ---------------------------------------------------------------------------

void run_assertions() {
    const std::vector<IntVector> cases{
        {},
        {1},
        {4, 1, 3, 2},
        {5, 5, 5},
        {-10, 0, 7, -3, 2, -3},
        {100, 1, 50, 1, 100}
    };

    const std::vector<
        std::pair<
            std::string,
            std::function<IntVector(const IntVector&)>
        >
    > sorters{
        {
            "Counting Sort",
            [](const IntVector& values) {
                return counting_sort(values);
            }
        },
        {
            "Heap Sort",
            [](const IntVector& values) {
                return heap_sort(values);
            }
        }
    };

    for (const auto& [name, sorter] : sorters) {
        for (const auto& values : cases) {
            verify_sort(sorter, values, name);
        }
    }

    if (!contains_duplicate_by_sorting({1, 2, 2})) {
        throw std::runtime_error(
            "duplicate detection failed"
        );
    }

    if (contains_duplicate_by_sorting({1, 2, 3})) {
        throw std::runtime_error(
            "duplicate detection false positive"
        );
    }

    const auto intervals =
        merge_intervals({{1, 3}, {3, 5}});

    if (intervals.size() != 1 ||
        intervals[0].start != 1 ||
        intervals[0].end != 5) {
        throw std::runtime_error(
            "interval merging failed"
        );
    }

    const auto pair =
        two_sum_sorted({3, 1, 4, 8}, 7);

    if (!pair.has_value() ||
        pair->first != 3 ||
        pair->second != 4) {
        throw std::runtime_error(
            "two-sum failed"
        );
    }

    if (
        kth_largest_with_heap({9, 2, 7, 5}, 1) != 9 ||
        kth_largest_with_heap({9, 2, 7, 5}, 4) != 2
    ) {
        throw std::runtime_error(
            "kth-largest calculation failed"
        );
    }
}

void print_complexity_reference() {
    std::cout << "\nFinal comparison\n";
    std::cout
        << std::left
        << std::setw(18) << "Algorithm"
        << std::setw(16) << "Average Time"
        << std::setw(16) << "Worst Time"
        << std::setw(16) << "Extra Space"
        << std::setw(12) << "Stable"
        << '\n';

    std::cout << std::string(78, '-') << '\n';

    std::cout
        << std::setw(18) << "Bubble Sort"
        << std::setw(16) << "O(n²)"
        << std::setw(16) << "O(n²)"
        << std::setw(16) << "O(1)"
        << std::setw(12) << "Yes"
        << '\n';

    std::cout
        << std::setw(18) << "Selection Sort"
        << std::setw(16) << "O(n²)"
        << std::setw(16) << "O(n²)"
        << std::setw(16) << "O(1)"
        << std::setw(12) << "Usually No"
        << '\n';

    std::cout
        << std::setw(18) << "Insertion Sort"
        << std::setw(16) << "O(n²)"
        << std::setw(16) << "O(n²)"
        << std::setw(16) << "O(1)"
        << std::setw(12) << "Yes"
        << '\n';

    std::cout
        << std::setw(18) << "Merge Sort"
        << std::setw(16) << "O(n log n)"
        << std::setw(16) << "O(n log n)"
        << std::setw(16) << "O(n)"
        << std::setw(12) << "Yes"
        << '\n';

    std::cout
        << std::setw(18) << "Quick Sort"
        << std::setw(16) << "O(n log n)"
        << std::setw(16) << "O(n²)"
        << std::setw(16) << "Depends"
        << std::setw(12) << "Usually No"
        << '\n';

    std::cout
        << std::setw(18) << "Counting Sort"
        << std::setw(16) << "O(n + k)"
        << std::setw(16) << "O(n + k)"
        << std::setw(16) << "O(n + k)"
        << std::setw(12) << "Can be"
        << '\n';

    std::cout
        << std::setw(18) << "Heap Sort"
        << std::setw(16) << "O(n log n)"
        << std::setw(16) << "O(n log n)"
        << std::setw(16) << "O(1)"
        << std::setw(12) << "No"
        << '\n';
}

} // namespace sorting_review


int main() {
    using namespace sorting_review;

    try {
        std::cout
            << "============================================================\n"
            << "ADVANCED SORTING REVIEW\n"
            << "============================================================\n";

        run_assertions();

        demonstrate_counting_sort();
        demonstrate_heap_sort();
        demonstrate_stability();
        demonstrate_problem_solving();
        demonstrate_case_study();
        demonstrate_benchmarks();
        print_complexity_reference();

        std::cout
            << "\nAll C++ correctness checks passed.\n";

        return 0;
    } catch (const std::exception& error) {
        std::cerr
            << "Execution failed: "
            << error.what()
            << '\n';

        return 1;
    }
}
