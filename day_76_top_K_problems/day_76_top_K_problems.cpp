#include <algorithm>
#include <cassert>
#include <cmath>
#include <functional>
#include <iostream>
#include <limits>
#include <queue>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;

class SelectionError : public invalid_argument {
public:
    explicit SelectionError(const string& message)
        : invalid_argument(message) {}
};

void validateK(int k, int n, bool allowZero = false) {
    int minimum = allowZero ? 0 : 1;

    if (k < minimum || k > n) {
        throw SelectionError("Invalid k");
    }
}

class TopKEngine {
private:
    mt19937 generator;

public:
    TopKEngine() : generator(random_device{}()) {}

    int kthLargest(const vector<int>& values, int k) const {
        validateK(k, static_cast<int>(values.size()));

        priority_queue<
            int,
            vector<int>,
            greater<int>
        > heap;

        for (int value : values) {
            heap.push(value);

            if (static_cast<int>(heap.size()) > k) {
                heap.pop();
            }
        }

        return heap.top();
    }

    int kthSmallest(const vector<int>& values, int k) const {
        validateK(k, static_cast<int>(values.size()));

        priority_queue<int> heap;

        for (int value : values) {
            heap.push(value);

            if (static_cast<int>(heap.size()) > k) {
                heap.pop();
            }
        }

        return heap.top();
    }

    int quickselectLargest(vector<int> values, int k) {
        validateK(k, static_cast<int>(values.size()));

        const int target = k - 1;
        int left = 0;
        int right = static_cast<int>(values.size()) - 1;

        while (left <= right) {
            uniform_int_distribution<int> distribution(left, right);
            int pivot = values[distribution(generator)];

            int low = left;
            int current = left;
            int high = right;

            while (current <= high) {
                if (values[current] > pivot) {
                    swap(values[current], values[low]);
                    current++;
                    low++;
                } else if (values[current] < pivot) {
                    swap(values[current], values[high]);
                    high--;
                } else {
                    current++;
                }
            }

            if (target < low) {
                right = low - 1;
            } else if (target > high) {
                left = high + 1;
            } else {
                return values[target];
            }
        }

        throw runtime_error("Quickselect failed");
    }

    vector<int> topKFrequent(
        const vector<int>& values,
        int k
    ) const {
        unordered_map<int, int> frequency;

        for (int value : values) {
            frequency[value]++;
        }

        validateK(k, static_cast<int>(frequency.size()), true);

        // Pair order: frequency, value.
        using Entry = pair<int, int>;

        // The heap root is the least desirable retained entry.
        auto compare = [](const Entry& a, const Entry& b) {
            if (a.first != b.first) {
                return a.first > b.first;
            }

            return a.second < b.second;
        };

        priority_queue<Entry, vector<Entry>, decltype(compare)>
            heap(compare);

        for (const auto& [value, count] : frequency) {
            heap.push({count, value});

            if (static_cast<int>(heap.size()) > k) {
                heap.pop();
            }
        }

        vector<int> result;

        while (!heap.empty()) {
            result.push_back(heap.top().second);
            heap.pop();
        }

        sort(result.begin(), result.end(), [&](int a, int b) {
            if (frequency[a] != frequency[b]) {
                return frequency[a] > frequency[b];
            }

            return a < b;
        });

        return result;
    }

    vector<int> kClosestElements(
        const vector<int>& values,
        int k,
        int target
    ) const {
        if (!is_sorted(values.begin(), values.end())) {
            throw SelectionError("Input must be sorted");
        }

        validateK(k, static_cast<int>(values.size()), true);

        if (k == 0) {
            return {};
        }

        int left = 0;
        int right = static_cast<int>(values.size()) - k;

        // Find the optimal contiguous window of size k.
        while (left < right) {
            int middle = left + (right - left) / 2;

            long long leftDistance =
                static_cast<long long>(target) - values[middle];

            long long rightDistance =
                static_cast<long long>(values[middle + k]) - target;

            if (leftDistance > rightDistance) {
                left = middle + 1;
            } else {
                right = middle;
            }
        }

        return vector<int>(
            values.begin() + left,
            values.begin() + left + k
        );
    }
};

void runTests(TopKEngine& engine) {
    vector<int> values = {3, 2, 1, 5, 6, 4};

    assert(engine.kthLargest(values, 2) == 5);
    assert(engine.kthSmallest(values, 2) == 2);
    assert(engine.quickselectLargest(values, 2) == 5);

    vector<int> frequencies = {1, 1, 1, 2, 2, 3};
    vector<int> frequent = engine.topKFrequent(frequencies, 2);

    assert((frequent == vector<int>{1, 2}));

    vector<int> sorted = {1, 2, 3, 4, 5};
    vector<int> closest = engine.kClosestElements(sorted, 4, 3);

    assert((closest == vector<int>{1, 2, 3, 4}));

    assert(engine.topKFrequent({}, 0).empty());
    assert(engine.kClosestElements(sorted, 0, 3).empty());

    bool rejected = false;

    try {
        engine.kthLargest(values, 10);
    } catch (const SelectionError&) {
        rejected = true;
    }

    assert(rejected);
}

int main() {
    try {
        TopKEngine engine;

        cout << "TOP-K GOVERNANCE AND SELECTION ENGINE\n";
        cout << "=====================================\n";

        vector<int> values = {3, 2, 1, 5, 6, 4};

        cout << "Input: ";

        for (int value : values) {
            cout << value << " ";
        }

        cout << "\n";

        cout << "Second largest: "
             << engine.kthLargest(values, 2) << "\n";

        cout << "Third smallest: "
             << engine.kthSmallest(values, 3) << "\n";

        cout << "Second largest using Quickselect: "
             << engine.quickselectLargest(values, 2) << "\n";

        vector<int> data = {1, 1, 1, 2, 2, 3, 4, 4, 4, 4};

        cout << "Top two frequent: ";

        for (int value : engine.topKFrequent(data, 2)) {
            cout << value << " ";
        }

        cout << "\n";

        vector<int> sorted = {1, 2, 3, 4, 5};

        cout << "Four closest to 3: ";

        for (int value : engine.kClosestElements(sorted, 4, 3)) {
            cout << value << " ";
        }

        cout << "\n\n";

        runTests(engine);

        cout << "All tests passed.\n";

    } catch (const exception& error) {
        cerr << "Error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
