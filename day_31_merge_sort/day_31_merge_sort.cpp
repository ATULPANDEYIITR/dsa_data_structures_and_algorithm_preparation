/*
 * Merge Sort Case Study
 *
 * Scenario:
 * A data-processing service receives transaction records that must be
 * ordered by transaction amount before a downstream reconciliation stage.
 *
 * The program implements a repository-style sorting engine without using
 * std::sort. It demonstrates:
 *
 * - Divide-and-conquer decomposition
 * - Recursive splitting
 * - Stable merging
 * - Custom comparison
 * - Auxiliary storage
 * - Bottom-up merge sort
 * - Inversion counting
 * - Validation
 * - Failure handling
 * - Complexity instrumentation
 *
 * Standard: C++17
 */

#include <algorithm>
#include <cstddef>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

struct SortMetrics {
    std::size_t comparisons = 0;
    std::size_t merges = 0;
    std::size_t split_operations = 0;
};

struct Transaction {
    long long transaction_id;
    std::string account;
    long long amount_cents;
    std::size_t original_position;
};

std::ostream& operator<<(std::ostream& output, const Transaction& transaction) {
    output << "TX-" << transaction.transaction_id
           << " account=" << transaction.account
           << " amount=" << transaction.amount_cents << " cents"
           << " original_position=" << transaction.original_position;
    return output;
}

void validate_numeric_input(const std::vector<long long>& values) {
    /*
     * The vector itself guarantees memory-safe indexing through its size,
     * while this validation establishes the application-level contract.
     * There is no NaN/Infinity issue because long long is integral.
     */
    if (values.size() >
        static_cast<std::size_t>(std::numeric_limits<std::ptrdiff_t>::max())) {
        throw std::invalid_argument("Input is too large for index arithmetic.");
    }
}

template <typename T, typename Compare>
void merge_ranges(
    std::vector<T>& values,
    std::vector<T>& buffer,
    std::size_t left,
    std::size_t middle,
    std::size_t right,
    Compare compare,
    SortMetrics& metrics
) {
    std::size_t left_index = left;
    std::size_t right_index = middle + 1;
    std::size_t output_index = left;

    while (left_index <= middle && right_index <= right) {
        ++metrics.comparisons;

        /*
         * compare(a, b) means "a should appear before b".
         *
         * If neither a < b nor b < a, the keys are equivalent. Selecting
         * from the left half preserves stability.
         */
        if (!compare(values[right_index], values[left_index])) {
            buffer[output_index] = values[left_index];
            ++left_index;
        } else {
            buffer[output_index] = values[right_index];
            ++right_index;
        }

        ++output_index;
    }

    while (left_index <= middle) {
        buffer[output_index] = values[left_index];
        ++left_index;
        ++output_index;
    }

    while (right_index <= right) {
        buffer[output_index] = values[right_index];
        ++right_index;
        ++output_index;
    }

    for (std::size_t index = left; index <= right; ++index) {
        values[index] = std::move(buffer[index]);
    }

    ++metrics.merges;
}

template <typename T, typename Compare>
void merge_sort_recursive(
    std::vector<T>& values,
    Compare compare,
    SortMetrics& metrics
) {
    if (values.size() < 2) {
        return;
    }

    std::vector<T> buffer(values.size());

    std::function<void(std::size_t, std::size_t)> sort_range =
        [&](std::size_t left, std::size_t right) {
            if (left >= right) {
                return;
            }

            /*
             * This formulation avoids left + right overflow, which matters
             * when indices approach the maximum representable value.
             */
            const std::size_t middle =
                left + (right - left) / 2;

            ++metrics.split_operations;

            sort_range(left, middle);
            sort_range(middle + 1, right);

            /*
             * If the two boundary elements are already ordered, the entire
             * combined range is ordered because each half is sorted.
             */
            ++metrics.comparisons;

            if (!compare(values[middle + 1], values[middle])) {
                return;
            }

            merge_ranges(
                values,
                buffer,
                left,
                middle,
                right,
                compare,
                metrics
            );
        };

    sort_range(0, values.size() - 1);
}

template <typename T, typename Compare>
void merge_sort_bottom_up(
    std::vector<T>& values,
    Compare compare
) {
    if (values.size() < 2) {
        return;
    }

    std::vector<T> buffer(values.size());

    /*
     * width represents the size of each already-sorted run.
     * Runs grow as 1, 2, 4, 8, ... until they cover the input.
     */
    for (std::size_t width = 1; width < values.size();) {
        std::size_t left = 0;

        while (left < values.size()) {
            const std::size_t middle =
                std::min(left + width - 1, values.size() - 1);

            if (middle == values.size() - 1) {
                break;
            }

            const std::size_t remaining =
                values.size() - middle - 1;

            const std::size_t right =
                middle + std::min(width, remaining);

            SortMetrics unused_metrics;

            merge_ranges(
                values,
                buffer,
                left,
                middle,
                right,
                compare,
                unused_metrics
            );

            if (right == values.size() - 1) {
                break;
            }

            left = right + 1;
        }

        /*
         * Guard against integer overflow when doubling width.
         */
        if (width > values.size() / 2) {
            break;
        }

        width *= 2;
    }
}

