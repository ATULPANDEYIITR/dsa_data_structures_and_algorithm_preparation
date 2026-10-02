#include <algorithm>
#include <chrono>
#include <cstddef>
#include <functional>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

/*
 * C++17 Quick Sort Case Study
 *
 * Scenario:
 * A data-processing service receives batches of integer transaction amounts
 * that must be ordered before percentile, range, and threshold calculations.
 *
 * The service needs to understand how pivot selection, partitioning,
 * recursion, duplicate values, and worst-case input patterns affect sorting.
 *
 * This program implements:
 * - configurable pivot selection
 * - Lomuto partitioning
 * - recursive quick sort
 * - three-way partitioning
 * - iterative quick sort
 * - merge sort
 * - operation metrics
 * - validation and correctness checks
 * - adversarial-input analysis
 * - a realistic batch-processing workflow
 *
 * Compile:
 *   g++ -std=c++17 -O2 quick_sort.cpp -o quick_sort
 */

struct SortMetrics {
    std::size_t comparisons = 0;
    std::size_t swaps = 0;
    std::size_t partitions = 0;
    std::size_t recursive_calls = 0;
    std::size_t max_depth = 0;
};

enum class PivotStrategy {
    First,
    Last,
    Middle,
    Random,
    MedianOfThree
};

struct BatchReport {
    std::size_t count = 0;
    long long minimum = 0;
    long long maximum = 0;
    double median = 0.0;
};

void validate_input(const std::vector<int>& values) {
    /*
     * The vector itself can be empty. An empty batch is valid because there
     * is no element whose ordering needs to be determined.
     */
    if (values.size() > 10'000'000) {
        throw std::invalid_argument(
            "Batch exceeds the configured demonstration size limit."
        );
    }
}

bool is_sorted(const std::vector<int>& values) {
    return std::is_sorted(values.begin(), values.end());
}

void swap_values(
    std::vector<int>& values,
    std::size_t left,
    std::size_t right,
    SortMetrics& metrics
) {
    if (left == right) {
        return;
    }

    std::swap(values[left], values[right]);
    ++metrics.swaps;
}

std::size_t choose_pivot_index(
    const std::vector<int>& values,
    std::size_t low,
    std::size_t high,
    PivotStrategy strategy,
    std::mt19937& generator
) {
    switch (strategy) {
        case PivotStrategy::First:
            return low;

        case PivotStrategy::Last:
            return high;

        case PivotStrategy::Middle:
            return low + (high - low) / 2;

        case PivotStrategy::Random: {
            std::uniform_int_distribution<std::size_t> distribution(low, high);
            return distribution(generator);
        }

        case PivotStrategy::MedianOfThree: {
            const std::size_t middle = low + (high - low) / 2;

            std::array<std::pair<int, std::size_t>, 3> candidates = {{
                {values[low], low},
                {values[middle], middle},
                {values[high], high}
            }};

            std::sort(
                candidates.begin(),
                candidates.end(),
                [](const auto& left, const auto& right) {
                    return left.first < right.first;
                }
            );

            return candidates[1].second;
        }
    }

    throw std::invalid_argument("Unsupported pivot strategy.");
}

std::size_t lomuto_partition(
    std::vector<int>& values,
    std::size_t low,
    std::size_t high,
    SortMetrics& metrics
) {
    ++metrics.partitions;

    const int pivot = values[high];
    std::size_t boundary = low;

    for (std::size_t current = low; current < high; ++current) {
        ++metrics.comparisons;

        if (values[current] <= pivot) {
            swap_values(values, boundary, current, metrics);
            ++boundary;
        }
    }

    swap_values(values, boundary, high, metrics);
    return boundary;
}

void quick_sort_recursive_range(
    std::vector<int>& values,
    std::size_t low,
    std::size_t high,
    PivotStrategy strategy,
    SortMetrics& metrics,
    std::mt19937& generator,
    std::size_t depth
) {
    ++metrics.recursive_calls;
    metrics.max_depth = std::max(metrics.max_depth, depth);

    if (low >= high) {
        return;
    }

    const std::size_t pivot_index = choose_pivot_index(
        values,
        low,
        high,
        strategy,
        generator
    );

    swap_values(values, pivot_index, high, metrics);

    const std::size_t final_pivot = lomuto_partition(
        values,
        low,
        high,
        metrics
    );

    if (final_pivot > low) {
        quick_sort_recursive_range(
            values,
            low,
            final_pivot - 1,
            strategy,
            metrics,
            generator,
            depth + 1
        );
    }

    if (final_pivot < high) {
        quick_sort_recursive_range(
            values,
            final_pivot + 1,
            high,
            strategy,
            metrics,
            generator,
            depth + 1
        );
    }
}

SortMetrics quick_sort_recursive(
    std::vector<int>& values,
    PivotStrategy strategy
) {
    validate_input(values);

    SortMetrics metrics;

    if (values.size() < 2) {
        return metrics;
    }

    std::mt19937 generator(2026);

    quick_sort_recursive_range(
        values,
        0,
        values.size() - 1,
        strategy,
        metrics,
        generator,
        1
    );

    return metrics;
}

