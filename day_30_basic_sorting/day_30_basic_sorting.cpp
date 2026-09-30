#include <algorithm>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

/*
 * Basic Sorting Case Study: Inventory Reordering
 *
 * Scenario:
 * A warehouse receives a batch of inventory records and needs deterministic
 * ordering by stock level. Equal stock levels must retain their arrival order
 * when the selected algorithm is stable.
 *
 * The system compares three from-scratch algorithms:
 *   - Bubble sort
 *   - Selection sort
 *   - Insertion sort
 *
 * The case study also tracks comparisons, swaps, and writes so algorithmic
 * behavior can be observed rather than inferred only from elapsed time.
 */

struct SortStats {
    std::size_t comparisons = 0;
    std::size_t swaps = 0;
    std::size_t writes = 0;
};

struct InventoryItem {
    std::string sku;
    int stock;
    int arrivalOrder;
};

/*
 * Sorting by stock only is intentional. If two records have equal stock,
 * the comparator returns false in both directions. A stable algorithm can
 * therefore preserve their original arrival order.
 */
bool lowerStock(const InventoryItem& left, const InventoryItem& right) {
    return left.stock < right.stock;
}

template <typename T, typename Compare>
bool sortedAccordingTo(const std::vector<T>& values, Compare before) {
    for (std::size_t index = 0; index + 1 < values.size(); ++index) {
        if (before(values[index + 1], values[index])) {
            return false;
        }
    }

    return true;
}

template <typename T>
void swapTracked(
    std::vector<T>& values,
    std::size_t left,
    std::size_t right,
    SortStats& stats
) {
    if (left == right) {
        return;
    }

    std::swap(values[left], values[right]);
    ++stats.swaps;
    stats.writes += 2;
}

/*
 * Bubble sort:
 * Adjacent records are compared and exchanged when they are reversed.
 * The sorted suffix grows from the right side of the vector.
 */
template <typename T, typename Compare>
SortStats bubbleSort(std::vector<T>& values, Compare before) {
    SortStats stats;

    if (values.size() < 2) {
        return stats;
    }

    for (std::size_t end = values.size() - 1; end > 0; --end) {
        bool swapped = false;

        for (std::size_t index = 0; index < end; ++index) {
            ++stats.comparisons;

            if (before(values[index + 1], values[index])) {
                swapTracked(values, index, index + 1, stats);
                swapped = true;
            }
        }

        /*
         * No adjacent inversion means the entire vector is already ordered.
         * This optimization creates the linear best case.
         */
        if (!swapped) {
            break;
        }
    }

    return stats;
}

/*
 * Selection sort:
 * Every position is filled by finding the best remaining record. The scan
 * always occurs, so an already sorted vector still requires quadratic
 * comparisons.
 */
template <typename T, typename Compare>
SortStats selectionSort(std::vector<T>& values, Compare before) {
    SortStats stats;

    for (std::size_t position = 0; position + 1 < values.size(); ++position) {
        std::size_t selected = position;

        for (std::size_t index = position + 1;
             index < values.size();
             ++index) {
            ++stats.comparisons;

            if (before(values[index], values[selected])) {
                selected = index;
            }
        }

        if (selected != position) {
            swapTracked(values, position, selected, stats);
        }
    }

    return stats;
}

/*
 * Insertion sort:
 * The prefix [0, position) is already ordered. Larger records are shifted
 * right until the current record reaches its insertion point.
 *
 * Only a strict comparison is used. Equal-key records are not shifted past
 * one another, giving insertion sort its stable behavior.
 */
template <typename T, typename Compare>
SortStats insertionSort(std::vector<T>& values, Compare before) {
    SortStats stats;

    for (std::size_t position = 1; position < values.size(); ++position) {
        T current = values[position];
        ++stats.writes;

        std::size_t index = position;

        while (index > 0) {
            ++stats.comparisons;

            if (!before(current, values[index - 1])) {
                break;
            }

            values[index] = values[index - 1];
            ++stats.writes;
            --index;
        }

        values[index] = std::move(current);
        ++stats.writes;
    }

    return stats;
}

void printInventory(const std::vector<InventoryItem>& inventory) {
    for (const auto& item : inventory) {
        std::cout
            << std::left
            << std::setw(10) << item.sku
            << " stock=" << std::setw(3) << item.stock
            << " arrival=" << item.arrivalOrder
            << '\n';
    }
}

std::vector<std::string> equalStockOrder(
    const std::vector<InventoryItem>& inventory,
    int stock
) {
    std::vector<std::string> result;

    for (const auto& item : inventory) {
        if (item.stock == stock) {
            result.push_back(item.sku);
        }
    }

    return result;
}