std::size_t count_inversions(const std::vector<long long>& input) {
    if (input.empty()) {
        return 0;
    }

    std::vector<long long> values = input;
    std::vector<long long> buffer(values.size());

    std::function<std::size_t(std::size_t, std::size_t)> count_range =
        [&](std::size_t left, std::size_t right) -> std::size_t {
            if (left >= right) {
                return 0;
            }

            const std::size_t middle =
                left + (right - left) / 2;

            std::size_t inversions =
                count_range(left, middle) +
                count_range(middle + 1, right);

            std::size_t left_index = left;
            std::size_t right_index = middle + 1;
            std::size_t output_index = left;

            while (left_index <= middle &&
                   right_index <= right) {
                if (values[left_index] <= values[right_index]) {
                    buffer[output_index] = values[left_index];
                    ++left_index;
                } else {
                    buffer[output_index] = values[right_index];

                    /*
                     * Every remaining element in the left half is greater
                     * than values[right_index], producing this many
                     * inversions at once.
                     */
                    inversions += middle - left_index + 1;

                    ++right_index;
                }

                ++output_index;
            }

            while (left_index <= middle) {
                buffer[output_index] = values[left_index];
                ++left_index;
                ++output_index;
            }

            while (right_index <= right) {
                buffer[output_index] = values[right_index];
                ++right_index;
                ++output_index;
            }

            for (std::size_t index = left; index <= right; ++index) {
                values[index] = buffer[index];
            }

            return inversions;
        };

    return count_range(0, values.size() - 1);
}

template <typename T>
void print_vector(
    const std::vector<T>& values,
    const std::string& label
) {
    std::cout << label << ": [";

    for (std::size_t index = 0; index < values.size(); ++index) {
        if (index != 0) {
            std::cout << ", ";
        }

        std::cout << values[index];
    }

    std::cout << "]\n";
}

void demonstrate_transaction_sorting() {
    std::vector<Transaction> transactions = {
        {1001, "ACC-17", 12500, 0},
        {1002, "ACC-04", 7500, 1},
        {1003, "ACC-17", 12500, 2},
        {1004, "ACC-09", 3200, 3},
        {1005, "ACC-04", 7500, 4},
        {1006, "ACC-12", 18400, 5}
    };

    /*
     * The comparator orders transactions by amount only. Since merge_sort
     * preserves equivalent records from left to right, transaction 1001
     * remains before 1003, and 1002 remains before 1005.
     */
    const auto by_amount = [](
        const Transaction& first,
        const Transaction& second
    ) {
        return first.amount_cents < second.amount_cents;
    };

    SortMetrics metrics;
    merge_sort_recursive(transactions, by_amount, metrics);

    std::cout << "\nTransaction reconciliation case study:\n";

    for (const auto& transaction : transactions) {
        std::cout << "  " << transaction << '\n';
    }

    std::cout << "\nMetrics:\n"
              << "  comparisons       = " << metrics.comparisons << '\n'
              << "  merges            = " << metrics.merges << '\n'
              << "  split operations  = " << metrics.split_operations << '\n';

    if (
        transactions[1].transaction_id != 1002 ||
        transactions[2].transaction_id != 1005
    ) {
        throw std::logic_error(
            "Stable ordering invariant failed for equal transaction amounts."
        );
    }
}

void verify_numeric_sort() {
    const std::vector<std::vector<long long>> cases = {
        {},
        {1},
        {2, 1},
        {1, 2, 3, 4},
        {5, 5, 5},
        {9, -2, 7, 0, -8, 4},
        {10, 9, 8, 7, 6, 5, 4, 3, 2, 1}
    };

    const auto ascending = [](
        long long first,
        long long second
    ) {
        return first < second;
    };

    for (const auto& input : cases) {
        std::vector<long long> recursive_result = input;
        SortMetrics metrics;

        merge_sort_recursive(
            recursive_result,
            ascending,
            metrics
        );

        std::vector<long long> expected = input;
        std::sort(expected.begin(), expected.end());

        if (recursive_result != expected) {
            throw std::logic_error(
                "Recursive merge sort verification failed."
            );
        }

        std::vector<long long> iterative_result = input;
        merge_sort_bottom_up(iterative_result, ascending);

        if (iterative_result != expected) {
            throw std::logic_error(
                "Bottom-up merge sort verification failed."
            );
        }
    }

    std::mt19937 generator(42);
    std::uniform_int_distribution<long long> distribution(-1000, 1000);

    for (int trial = 0; trial < 100; ++trial) {
        std::vector<long long> input;

        for (int index = 0; index < 100; ++index) {
            input.push_back(distribution(generator));
        }

        std::vector<long long> expected = input;
        std::sort(expected.begin(), expected.end());

        SortMetrics metrics;
        merge_sort_recursive(input, ascending, metrics);

        if (input != expected) {
            throw std::logic_error(
                "Randomized verification failed."
            );
        }
    }

    std::cout << "\nVerification: all C++ sorting tests passed.\n";
}