std::pair<std::size_t, std::size_t> three_way_partition(
    std::vector<int>& values,
    std::size_t low,
    std::size_t high,
    SortMetrics& metrics
) {
    ++metrics.partitions;

    const int pivot = values[low + (high - low) / 2];

    std::size_t less = low;
    std::size_t current = low;
    std::size_t greater = high;

    while (current <= greater) {
        ++metrics.comparisons;

        if (values[current] < pivot) {
            swap_values(values, less, current, metrics);
            ++less;
            ++current;
        } else if (values[current] > pivot) {
            swap_values(values, current, greater, metrics);

            /*
             * The swapped-in element at current has not been classified yet,
             * so current is intentionally not incremented here.
             */
            if (greater == 0) {
                break;
            }
            --greater;
        } else {
            ++current;
        }
    }

    return {less, greater};
}

void three_way_recursive(
    std::vector<int>& values,
    std::size_t low,
    std::size_t high,
    SortMetrics& metrics,
    std::size_t depth
) {
    ++metrics.recursive_calls;
    metrics.max_depth = std::max(metrics.max_depth, depth);

    if (low >= high) {
        return;
    }

    const auto [equal_start, equal_end] =
        three_way_partition(values, low, high, metrics);

    if (equal_start > low) {
        three_way_recursive(
            values,
            low,
            equal_start - 1,
            metrics,
            depth + 1
        );
    }

    if (equal_end < high) {
        three_way_recursive(
            values,
            equal_end + 1,
            high,
            metrics,
            depth + 1
        );
    }
}

SortMetrics quick_sort_three_way(std::vector<int>& values) {
    validate_input(values);

    SortMetrics metrics;

    if (values.size() < 2) {
        return metrics;
    }

    three_way_recursive(
        values,
        0,
        values.size() - 1,
        metrics,
        1
    );

    return metrics;
}

SortMetrics quick_sort_iterative(std::vector<int>& values) {
    validate_input(values);

    SortMetrics metrics;

    if (values.size() < 2) {
        return metrics;
    }

    std::vector<std::pair<std::size_t, std::size_t>> ranges;
    ranges.emplace_back(0, values.size() - 1);

    /*
     * This explicit stack replaces recursive calls. The smaller partition is
     * pushed after the larger one so that it is processed first, helping
     * control auxiliary stack growth.
     */
    while (!ranges.empty()) {
        const auto [low, high] = ranges.back();
        ranges.pop_back();

        if (low >= high) {
            continue;
        }

        const std::size_t middle = low + (high - low) / 2;
        swap_values(values, middle, high, metrics);

        const std::size_t pivot_index =
            lomuto_partition(values, low, high, metrics);

        const bool has_left = pivot_index > low;
        const bool has_right = pivot_index < high;

        if (has_left && has_right) {
            const std::size_t left_size = pivot_index - low;
            const std::size_t right_size = high - pivot_index;

            if (left_size > right_size) {
                ranges.emplace_back(low, pivot_index - 1);
                ranges.emplace_back(pivot_index + 1, high);
            } else {
                ranges.emplace_back(pivot_index + 1, high);
                ranges.emplace_back(low, pivot_index - 1);
            }
        } else if (has_left) {
            ranges.emplace_back(low, pivot_index - 1);
        } else if (has_right) {
            ranges.emplace_back(pivot_index + 1, high);
        }
    }

    return metrics;
}

void merge_ranges(
    std::vector<int>& values,
    std::vector<int>& temporary,
    std::size_t left,
    std::size_t middle,
    std::size_t right,
    SortMetrics& metrics
) {
    std::size_t left_index = left;
    std::size_t right_index = middle + 1;
    std::size_t output = left;

    while (left_index <= middle && right_index <= right) {
        ++metrics.comparisons;

        if (values[left_index] <= values[right_index]) {
            temporary[output++] = values[left_index++];
        } else {
            temporary[output++] = values[right_index++];
        }
    }

    while (left_index <= middle) {
        temporary[output++] = values[left_index++];
    }

    while (right_index <= right) {
        temporary[output++] = values[right_index++];
    }

    for (std::size_t index = left; index <= right; ++index) {
        values[index] = temporary[index];
    }
}

void merge_sort_range(
    std::vector<int>& values,
    std::vector<int>& temporary,
    std::size_t left,
    std::size_t right,
    SortMetrics& metrics,
    std::size_t depth
) {
    ++metrics.recursive_calls;
    metrics.max_depth = std::max(metrics.max_depth, depth);

    if (left >= right) {
        return;
    }

    const std::size_t middle = left + (right - left) / 2;

    merge_sort_range(
        values,
        temporary,
        left,
        middle,
        metrics,
        depth + 1
    );

    merge_sort_range(
        values,
        temporary,
        middle + 1,
        right,
        metrics,
        depth + 1
    );

    merge_ranges(
        values,
        temporary,
        left,
        middle,
        right,
        metrics
    );
}

