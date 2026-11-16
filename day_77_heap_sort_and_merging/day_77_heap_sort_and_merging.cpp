#include <algorithm>
#include <chrono>
#include <cstddef>
#include <fstream>
#include <functional>
#include <iostream>
#include <limits>
#include <queue>
#include <random>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace std;

enum class MergeStrategy {
    HEAP,
    PAIRWISE
};

struct MergeStatistics {
    size_t sourceCount = 0;
    size_t totalElements = 0;
    double elapsedMilliseconds = 0.0;
};

struct MergeResult {
    vector<int> values;
    MergeStatistics statistics;
};

class HeapAlgorithms {
private:
    static void siftDown(
        vector<int>& values,
        size_t root,
        size_t heapSize
    ) {
        while (true) {
            size_t largest = root;
            size_t left = 2 * root + 1;
            size_t right = 2 * root + 2;

            if (
                left < heapSize &&
                values[left] > values[largest]
            ) {
                largest = left;
            }

            if (
                right < heapSize &&
                values[right] > values[largest]
            ) {
                largest = right;
            }

            if (largest == root) {
                break;
            }

            swap(values[root], values[largest]);
            root = largest;
        }
    }

    static void validateSortedLists(
        const vector<vector<int>>& lists
    ) {
        for (size_t source = 0; source < lists.size(); ++source) {
            if (!is_sorted(lists[source].begin(), lists[source].end())) {
                throw invalid_argument(
                    "Input sequence " + to_string(source) +
                    " is not sorted."
                );
            }
        }
    }

public:
    /*
     * Heap sort:
     * 1. Build a max heap.
     * 2. Repeatedly move the maximum to the final position.
     * 3. Restore the heap in the remaining prefix.
     */
    static vector<int> heapSort(
        vector<int> values,
        bool descending = false
    ) {
        const size_t n = values.size();

        if (n < 2) {
            return values;
        }

        // Bottom-up construction: O(n).
        for (int i = static_cast<int>(n / 2) - 1; i >= 0; --i) {
            siftDown(values, static_cast<size_t>(i), n);
        }

        // Extraction: O(n log n).
        for (size_t end = n - 1; end > 0; --end) {
            swap(values[0], values[end]);
            siftDown(values, 0, end);
        }

        if (descending) {
            reverse(values.begin(), values.end());
        }

        return values;
    }

    static vector<int> mergeTwo(
        const vector<int>& left,
        const vector<int>& right
    ) {
        if (!is_sorted(left.begin(), left.end()) ||
            !is_sorted(right.begin(), right.end())) {
            throw invalid_argument("Both inputs must be sorted.");
        }

        vector<int> result;
        result.reserve(left.size() + right.size());

        size_t i = 0;
        size_t j = 0;

        while (i < left.size() && j < right.size()) {
            if (left[i] <= right[j]) {
                result.push_back(left[i++]);
            } else {
                result.push_back(right[j++]);
            }
        }

        result.insert(
            result.end(),
            left.begin() + static_cast<ptrdiff_t>(i),
            left.end()
        );

        result.insert(
            result.end(),
            right.begin() + static_cast<ptrdiff_t>(j),
            right.end()
        );

        return result;
    }

    /*
     * Min-heap entries contain:
     * value, source index, position inside the source.
     *
     * Only one active value per source is maintained.
     */
    static vector<int> mergeKHeap(
        const vector<vector<int>>& lists
    ) {
        validateSortedLists(lists);

        using Entry = tuple<int, size_t, size_t>;

        priority_queue<
            Entry,
            vector<Entry>,
            greater<Entry>
        > minHeap;

        size_t total = 0;

        for (size_t source = 0; source < lists.size(); ++source) {
            total += lists[source].size();

            if (!lists[source].empty()) {
                minHeap.emplace(
                    lists[source][0],
                    source,
                    0
                );
            }
        }

        vector<int> result;
        result.reserve(total);

        while (!minHeap.empty()) {
            auto [value, source, position] = minHeap.top();
            minHeap.pop();

            result.push_back(value);

            const size_t nextPosition = position + 1;

            if (nextPosition < lists[source].size()) {
                minHeap.emplace(
                    lists[source][nextPosition],
                    source,
                    nextPosition
                );
            }
        }

        if (result.size() != total) {
            throw runtime_error("Merge element-count invariant failed.");
        }

        return result;
    }

    /*
     * Balanced pairwise multiway merge.
     */
    static vector<int> mergeKPairwise(
        const vector<vector<int>>& lists
    ) {
        validateSortedLists(lists);

        vector<vector<int>> current = lists;

        if (current.empty()) {
            return {};
        }

        while (current.size() > 1) {
            vector<vector<int>> nextRound;
            nextRound.reserve((current.size() + 1) / 2);

            for (size_t i = 0; i < current.size(); i += 2) {
                if (i + 1 < current.size()) {
                    nextRound.push_back(
                        mergeTwo(current[i], current[i + 1])
                    );
                } else {
                    nextRound.push_back(move(current[i]));
                }
            }

            current = move(nextRound);
        }

        return move(current.front());
    }

    static MergeResult merge(
        const vector<vector<int>>& lists,
        MergeStrategy strategy
    ) {
        auto start = chrono::steady_clock::now();

        vector<int> output;

        if (strategy == MergeStrategy::HEAP) {
            output = mergeKHeap(lists);
        } else {
            output = mergeKPairwise(lists);
        }

        auto finish = chrono::steady_clock::now();

        double elapsed = chrono::duration<double, milli>(
            finish - start
        ).count();

        MergeStatistics statistics{
            lists.size(),
            output.size(),
            elapsed
        };

        return {move(output), statistics};
    }