/*
 * Demonstrates why stability matters in a real record-oriented system.
 *
 * If the warehouse later processes equal-stock items by arrival order,
 * replacing a stable algorithm with an unstable one can change business
 * behavior even though the primary numeric ordering remains correct.
 */
void demonstrateStability() {
    const std::vector<InventoryItem> original = {
        {"SKU-A", 20, 0},
        {"SKU-B", 10, 1},
        {"SKU-C", 20, 2},
        {"SKU-D", 5,  3},
        {"SKU-E", 20, 4}
    };

    std::cout << "\nSTABILITY CASE STUDY\n";
    std::cout << std::string(72, '-') << '\n';

    std::cout << "Original order for stock=20: ";
    for (const auto& sku : equalStockOrder(original, 20)) {
        std::cout << sku << ' ';
    }
    std::cout << '\n';

    {
        auto data = original;
        const SortStats stats = bubbleSort(data, lowerStock);

        std::cout << "\nBubble sort:\n";
        printInventory(data);
        std::cout << "Equal-stock order: ";
        for (const auto& sku : equalStockOrder(data, 20)) {
            std::cout << sku << ' ';
        }
        std::cout << "\nComparisons: " << stats.comparisons
                  << "\nSwaps: " << stats.swaps << '\n';
    }

    {
        auto data = original;
        const SortStats stats = selectionSort(data, lowerStock);

        std::cout << "\nSelection sort:\n";
        printInventory(data);
        std::cout << "Equal-stock order: ";
        for (const auto& sku : equalStockOrder(data, 20)) {
            std::cout << sku << ' ';
        }
        std::cout << "\nComparisons: " << stats.comparisons
                  << "\nSwaps: " << stats.swaps << '\n';
    }

    {
        auto data = original;
        const SortStats stats = insertionSort(data, lowerStock);

        std::cout << "\nInsertion sort:\n";
        printInventory(data);
        std::cout << "Equal-stock order: ";
        for (const auto& sku : equalStockOrder(data, 20)) {
            std::cout << sku << ' ';
        }
        std::cout << "\nComparisons: " << stats.comparisons
                  << "\nSwaps: " << stats.swaps << '\n';
    }
}

void demonstrateBasicCases() {
    const std::vector<std::pair<std::string, std::vector<int>>> cases = {
        {"empty", {}},
        {"single", {42}},
        {"duplicates", {5, 2, 5, 1, 2, 5, 3}},
        {"sorted", {1, 2, 3, 4, 5, 6}},
        {"reverse", {6, 5, 4, 3, 2, 1}},
        {"mixed", {9, 1, 7, 3, 2, 8, 4, 6, 5}}
    };

    std::cout << "BASIC SORTING CASES\n";
    std::cout << std::string(72, '=') << '\n';

    for (const auto& [name, original] : cases) {
        std::cout << "\nCase: " << name << "\n";

        for (const std::string algorithmName :
             {"Bubble sort", "Selection sort", "Insertion sort"}) {
            auto data = original;
            SortStats stats;

            if (algorithmName == "Bubble sort") {
                stats = bubbleSort(data, [](int a, int b) { return a < b; });
            } else if (algorithmName == "Selection sort") {
                stats = selectionSort(data, [](int a, int b) { return a < b; });
            } else {
                stats = insertionSort(data, [](int a, int b) { return a < b; });
            }

            if (!sortedAccordingTo(
                    data,
                    [](int a, int b) { return a < b; }
                )) {
                throw std::runtime_error(
                    algorithmName + " failed on case " + name
                );
            }

            std::cout << std::left
                      << std::setw(17) << algorithmName
                      << " comparisons=" << std::setw(4) << stats.comparisons
                      << " swaps=" << std::setw(3) << stats.swaps
                      << " writes=" << stats.writes
                      << " result=";

            for (int value : data) {
                std::cout << value << ' ';
            }
            std::cout << '\n';
        }
    }
}

/*
 * Operation counts expose the difference between the theoretical algorithms.
 * A deterministic input generator makes the experiment reproducible.
 */