SortMetrics merge_sort(std::vector<int>& values) {
    validate_input(values);

    SortMetrics metrics;

    if (values.size() < 2) {
        return metrics;
    }

    std::vector<int> temporary(values.size());

    merge_sort_range(
        values,
        temporary,
        0,
        values.size() - 1,
        metrics,
        1
    );

    return metrics;
}

BatchReport analyze_sorted_transactions(
    const std::vector<int>& sorted_transactions
) {
    if (sorted_transactions.empty()) {
        return {};
    }

    BatchReport report;
    report.count = sorted_transactions.size();
    report.minimum = sorted_transactions.front();
    report.maximum = sorted_transactions.back();

    const std::size_t middle = sorted_transactions.size() / 2;

    if (sorted_transactions.size() % 2 == 0) {
        report.median =
            (static_cast<double>(sorted_transactions[middle - 1]) +
             static_cast<double>(sorted_transactions[middle])) / 2.0;
    } else {
        report.median = sorted_transactions[middle];
    }

    return report;
}

void print_metrics(
    const std::string& name,
    const SortMetrics& metrics
) {
    std::cout
        << std::left
        << std::setw(24)
        << name
        << " comparisons=" << std::setw(7) << metrics.comparisons
        << " swaps=" << std::setw(6) << metrics.swaps
        << " partitions=" << std::setw(6) << metrics.partitions
        << " depth=" << std::setw(5) << metrics.max_depth
        << '\n';
}

void demonstrate_partition() {
    std::cout << "\n=== Pivot and Partition ===\n";

    std::vector<int> values = {
        29, 10, 14, 37, 13, 8, 42, 18
    };

    const std::vector<int> original = values;
    SortMetrics metrics;

    const std::size_t pivot_index =
        lomuto_partition(values, 0, values.size() - 1, metrics);

    std::cout << "Original: ";
    for (int value : original) {
        std::cout << value << ' ';
    }

    std::cout << "\nAfter:    ";
    for (int value : values) {
        std::cout << value << ' ';
    }

    std::cout << "\nPivot value: " << values[pivot_index]
              << "\nPivot index: " << pivot_index
              << "\n";

    print_metrics("partition", metrics);
}

void demonstrate_pivot_strategies() {
    std::cout << "\n=== Pivot Strategy Comparison ===\n";

    const std::vector<int> input = {
        41, 8, 29, 17, 63, 4, 52, 31, 22, 70, 11
    };

    const std::vector<std::pair<std::string, PivotStrategy>> strategies = {
        {"first", PivotStrategy::First},
        {"last", PivotStrategy::Last},
        {"middle", PivotStrategy::Middle},
        {"random", PivotStrategy::Random},
        {"median_of_three", PivotStrategy::MedianOfThree}
    };

    for (const auto& [name, strategy] : strategies) {
        std::vector<int> values = input;
        const SortMetrics metrics =
            quick_sort_recursive(values, strategy);

        print_metrics(name, metrics);

        if (!is_sorted(values)) {
            throw std::runtime_error(
                "Pivot strategy produced an incorrectly sorted array."
            );
        }
    }
}

void demonstrate_worst_case() {
    std::cout << "\n=== Worst-Case Behavior ===\n";

    constexpr std::size_t size = 300;

    std::vector<int> values(size);
    for (std::size_t index = 0; index < size; ++index) {
        values[index] = static_cast<int>(index);
    }

    const SortMetrics metrics =
        quick_sort_recursive(values, PivotStrategy::Last);

    const std::size_t expected =
        size * (size - 1) / 2;

    std::cout << "Input is already sorted.\n";
    std::cout << "Input size: " << size << '\n';
    std::cout << "Correct: " << std::boolalpha << is_sorted(values) << '\n';
    std::cout << "Observed comparisons: " << metrics.comparisons << '\n';
    std::cout << "n(n-1)/2: " << expected << '\n';
    std::cout << "Maximum recursion depth: "
              << metrics.max_depth << '\n';

    std::cout
        << "The last-element pivot is an extreme element on this input, "
        << "so each partition leaves one large unsorted side.\n";
}

void demonstrate_duplicate_handling() {
    std::cout << "\n=== Duplicate-Heavy Data ===\n";

    const std::vector<int> input = {
        5, 3, 5, 2, 5, 8, 5, 1, 3, 5,
        4, 5, 2, 5, 7, 5, 3, 5, 6, 5
    };

    std::vector<int> standard = input;
    std::vector<int> three_way = input;

    const SortMetrics standard_metrics =
        quick_sort_recursive(
            standard,
            PivotStrategy::MedianOfThree
        );

    const SortMetrics three_way_metrics =
        quick_sort_three_way(three_way);

    print_metrics("two-way quick sort", standard_metrics);
    print_metrics("three-way quick sort", three_way_metrics);

    if (standard != three_way) {
        throw std::runtime_error(
            "Two-way and three-way implementations disagree."
        );
    }

    std::cout
        << "Three-way partitioning places all values equal to the pivot "
        << "into a region that requires no further recursive sorting.\n";
}