    /*
     * External-style sorting.
     * Each chunk is sorted independently and then merged.
     */
    static vector<int> externalMergeSort(
        const vector<int>& values,
        size_t chunkSize
    ) {
        if (chunkSize == 0) {
            throw invalid_argument("Chunk size must be positive.");
        }

        vector<vector<int>> chunks;

        for (size_t i = 0; i < values.size(); i += chunkSize) {
            size_t end = min(values.size(), i + chunkSize);

            vector<int> chunk(
                values.begin() + static_cast<ptrdiff_t>(i),
                values.begin() + static_cast<ptrdiff_t>(end)
            );

            chunks.push_back(heapSort(move(chunk)));
        }

        return mergeKHeap(chunks);
    }
};

class RepositoryMergeEngine {
private:
    vector<vector<int>> sources;
    vector<bool> registered;
    bool finalized = false;

public:
    explicit RepositoryMergeEngine(size_t expectedSources)
        : sources(expectedSources),
          registered(expectedSources, false) {
        if (expectedSources == 0) {
            throw invalid_argument(
                "At least one source is required."
            );
        }
    }

    void registerSource(
        size_t sourceId,
        const vector<int>& sortedValues
    ) {
        if (finalized) {
            throw logic_error("Merge engine is finalized.");
        }

        if (sourceId >= sources.size()) {
            throw out_of_range("Invalid source identifier.");
        }

        if (registered[sourceId]) {
            throw logic_error("Source already registered.");
        }

        if (!is_sorted(sortedValues.begin(), sortedValues.end())) {
            throw invalid_argument("Source must be sorted.");
        }

        sources[sourceId] = sortedValues;
        registered[sourceId] = true;
    }

    bool ready() const {
        return all_of(
            registered.begin(),
            registered.end(),
            [](bool value) {
                return value;
            }
        );
    }

    vector<int> finalize() {
        if (finalized) {
            throw logic_error("Merge already finalized.");
        }

        if (!ready()) {
            throw logic_error("Not all sources have registered.");
        }

        vector<int> result = HeapAlgorithms::mergeKHeap(sources);

        finalized = true;

        return result;
    }
};

static void printVector(
    const string& label,
    const vector<int>& values
) {
    cout << label << ": ";

    for (size_t i = 0; i < values.size(); ++i) {
        if (i != 0) {
            cout << ", ";
        }

        cout << values[i];
    }

    cout << '\n';
}

static void runTests() {
    cout << "HEAP SORT\n";

    vector<int> values = {
        45, 12, 89, 3, 67, 21, 90, 4, 45
    };

    printVector("Original", values);

    vector<int> sorted = HeapAlgorithms::heapSort(values);
    printVector("Sorted", sorted);

    vector<int> expected = values;
    sort(expected.begin(), expected.end());

    if (sorted != expected) {
        throw runtime_error("Heap sort test failed.");
    }

    vector<int> descending = HeapAlgorithms::heapSort(
        values,
        true
    );

    reverse(expected.begin(), expected.end());

    if (descending != expected) {
        throw runtime_error("Descending sort test failed.");
    }

    cout << "\nK-WAY MERGE\n";

    vector<vector<int>> lists = {
        {1, 4, 7, 10},
        {2, 5, 8, 11},
        {3, 6, 9, 12},
        {0, 13, 15}
    };

    MergeResult heapResult = HeapAlgorithms::merge(
        lists,
        MergeStrategy::HEAP
    );

    MergeResult pairwiseResult = HeapAlgorithms::merge(
        lists,
        MergeStrategy::PAIRWISE
    );

    printVector("Heap merge", heapResult.values);
    printVector("Pairwise merge", pairwiseResult.values);

    if (heapResult.values != pairwiseResult.values) {
        throw runtime_error("Merge implementations disagree.");
    }

    cout << "Heap merge time: "
         << heapResult.statistics.elapsedMilliseconds
         << " ms\n";

    cout << "\nEDGE CASES\n";

    vector<vector<vector<int>>> cases = {
        {},
        {{}},
        {{}, {}, {}},
        {{1, 1, 1}, {1, 1}, {1}},
        {{-10, -5}, {-8, 0}, {2, 3}}
    };

    for (const auto& test : cases) {
        printVector(
            "Result",
            HeapAlgorithms::mergeKHeap(test)
        );
    }

    try {
        HeapAlgorithms::mergeKHeap({
            {1, 5, 3},
            {2, 4}
        });

        throw runtime_error("Unsorted input was accepted.");
    } catch (const invalid_argument& error) {
        cout << "Validation correctly rejected input: "
             << error.what() << '\n';
    }

    cout << "\nMULTI-SOURCE COORDINATION\n";

    RepositoryMergeEngine engine(3);

    engine.registerSource(0, {1, 4, 7});
    engine.registerSource(1, {2, 5, 8});
    engine.registerSource(2, {3, 6, 9});

    if (!engine.ready()) {
        throw runtime_error("Merge engine readiness failed.");
    }

    printVector("Coordinated result", engine.finalize());

    cout << "\nEXTERNAL-STYLE MERGE SORT\n";

    vector<int> externalInput = {
        19, 4, 7, 2, 15, 1, 8, 3, 11, 6
    };

    vector<int> externalSorted =
        HeapAlgorithms::externalMergeSort(externalInput, 3);

    printVector("External result", externalSorted);

    vector<int> builtin = externalInput;
    sort(builtin.begin(), builtin.end());

    if (externalSorted != builtin) {
        throw runtime_error("External merge sort failed.");
    }

    cout << "\nAll C++17 checks passed.\n";
}

int main() {
    try {
        runTests();
        return 0;
    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }
}