void demonstrate_inversion_counting() {
    const std::vector<long long> input = {2, 4, 1, 3, 5};

    const std::size_t inversions = count_inversions(input);

    std::cout << "\nInversion-counting extension:\n";
    print_vector(input, "  input");
    std::cout << "  inversions = " << inversions << '\n';

    if (inversions != 3) {
        throw std::logic_error(
            "Inversion count verification failed."
        );
    }
}

void demonstrate_complexity() {
    const auto ascending = [](
        long long first,
        long long second
    ) {
        return first < second;
    };

    std::cout << "\nComplexity measurements:\n";

    for (const std::size_t size : {8U, 16U, 32U, 64U, 128U}) {
        std::vector<long long> input;

        for (std::size_t index = 0; index < size; ++index) {
            input.push_back(
                static_cast<long long>(size - index)
            );
        }

        SortMetrics metrics;
        merge_sort_recursive(input, ascending, metrics);

        std::cout << "  n=" << std::setw(3) << size
                  << " comparisons=" << std::setw(6)
                  << metrics.comparisons
                  << " merges=" << std::setw(4)
                  << metrics.merges
                  << " splits=" << std::setw(4)
                  << metrics.split_operations
                  << '\n';
    }

    std::cout
        << "\nThe recurrence is T(n) = 2T(n/2) + O(n).\n"
        << "The two recursive calls create the two sorted halves.\n"
        << "The merge scans those halves once, contributing O(n) work per level.\n"
        << "There are O(log n) balanced levels, producing O(n log n) time.\n"
        << "The auxiliary merge buffer requires O(n) additional storage.\n";
}

void demonstrate_edge_cases() {
    const auto ascending = [](
        long long first,
        long long second
    ) {
        return first < second;
    };

    std::vector<long long> empty;
    SortMetrics empty_metrics;

    merge_sort_recursive(empty, ascending, empty_metrics);

    if (!empty.empty()) {
        throw std::logic_error("Empty input should remain empty.");
    }

    std::vector<long long> one_value = {42};
    SortMetrics single_metrics;

    merge_sort_recursive(
        one_value,
        ascending,
        single_metrics
    );

    if (one_value != std::vector<long long>{42}) {
        throw std::logic_error(
            "Single-element input should remain unchanged."
        );
    }

    std::vector<long long> duplicates = {
        7, 7, 7, 7, 7
    };

    SortMetrics duplicate_metrics;
    merge_sort_recursive(
        duplicates,
        ascending,
        duplicate_metrics
    );

    if (
        duplicates !=
        std::vector<long long>{7, 7, 7, 7, 7}
    ) {
        throw std::logic_error(
            "Duplicate handling failed."
        );
    }

    std::cout << "\nEdge-case validation passed.\n";
}

int main() {
    try {
        std::cout << "MERGE SORT GOVERNED DATA PIPELINE\n";
        std::cout << "=================================\n";

        demonstrate_transaction_sorting();

        const std::vector<long long> sample = {
            38, 27, 43, 3, 9, 82, 10
        };

        std::vector<long long> sorted = sample;
        SortMetrics metrics;

        const auto ascending = [](
            long long first,
            long long second
        ) {
            return first < second;
        };

        merge_sort_recursive(
            sorted,
            ascending,
            metrics
        );

        std::cout << "\nCore merge sort example:\n";
        print_vector(sample, "  before");
        print_vector(sorted, "  after");

        std::vector<long long> bottom_up = sample;
        merge_sort_bottom_up(bottom_up, ascending);

        print_vector(
            bottom_up,
            "  bottom-up result"
        );

        demonstrate_inversion_counting();
        demonstrate_edge_cases();
        verify_numeric_sort();
        demonstrate_complexity();

        std::cout << "\nCase-study properties:\n"
                  << "  Divide: split a range around its midpoint.\n"
                  << "  Conquer: recursively sort both halves.\n"
                  << "  Combine: stable merge of the sorted halves.\n"
                  << "  Time: O(n log n) for balanced merge sort.\n"
                  << "  Auxiliary space: O(n) for the merge buffer.\n"
                  << "  Stability: preserved when equivalent keys prefer the left half.\n";

        return 0;
    }
    catch (const std::exception& error) {
        std::cerr
            << "Program failed safely: "
            << error.what()
            << '\n';

        return 1;
    }
}