void demonstrate_transaction_batch() {
    std::cout << "\n=== Transaction Batch Case Study ===\n";

    /*
     * These values represent transaction amounts in cents. The sort is not
     * the business result itself; it is an intermediate operation needed for
     * ordered statistics such as minimum, maximum, and median.
     */
    std::vector<int> transactions = {
        1499, 799, 2499, 1499, 5200, 1299, 799,
        9999, 2499, 1899, 5200, 1299, 749, 2499
    };

    std::cout << "Incoming transaction amounts (cents): ";
    for (int amount : transactions) {
        std::cout << amount << ' ';
    }
    std::cout << '\n';

    const SortMetrics metrics =
        quick_sort_three_way(transactions);

    if (!is_sorted(transactions)) {
        throw std::runtime_error(
            "Transaction batch failed validation after sorting."
        );
    }

    const BatchReport report =
        analyze_sorted_transactions(transactions);

    std::cout << "Sorted amounts: ";
    for (int amount : transactions) {
        std::cout << amount << ' ';
    }

    std::cout << "\nRecords: " << report.count
              << "\nMinimum cents: " << report.minimum
              << "\nMaximum cents: " << report.maximum
              << "\nMedian cents: " << std::fixed
              << std::setprecision(1)
              << report.median
              << '\n';

    print_metrics("transaction quick sort", metrics);
}

