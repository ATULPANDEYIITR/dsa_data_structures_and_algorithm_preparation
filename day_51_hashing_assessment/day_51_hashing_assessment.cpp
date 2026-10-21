#include <algorithm>
#include <cstdint>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

class HashingAssessment {
public:
    static unordered_map<long long, size_t>
    frequencyCounts(const vector<long long>& values) {
        unordered_map<long long, size_t> counts;
        counts.reserve(values.size());

        for (long long value : values) {
            ++counts[value];
        }
        return counts;
    }

    static vector<long long> findDuplicates(const vector<long long>& values) {
        unordered_set<long long> seen;
        unordered_set<long long> reported;
        vector<long long> duplicates;

        seen.reserve(values.size());
        reported.reserve(values.size());

        for (long long value : values) {
            if (seen.count(value) && !reported.count(value)) {
                duplicates.push_back(value);
                reported.insert(value);
            }
            seen.insert(value);
        }
        return duplicates;
    }

    static pair<size_t, size_t> twoSum(
        const vector<long long>& values, long long target) {
        unordered_map<long long, size_t> earliest;
        earliest.reserve(values.size());

        for (size_t index = 0; index < values.size(); ++index) {
            // Avoid signed overflow when calculating target - value.
            const long long value = values[index];
            if ((value > 0 && target < numeric_limits<long long>::min() + value) ||
                (value < 0 && target > numeric_limits<long long>::max() + value)) {
                if (!earliest.count(value)) earliest.emplace(value, index);
                continue;
            }

            const long long complement = target - value;
            auto match = earliest.find(complement);
            if (match != earliest.end()) {
                return {match->second, index};
            }
            earliest.emplace(value, index);
        }

        throw runtime_error("No pair sums to the requested target");
    }

    static uint64_t countSubarraysWithSum(
        const vector<long long>& values, long long target) {
        // Prefix arithmetic is checked to avoid undefined signed overflow.
        unordered_map<long long, uint64_t> prefixFrequency;
        prefixFrequency.reserve(values.size() + 1);
        prefixFrequency[0] = 1;

        long long prefixSum = 0;
        uint64_t total = 0;

        for (long long value : values) {
            if ((value > 0 && prefixSum > numeric_limits<long long>::max() - value) ||
                (value < 0 && prefixSum < numeric_limits<long long>::min() - value)) {
                throw overflow_error("Prefix sum overflow");
            }
            prefixSum += value;

            long long wanted;
            bool representable = true;

            if ((target < 0 &&
                 prefixSum > numeric_limits<long long>::max() + target) ||
                (target > 0 &&
                 prefixSum < numeric_limits<long long>::min() + target)) {
                representable = false;
            }

            if (representable) {
                wanted = prefixSum - target;
                auto found = prefixFrequency.find(wanted);
                if (found != prefixFrequency.end()) {
                    if (numeric_limits<uint64_t>::max() - total < found->second) {
                        throw overflow_error("Subarray count overflow");
                    }
                    total += found->second;
                }
            }

            auto& count = prefixFrequency[prefixSum];
            if (count == numeric_limits<uint64_t>::max()) {
                throw overflow_error("Prefix frequency overflow");
            }
            ++count;
        }

        return total;
    }

    static size_t longestConsecutiveSequence(const vector<long long>& values) {
        unordered_set<long long> unique(values.begin(), values.end());
        size_t longest = 0;

        for (long long value : unique) {
            // Guard the minimum integer before subtracting one.
            if (value != numeric_limits<long long>::min() &&
                unique.count(value - 1)) {
                continue;
            }

            size_t length = 1;
            long long current = value;

            while (current != numeric_limits<long long>::max() &&
                   unique.count(current + 1)) {
                ++current;
                ++length;
            }

            longest = max(longest, length);
        }

        return longest;
    }

    static uint64_t stringHash(const string& text) {
        constexpr uint64_t base = 257;
        constexpr uint64_t modulus = 1000000007;
        uint64_t hash = 0;

        // Hash bytes consistently; this does not guarantee collision freedom.
        for (unsigned char character : text) {
            hash = (hash * base + character) % modulus;
        }
        return hash;
    }

    static vector<vector<string>>
    groupStringsByVerifiedHash(const vector<string>& values) {
        unordered_map<uint64_t, vector<vector<string>>> buckets;

        for (const string& value : values) {
            auto& groups = buckets[stringHash(value)];
            auto matching = find_if(
                groups.begin(), groups.end(),
                [&](const vector<string>& group) {
                    return group.front() == value;
                });

            if (matching == groups.end()) {
                groups.push_back({value});
            } else {
                matching->push_back(value);
            }
        }

        vector<vector<string>> result;
        for (auto& entry : buckets) {
            for (auto& group : entry.second) {
                result.push_back(move(group));
            }
        }
        return result;
    }
};

void require(bool condition, const string& name) {
    if (!condition) {
        throw runtime_error("Assessment failed: " + name);
    }
    cout << "PASS | " << name << '\n';
}

int main() {
    try {
        const vector<long long> values{1, 2, 2, 3, 1, 2};
        const auto frequencies = HashingAssessment::frequencyCounts(values);
        require(frequencies.at(1) == 2 && frequencies.at(2) == 3 &&
                frequencies.at(3) == 1, "frequency counting");

        require(HashingAssessment::findDuplicates({4, 2, 4, 2, 4}) ==
                vector<long long>({4, 2}), "duplicate detection");

        require(HashingAssessment::twoSum({3, -2, 7, 5}, 3) ==
                pair<size_t, size_t>(1, 2), "two-sum lookup");

        bool missingPairRejected = false;
        try {
            HashingAssessment::twoSum({1, 2}, 9);
        } catch (const runtime_error&) {
            missingPairRejected = true;
        }
        require(missingPairRejected, "missing pair failure");

        require(HashingAssessment::countSubarraysWithSum({1, -1, 0}, 0) == 3,
                "prefix sum with negative values");

        require(HashingAssessment::countSubarraysWithSum({}, 0) == 0,
                "empty prefix-sum input");

        require(HashingAssessment::longestConsecutiveSequence(
                    {100, 4, 200, 1, 3, 2}) == 4,
                "longest consecutive sequence");

        require(HashingAssessment::stringHash("branch") ==
                HashingAssessment::stringHash("branch"),
                "deterministic string hash");

        const auto groups = HashingAssessment::groupStringsByVerifiedHash(
            {"cat", "dog", "cat"});
        size_t catOccurrences = 0;
        size_t dogOccurrences = 0;
        for (const auto& group : groups) {
            if (group.front() == "cat") catOccurrences = group.size();
            if (group.front() == "dog") dogOccurrences = group.size();
        }
        require(catOccurrences == 2 && dogOccurrences == 1,
                "hash bucket equality verification");

        cout << "\nAll assessment checks passed.\n";
        return 0;
    } catch (const exception& error) {
        cerr << "ERROR: " << error.what() << '\n';
        return 1;
    }
}