void demonstrateComplexityPatterns() {
    std::cout << "\nBEST-CASE AND WORST-CASE PATTERNS\n";
    std::cout << std::string(96, '-') << '\n';

    std::cout
        << std::left
        << std::setw(17) << "Algorithm"
        << std::setw(6) << "N"
        << std::setw(20) << "Sorted comparisons"
        << std::setw(16) << "Sorted swaps"
        << std::setw(22) << "Reverse comparisons"
        << "Reverse swaps\n";

    const std::vector<std::size_t> sizes = {5, 10, 20, 40};

    for (std::size_t size : sizes) {
        std::vector<int> sorted(size);
        for (std::size_t index = 0; index < size; ++index) {
            sorted[index] = static_cast<int>(index);
        }

        auto reverse = sorted;
        std::reverse(reverse.begin(), reverse.end());

        for (const std::string algorithmName :
             {"Bubble sort", "Selection sort", "Insertion sort"}) {
            auto bestData = sorted;
            auto worstData = reverse;

            SortStats best;
            SortStats worst;

            if (algorithmName == "Bubble sort") {
                best = bubbleSort(
                    bestData,
                    [](int a, int b) { return a < b; }
                );
                worst = bubbleSort(
                    worstData,
                    [](int a, int b) { return a < b; }
                );
            } else if (algorithmName == "Selection sort") {
                best = selectionSort(
                    bestData,
                    [](int a, int b) { return a < b; }
                );
                worst = selectionSort(
                    worstData,
                    [](int a, int b) { return a < b; }
                );
            } else {
                best = insertionSort(
                    bestData,
                    [](int a, int b) { return a < b; }
                );
                worst = insertionSort(
                    worstData,
                    [](int a, int b) { return a < b; }
                );
            }

            std::cout
                << std::left
                << std::setw(17) << algorithmName
                << std::setw(6) << size
                << std::setw(20) << best.comparisons
                << std::setw(16) << best.swaps
                << std::setw(22) << worst.comparisons
                << worst.swaps
                << '\n';
        }
    }
}

/*
 * Independent randomized verification.
 *
 * std::sort is used only as the test oracle. It is not called by any of the
 * three implementations under study.
 */
void randomizedCorrectnessTest() {
    std::mt19937 generator(20260930);
    std::uniform_int_distribution<int> sizeDistribution(0, 30);
    std::uniform_int_distribution<int> valueDistribution(-20, 20);

    std::size_t tests = 0;

    for (int run = 0; run < 100; ++run) {
        const int size = sizeDistribution(generator);
        std::vector<int> original;

        for (int index = 0; index < size; ++index) {
            original.push_back(valueDistribution(generator));
        }

        auto expected = original;
        std::sort(expected.begin(), expected.end());

        {
            auto candidate = original;
            bubbleSort(candidate, [](int a, int b) { return a < b; });

            if (candidate != expected) {
                throw std::runtime_error("Bubble sort randomized test failed.");
            }
            ++tests;
        }

        {
            auto candidate = original;
            selectionSort(candidate, [](int a, int b) { return a < b; });

            if (candidate != expected) {
                throw std::runtime_error(
                    "Selection sort randomized test failed."
                );
            }
            ++tests;
        }

        {
            auto candidate = original;
            insertionSort(candidate, [](int a, int b) { return a < b; });

            if (candidate != expected) {
                throw std::runtime_error(
                    "Insertion sort randomized test failed."
                );
            }
            ++tests;
        }
    }

    std::cout << "\nRANDOMIZED CORRECTNESS\n";
    std::cout << std::string(72, '-') << '\n';
    std::cout << "Passed " << tests
              << " algorithm/input combinations.\n";
}

void demonstrateDescendingOrder() {
    const std::vector<int> original = {8, 3, 7, 4, 9, 2, 6, 1, 5};

    auto descending = [](int a, int b) {
        return a > b;
    };

    std::cout << "\nDESCENDING ORDER\n";
    std::cout << std::string(72, '-') << '\n';

    auto bubble = original;
    auto selection = original;
    auto insertion = original;

    bubbleSort(bubble, descending);
    selectionSort(selection, descending);
    insertionSort(insertion, descending);

    for (const auto& [name, data] :
         std::vector<std::pair<std::string, std::vector<int>>>{
             {"Bubble sort", bubble},
             {"Selection sort", selection},
             {"Insertion sort", insertion}
         }) {
        if (!sortedAccordingTo(data, descending)) {
            throw std::runtime_error(name + " failed descending order.");
        }

        std::cout << std::left << std::setw(17) << name << ": ";
        for (int value : data) {
            std::cout << value << ' ';
        }
        std::cout << '\n';
    }
}

int main() {
    try {
        demonstrateBasicCases();
        demonstrateDescendingOrder();
        demonstrateStability();
        demonstrateComplexityPatterns();
        randomizedCorrectnessTest();

        std::cout << "\nCOMPLEXITY REFERENCE\n";
        std::cout << std::string(72, '-') << '\n';
        std::cout
            << "Bubble sort:    best O(n), average O(n^2), worst O(n^2), "
               "stable, in-place.\n";
        std::cout
            << "Selection sort: best O(n^2), average O(n^2), worst O(n^2), "
               "unstable, in-place.\n";
        std::cout
            << "Insertion sort: best O(n), average O(n^2), worst O(n^2), "
               "stable, in-place.\n";

        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Program failed: " << error.what() << '\n';
        return 1;
    }
}