void benchmark_quick_sort_and_merge_sort() {
    std::cout << "\n=== Quick Sort vs Merge Sort ===\n";

    std::mt19937 generator(2026);
    std::uniform_int_distribution<int> distribution(-100'000, 100'000);

    std::vector<int> original(5'000);
    for (int& value : original) {
        value = distribution(generator);
    }

    std::vector<int> quick_values = original;
    std::vector<int> merge_values = original;

    const auto quick_start = std::chrono::steady_clock::now();
    const SortMetrics quick_metrics =
        quick_sort_three_way(quick_values);
    const auto quick_end = std::chrono::steady_clock::now();

    const auto merge_start = std::chrono::steady_clock::now();
    const SortMetrics merge_metrics =
        merge_sort(merge_values);
    const auto merge_end = std::chrono::steady_clock::now();

    const double quick_ms =
        std::chrono::duration<double, std::milli>(
            quick_end - quick_start
        ).count();

    const double merge_ms =
        std::chrono::duration<double, std::milli>(
            merge_end - merge_start
        ).count();

    std::cout << "Quick sort correct: "
              << std::boolalpha
              << is_sorted(quick_values)
              << '\n';

    std::cout << "Merge sort correct: "
              << std::boolalpha
              << is_sorted(merge_values)
              << '\n';

    std::cout << "Quick sort time: "
              << std::fixed << std::setprecision(3)
              << quick_ms << " ms\n";

    std::cout << "Merge sort time: "
              << std::fixed << std::setprecision(3)
              << merge_ms << " ms\n";

    print_metrics("quick sort", quick_metrics);
    print_metrics("merge sort", merge_metrics);

    std::cout
        << "Wall-clock timings vary with compiler optimization, hardware, "
        << "memory behavior, and input distribution.\n";
}

void randomized_correctness_test() {
    std::cout << "\n=== Randomized Correctness Tests ===\n";

    std::mt19937 generator(555);
    std::uniform_int_distribution<int> length_distribution(0, 100);
    std::uniform_int_distribution<int> value_distribution(-30, 30);

    for (int test_case = 0; test_case < 300; ++test_case) {
        const int length = length_distribution(generator);

        std::vector<int> input(static_cast<std::size_t>(length));

        for (int& value : input) {
            value = value_distribution(generator);
        }

        std::vector<int> expected = input;
        std::sort(expected.begin(), expected.end());

        {
            auto actual = input;
            quick_sort_recursive(
                actual,
                PivotStrategy::MedianOfThree
            );

            if (actual != expected) {
                throw std::runtime_error(
                    "Recursive quick sort failed randomized verification."
                );
            }
        }

        {
            auto actual = input;
            quick_sort_three_way(actual);

            if (actual != expected) {
                throw std::runtime_error(
                    "Three-way quick sort failed randomized verification."
                );
            }
        }

        {
            auto actual = input;
            quick_sort_iterative(actual);

            if (actual != expected) {
                throw std::runtime_error(
                    "Iterative quick sort failed randomized verification."
                );
            }
        }

        {
            auto actual = input;
            merge_sort(actual);

            if (actual != expected) {
                throw std::runtime_error(
                    "Merge sort failed randomized verification."
                );
            }
        }
    }

    std::cout
        << "300 randomized cases passed for quick sort and merge sort.\n";
}

int main() {
    try {
        std::cout << "QUICK SORT TECHNICAL CASE STUDY\n";
        std::cout << "========================================\n";

        demonstrate_partition();
        demonstrate_pivot_strategies();
        demonstrate_worst_case();
        demonstrate_duplicate_handling();
        demonstrate_transaction_batch();
        benchmark_quick_sort_and_merge_sort();
        randomized_correctness_test();

        std::cout << "\nCase study completed successfully.\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }
}#include <algorithm>
#include <chrono>
#include <cstddef>
#include <functional>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

/*
 * C++17 Quick Sort Case Study
 *
 * Scenario:
 * A data-processing service receives batches of integer transaction amounts
 * that must be ordered before percentile, range, and threshold calculations.
 *
 * The service needs to understand how pivot selection, partitioning,
 * recursion, duplicate values, and worst-case input patterns affect sorting.
 *
 * This program implements:
 * - configurable pivot selection
 * - Lomuto partitioning
 * - recursive quick sort
 * - three-way partitioning
 * - iterative quick sort
 * - merge sort
 * - operation metrics
 * - validation and correctness checks
 * - adversarial-input analysis
 * - a realistic batch-processing workflow
 *
 * Compile:
 *   g++ -std=c++17 -O2 quick_sort.cpp -o quick_sort
 */

struct SortMetrics {
    std::size_t comparisons = 0;
    std::size_t swaps = 0;
    std::size_t partitions = 0;
    std::size_t recursive_calls = 0;
    std::size_t max_depth = 0;
};

enum class PivotStrategy {
    First,
    Last,
    Middle,
    Random,
    MedianOfThree
};

struct BatchReport {
    std::size_t count = 0;
    long long minimum = 0;
    long long maximum = 0;
    double median = 0.0;
};

void validate_input(const std::vector<int>& values) {
    /*
     * The vector itself can be empty. An empty batch is valid because there
     * is no element whose ordering needs to be determined.
     */
    if (values.size() > 10'000'000) {
        throw std::invalid_argument(
            "Batch exceeds the configured demonstration size limit."
        );
    }
}

bool is_sorted(const std::vector<int>& values) {
    return std::is_sorted(values.begin(), values.end());
}

void swap_values(
    std::vector<int>& values,
    std::size_t left,
    std::size_t right,
    SortMetrics& metrics
) {
    if (left == right) {
        return;
    }

    std::swap(values[left], values[right]);
    ++metrics.swaps;
}

std::size_t choose_pivot_index(
    const std::vector<int>& values,
    std::size_t low,
    std::size_t high,
    PivotStrategy strategy,
    std::mt19937& generator
) {
    switch (strategy) {
        case PivotStrategy::First:
            return low;

        case PivotStrategy::Last:
            return high;

        case PivotStrategy::Middle:
            return low + (high - low) / 2;

        case PivotStrategy::Random: {
            std::uniform_int_distribution<std::size_t> distribution(low, high);
            return distribution(generator);
        }

        case PivotStrategy::MedianOfThree: {
            const std::size_t middle = low + (high - low) / 2;

            std::array<std::pair<int, std::size_t>, 3> candidates = {{
                {values[low], low},
                {values[middle], middle},
                {values[high], high}
            }};

            std::sort(
                candidates.begin(),
                candidates.end(),
                [](const auto& left, const auto& right) {
                    return left.first < right.first;
                }
            );

            return candidates[1].second;
        }
    }

    throw std::invalid_argument("Unsupported pivot strategy.");
}

std::size_t lomuto_partition(
    std::vector<int>& values,
    std::size_t low,
    std::size_t high,
    SortMetrics& metrics
) {
    ++metrics.partitions;

    const int pivot = values[high];
    std::size_t boundary = low;

    for (std::size_t current = low; current < high; ++current) {
        ++metrics.comparisons;

        if (values[current] <= pivot) {
            swap_values(values, boundary, current, metrics);
            ++boundary;
        }
    }

    swap_values(values, boundary, high, metrics);
    return boundary;
}

void quick_sort_recursive_range(
    std::vector<int>& values,
    std::size_t low,
    std::size_t high,
    PivotStrategy strategy,
    SortMetrics& metrics,
    std::mt19937& generator,
    std::size_t depth
) {
    ++metrics.recursive_calls;
    metrics.max_depth = std::max(metrics.max_depth, depth);

    if (low >= high) {
        return;
    }

    const std::size_t pivot_index = choose_pivot_index(
        values,
        low,
        high,
        strategy,
        generator
    );

    swap_values(values, pivot_index, high, metrics);

    const std::size_t final_pivot = lomuto_partition(
        values,
        low,
        high,
        metrics
    );

    if (final_pivot > low) {
        quick_sort_recursive_range(
            values,
            low,
            final_pivot - 1,
            strategy,
            metrics,
            generator,
            depth + 1
        );
    }

    if (final_pivot < high) {
        quick_sort_recursive_range(
            values,
            final_pivot + 1,
            high,
            strategy,
            metrics,
            generator,
            depth + 1
        );
    }
}

SortMetrics quick_sort_recursive(
    std::vector<int>& values,
    PivotStrategy strategy
) {
    validate_input(values);

    SortMetrics metrics;

    if (values.size() < 2) {
        return metrics;
    }

    std::mt19937 generator(2026);

    quick_sort_recursive_range(
        values,
        0,
        values.size() - 1,
        strategy,
        metrics,
        generator,
        1
    );

    return metrics;
}

std::pair<std::size_t, std::size_t> three_way_partition(
    std::vector<int>& values,
    std::size_t low,
    std::size_t high,
    SortMetrics& metrics
) {
    ++metrics.partitions;

    const int pivot = values[low + (high - low) / 2];

    std::size_t less = low;
    std::size_t current = low;
    std::size_t greater = high;

    while (current <= greater) {
        ++metrics.comparisons;

        if (values[current] < pivot) {
            swap_values(values, less, current, metrics);
            ++less;
            ++current;
        } else if (values[current] > pivot) {
            swap_values(values, current, greater, metrics);

            /*
             * The swapped-in element at current has not been classified yet,
             * so current is intentionally not incremented here.
             */
            if (greater == 0) {
                break;
            }
            --greater;
        } else {
            ++current;
        }
    }

    return {less, greater};
}

void three_way_recursive(
    std::vector<int>& values,
    std::size_t low,
    std::size_t high,
    SortMetrics& metrics,
    std::size_t depth
) {
    ++metrics.recursive_calls;
    metrics.max_depth = std::max(metrics.max_depth, depth);

    if (low >= high) {
        return;
    }

    const auto [equal_start, equal_end] =
        three_way_partition(values, low, high, metrics);

    if (equal_start > low) {
        three_way_recursive(
            values,
            low,
            equal_start - 1,
            metrics,
            depth + 1
        );
    }

    if (equal_end < high) {
        three_way_recursive(
            values,
            equal_end + 1,
            high,
            metrics,
            depth + 1
        );
    }
}

SortMetrics quick_sort_three_way(std::vector<int>& values) {
    validate_input(values);

    SortMetrics metrics;

    if (values.size() < 2) {
        return metrics;
    }

    three_way_recursive(
        values,
        0,
        values.size() - 1,
        metrics,
        1
    );

    return metrics;
}

SortMetrics quick_sort_iterative(std::vector<int>& values) {
    validate_input(values);

    SortMetrics metrics;

    if (values.size() < 2) {
        return metrics;
    }

    std::vector<std::pair<std::size_t, std::size_t>> ranges;
    ranges.emplace_back(0, values.size() - 1);

    /*
     * This explicit stack replaces recursive calls. The smaller partition is
     * pushed after the larger one so that it is processed first, helping
     * control auxiliary stack growth.
     */
    while (!ranges.empty()) {
        const auto [low, high] = ranges.back();
        ranges.pop_back();

        if (low >= high) {
            continue;
        }

        const std::size_t middle = low + (high - low) / 2;
        swap_values(values, middle, high, metrics);

        const std::size_t pivot_index =
            lomuto_partition(values, low, high, metrics);

        const bool has_left = pivot_index > low;
        const bool has_right = pivot_index < high;

        if (has_left && has_right) {
            const std::size_t left_size = pivot_index - low;
            const std::size_t right_size = high - pivot_index;

            if (left_size > right_size) {
                ranges.emplace_back(low, pivot_index - 1);
                ranges.emplace_back(pivot_index + 1, high);
            } else {
                ranges.emplace_back(pivot_index + 1, high);
                ranges.emplace_back(low, pivot_index - 1);
            }
        } else if (has_left) {
            ranges.emplace_back(low, pivot_index - 1);
        } else if (has_right) {
            ranges.emplace_back(pivot_index + 1, high);
        }
    }

    return metrics;
}

void merge_ranges(
    std::vector<int>& values,
    std::vector<int>& temporary,
    std::size_t left,
    std::size_t middle,
    std::size_t right,
    SortMetrics& metrics
) {
    std::size_t left_index = left;
    std::size_t right_index = middle + 1;
    std::size_t output = left;

    while (left_index <= middle && right_index <= right) {
        ++metrics.comparisons;

        if (values[left_index] <= values[right_index]) {
            temporary[output++] = values[left_index++];
        } else {
            temporary[output++] = values[right_index++];
        }
    }

    while (left_index <= middle) {
        temporary[output++] = values[left_index++];
    }

    while (right_index <= right) {
        temporary[output++] = values[right_index++];
    }

    for (std::size_t index = left; index <= right; ++index) {
        values[index] = temporary[index];
    }
}

void merge_sort_range(
    std::vector<int>& values,
    std::vector<int>& temporary,
    std::size_t left,
    std::size_t right,
    SortMetrics& metrics,
    std::size_t depth
) {
    ++metrics.recursive_calls;
    metrics.max_depth = std::max(metrics.max_depth, depth);

    if (left >= right) {
        return;
    }

    const std::size_t middle = left + (right - left) / 2;

    merge_sort_range(
        values,
        temporary,
        left,
        middle,
        metrics,
        depth + 1
    );

    merge_sort_range(
        values,
        temporary,
        middle + 1,
        right,
        metrics,
        depth + 1
    );

    merge_ranges(
        values,
        temporary,
        left,
        middle,
        right,
        metrics
    );
}

SortMetrics merge_sort(std::vector<int>& values) {
    validate_input(values);

    SortMetrics metrics;

    if (values.size() < 2) {
        return metrics;
    }

    std::vector<int> temporary(values.size());

    merge_sort_range(
        values,
        temporary,
        0,
        values.size() - 1,
        metrics,
        1
    );

    return metrics;
}

BatchReport analyze_sorted_transactions(
    const std::vector<int>& sorted_transactions
) {
    if (sorted_transactions.empty()) {
        return {};
    }

    BatchReport report;
    report.count = sorted_transactions.size();
    report.minimum = sorted_transactions.front();
    report.maximum = sorted_transactions.back();

    const std::size_t middle = sorted_transactions.size() / 2;

    if (sorted_transactions.size() % 2 == 0) {
        report.median =
            (static_cast<double>(sorted_transactions[middle - 1]) +
             static_cast<double>(sorted_transactions[middle])) / 2.0;
    } else {
        report.median = sorted_transactions[middle];
    }

    return report;
}

void print_metrics(
    const std::string& name,
    const SortMetrics& metrics
) {
    std::cout
        << std::left
        << std::setw(24)
        << name
        << " comparisons=" << std::setw(7) << metrics.comparisons
        << " swaps=" << std::setw(6) << metrics.swaps
        << " partitions=" << std::setw(6) << metrics.partitions
        << " depth=" << std::setw(5) << metrics.max_depth
        << '\n';
}

void demonstrate_partition() {
    std::cout << "\n=== Pivot and Partition ===\n";

    std::vector<int> values = {
        29, 10, 14, 37, 13, 8, 42, 18
    };

    const std::vector<int> original = values;
    SortMetrics metrics;

    const std::size_t pivot_index =
        lomuto_partition(values, 0, values.size() - 1, metrics);

    std::cout << "Original: ";
    for (int value : original) {
        std::cout << value << ' ';
    }

    std::cout << "\nAfter:    ";
    for (int value : values) {
        std::cout << value << ' ';
    }

    std::cout << "\nPivot value: " << values[pivot_index]
              << "\nPivot index: " << pivot_index
              << "\n";

    print_metrics("partition", metrics);
}

void demonstrate_pivot_strategies() {
    std::cout << "\n=== Pivot Strategy Comparison ===\n";

    const std::vector<int> input = {
        41, 8, 29, 17, 63, 4, 52, 31, 22, 70, 11
    };

    const std::vector<std::pair<std::string, PivotStrategy>> strategies = {
        {"first", PivotStrategy::First},
        {"last", PivotStrategy::Last},
        {"middle", PivotStrategy::Middle},
        {"random", PivotStrategy::Random},
        {"median_of_three", PivotStrategy::MedianOfThree}
    };

    for (const auto& [name, strategy] : strategies) {
        std::vector<int> values = input;
        const SortMetrics metrics =
            quick_sort_recursive(values, strategy);

        print_metrics(name, metrics);

        if (!is_sorted(values)) {
            throw std::runtime_error(
                "Pivot strategy produced an incorrectly sorted array."
            );
        }
    }
}

void demonstrate_worst_case() {
    std::cout << "\n=== Worst-Case Behavior ===\n";

    constexpr std::size_t size = 300;

    std::vector<int> values(size);
    for (std::size_t index = 0; index < size; ++index) {
        values[index] = static_cast<int>(index);
    }

    const SortMetrics metrics =
        quick_sort_recursive(values, PivotStrategy::Last);

    const std::size_t expected =
        size * (size - 1) / 2;

    std::cout << "Input is already sorted.\n";
    std::cout << "Input size: " << size << '\n';
    std::cout << "Correct: " << std::boolalpha << is_sorted(values) << '\n';
    std::cout << "Observed comparisons: " << metrics.comparisons << '\n';
    std::cout << "n(n-1)/2: " << expected << '\n';
    std::cout << "Maximum recursion depth: "
              << metrics.max_depth << '\n';

    std::cout
        << "The last-element pivot is an extreme element on this input, "
        << "so each partition leaves one large unsorted side.\n";
}

void demonstrate_duplicate_handling() {
    std::cout << "\n=== Duplicate-Heavy Data ===\n";

    const std::vector<int> input = {
        5, 3, 5, 2, 5, 8, 5, 1, 3, 5,
        4, 5, 2, 5, 7, 5, 3, 5, 6, 5
    };

    std::vector<int> standard = input;
    std::vector<int> three_way = input;

    const SortMetrics standard_metrics =
        quick_sort_recursive(
            standard,
            PivotStrategy::MedianOfThree
        );

    const SortMetrics three_way_metrics =
        quick_sort_three_way(three_way);

    print_metrics("two-way quick sort", standard_metrics);
    print_metrics("three-way quick sort", three_way_metrics);

    if (standard != three_way) {
        throw std::runtime_error(
            "Two-way and three-way implementations disagree."
        );
    }

    std::cout
        << "Three-way partitioning places all values equal to the pivot "
        << "into a region that requires no further recursive sorting.\n";
}

void demonstrate_transaction_batch() {
    std::cout << "\n=== Transaction Batch Case Study ===\n";

    /*
     * These values represent transaction amounts in cents. The sort is not
     * the business result itself; it is an intermediate operation needed for
     * ordered statistics such as minimum, maximum, and median.
     */
    std::vector<int> transactions = {
        1499, 799, 2499, 1499, 5200, 1299, 799,
        9999, 2499, 1899, 5200, 1299, 749, 2499
    };

    std::cout << "Incoming transaction amounts (cents): ";
    for (int amount : transactions) {
        std::cout << amount << ' ';
    }
    std::cout << '\n';

    const SortMetrics metrics =
        quick_sort_three_way(transactions);

    if (!is_sorted(transactions)) {
        throw std::runtime_error(
            "Transaction batch failed validation after sorting."
        );
    }

    const BatchReport report =
        analyze_sorted_transactions(transactions);

    std::cout << "Sorted amounts: ";
    for (int amount : transactions) {
        std::cout << amount << ' ';
    }

    std::cout << "\nRecords: " << report.count
              << "\nMinimum cents: " << report.minimum
              << "\nMaximum cents: " << report.maximum
              << "\nMedian cents: " << std::fixed
              << std::setprecision(1)
              << report.median
              << '\n';

    print_metrics("transaction quick sort", metrics);
}

void benchmark_quick_sort_and_merge_sort() {
    std::cout << "\n=== Quick Sort vs Merge Sort ===\n";

    std::mt19937 generator(2026);
    std::uniform_int_distribution<int> distribution(-100'000, 100'000);

    std::vector<int> original(5'000);
    for (int& value : original) {
        value = distribution(generator);
    }

    std::vector<int> quick_values = original;
    std::vector<int> merge_values = original;

    const auto quick_start = std::chrono::steady_clock::now();
    const SortMetrics quick_metrics =
        quick_sort_three_way(quick_values);
    const auto quick_end = std::chrono::steady_clock::now();

    const auto merge_start = std::chrono::steady_clock::now();
    const SortMetrics merge_metrics =
        merge_sort(merge_values);
    const auto merge_end = std::chrono::steady_clock::now();

    const double quick_ms =
        std::chrono::duration<double, std::milli>(
            quick_end - quick_start
        ).count();

    const double merge_ms =
        std::chrono::duration<double, std::milli>(
            merge_end - merge_start
        ).count();

    std::cout << "Quick sort correct: "
              << std::boolalpha
              << is_sorted(quick_values)
              << '\n';

    std::cout << "Merge sort correct: "
              << std::boolalpha
              << is_sorted(merge_values)
              << '\n';

    std::cout << "Quick sort time: "
              << std::fixed << std::setprecision(3)
              << quick_ms << " ms\n";

    std::cout << "Merge sort time: "
              << std::fixed << std::setprecision(3)
              << merge_ms << " ms\n";

    print_metrics("quick sort", quick_metrics);
    print_metrics("merge sort", merge_metrics);

    std::cout
        << "Wall-clock timings vary with compiler optimization, hardware, "
        << "memory behavior, and input distribution.\n";
}

void randomized_correctness_test() {
    std::cout << "\n=== Randomized Correctness Tests ===\n";

    std::mt19937 generator(555);
    std::uniform_int_distribution<int> length_distribution(0, 100);
    std::uniform_int_distribution<int> value_distribution(-30, 30);

    for (int test_case = 0; test_case < 300; ++test_case) {
        const int length = length_distribution(generator);

        std::vector<int> input(static_cast<std::size_t>(length));

        for (int& value : input) {
            value = value_distribution(generator);
        }

        std::vector<int> expected = input;
        std::sort(expected.begin(), expected.end());

        {
            auto actual = input;
            quick_sort_recursive(
                actual,
                PivotStrategy::MedianOfThree
            );

            if (actual != expected) {
                throw std::runtime_error(
                    "Recursive quick sort failed randomized verification."
                );
            }
        }

        {
            auto actual = input;
            quick_sort_three_way(actual);

            if (actual != expected) {
                throw std::runtime_error(
                    "Three-way quick sort failed randomized verification."
                );
            }
        }

        {
            auto actual = input;
            quick_sort_iterative(actual);

            if (actual != expected) {
                throw std::runtime_error(
                    "Iterative quick sort failed randomized verification."
                );
            }
        }

        {
            auto actual = input;
            merge_sort(actual);

            if (actual != expected) {
                throw std::runtime_error(
                    "Merge sort failed randomized verification."
                );
            }
        }
    }

    std::cout
        << "300 randomized cases passed for quick sort and merge sort.\n";
}

int main() {
    try {
        std::cout << "QUICK SORT TECHNICAL CASE STUDY\n";
        std::cout << "========================================\n";

        demonstrate_partition();
        demonstrate_pivot_strategies();
        demonstrate_worst_case();
        demonstrate_duplicate_handling();
        demonstrate_transaction_batch();
        benchmark_quick_sort_and_merge_sort();
        randomized_correctness_test();

        std::cout << "\nCase study completed successfully.\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }
}
