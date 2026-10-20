#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

/*
 * Repository-independent inventory index for an application server.
 * The program contrasts chaining with open addressing under controlled collisions.
 * Expected lookup is O(1) with a well-distributed hash; worst case is O(n).
 */

class HashFunction {
public:
    static std::size_t hash(int key) {
        return static_cast<std::size_t>(static_cast<std::uint32_t>(key));
    }

    static std::size_t hash(const std::string& key) {
        // FNV-1a is used for a compact demonstration, not as a cryptographic hash.
        std::uint64_t value = 14695981039346656037ULL;
        for (unsigned char byte : key) {
            value ^= byte;
            value *= 1099511628211ULL;
        }
        return static_cast<std::size_t>(value);
    }
};

struct Metrics {
    std::size_t probes = 0;
    std::size_t collisions = 0;
    std::size_t resizes = 0;
};

template <typename K, typename V>
class ChainedTable {
    std::vector<std::vector<std::pair<K, V>>> buckets_;
    std::size_t size_ = 0;

    std::size_t index(const K& key) const {
        return HashFunction::hash(key) % buckets_.size();
    }

    void rehash(std::size_t capacity) {
        std::vector<std::pair<K, V>> entries;
        for (const auto& bucket : buckets_) {
            entries.insert(entries.end(), bucket.begin(), bucket.end());
        }
        buckets_.assign(capacity, {});
        size_ = 0;
        for (const auto& entry : entries) {
            buckets_[index(entry.first)].push_back(entry);
            ++size_;
        }
        ++metrics.resizes;
    }

public:
    Metrics metrics;

    explicit ChainedTable(std::size_t capacity = 8) {
        if (capacity == 0) {
            throw std::invalid_argument("Capacity must be positive");
        }
        buckets_.resize(capacity);
    }

    double load_factor() const {
        return static_cast<double>(size_) / buckets_.size();
    }

    void put(const K& key, const V& value) {
        auto& bucket = buckets_[index(key)];
        for (auto& entry : bucket) {
            ++metrics.probes;
            if (entry.first == key) {
                entry.second = value;
                return;
            }
            ++metrics.collisions;
        }

        if (!bucket.empty()) ++metrics.collisions;
        bucket.emplace_back(key, value);
        ++size_;

        if (load_factor() > 0.75) {
            rehash(buckets_.size() * 2);
        }
    }

    std::optional<V> get(const K& key) {
        for (const auto& entry : buckets_[index(key)]) {
            ++metrics.probes;
            if (entry.first == key) return entry.second;
        }
        return std::nullopt;
    }

    bool erase(const K& key) {
        auto& bucket = buckets_[index(key)];
        auto iterator = std::find_if(
            bucket.begin(), bucket.end(),
            [&key](const auto& entry) { return entry.first == key; }
        );
        metrics.probes += static_cast<std::size_t>(
            std::distance(bucket.begin(), iterator)
        ) + (iterator == bucket.end() ? 0 : 1);

        if (iterator == bucket.end()) return false;
        bucket.erase(iterator);
        --size_;
        return true;
    }

    std::size_t size() const { return size_; }
    std::size_t capacity() const { return buckets_.size(); }
};

template <typename K, typename V>
class OpenAddressTable {
    enum class State : unsigned char { Empty, Occupied, Deleted };

    struct Slot {
        State state = State::Empty;
        std::optional<K> key;
        std::optional<V> value;
    };

    std::vector<Slot> slots_;
    std::size_t size_ = 0;
    std::size_t deleted_ = 0;

    std::size_t index(const K& key) const {
        return HashFunction::hash(key) % slots_.size();
    }

    std::pair<std::size_t, bool> locate(const K& key) {
        std::size_t position = index(key);
        std::optional<std::size_t> first_deleted;

        for (std::size_t count = 0; count < slots_.size(); ++count) {
            ++metrics.probes;
            const Slot& slot = slots_[position];

            if (slot.state == State::Empty) {
                return {first_deleted.value_or(position), false};
            }
            if (slot.state == State::Deleted) {
                if (!first_deleted) first_deleted = position;
            } else if (slot.key == key) {
                return {position, true};
            } else {
                ++metrics.collisions;
            }

            position = (position + 1) % slots_.size();
        }

        if (first_deleted) return {*first_deleted, false};
        throw std::runtime_error("Hash table has no free slot");
    }

    void rehash(std::size_t capacity) {
        std::vector<std::pair<K, V>> entries;
        for (const auto& slot : slots_) {
            if (slot.state == State::Occupied) {
                entries.emplace_back(*slot.key, *slot.value);
            }
        }

        slots_.assign(capacity, {});
        size_ = 0;
        deleted_ = 0;
        for (const auto& entry : entries) {
            auto [position, found] = locate(entry.first);
            (void)found;
            slots_[position].state = State::Occupied;
            slots_[position].key = entry.first;
            slots_[position].value = entry.second;
            ++size_;
        }
        ++metrics.resizes;
    }

public:
    Metrics metrics;

    explicit OpenAddressTable(std::size_t capacity = 8) {
        if (capacity < 4) {
            throw std::invalid_argument("Capacity must be at least four");
        }
        slots_.resize(capacity);
    }

    double load_factor() const {
        return static_cast<double>(size_) / slots_.size();
    }

    void put(const K& key, const V& value) {
        if (static_cast<double>(size_ + deleted_ + 1) / slots_.size() > 0.65) {
            rehash(slots_.size() * 2);
        }

        auto [position, found] = locate(key);
        Slot& slot = slots_[position];

        if (found) {
            slot.value = value;
            return;
        }
        if (slot.state == State::Deleted) --deleted_;
        slot.state = State::Occupied;
        slot.key = key;
        slot.value = value;
        ++size_;
    }

    std::optional<V> get(const K& key) {
        auto [position, found] = locate(key);
        return found ? slots_[position].value : std::nullopt;
    }

    bool erase(const K& key) {
        auto [position, found] = locate(key);
        if (!found) return false;

        Slot& slot = slots_[position];
        slot.state = State::Deleted;
        slot.key.reset();
        slot.value.reset();
        --size_;
        ++deleted_;

        if (deleted_ > size_ && deleted_ > 8) {
            rehash(slots_.size());
        }
        return true;
    }

    std::size_t size() const { return size_; }
    std::size_t capacity() const { return slots_.size(); }
};

void print_metrics(const std::string& name, std::size_t capacity,
                   std::size_t size, double load, const Metrics& metrics) {
    std::cout << name << "\n"
              << "  Capacity: " << capacity << "\n"
              << "  Entries: " << size << "\n"
              << "  Load factor: " << std::fixed << std::setprecision(3)
              << load << "\n"
              << "  Probes: " << metrics.probes << "\n"
              << "  Collisions: " << metrics.collisions << "\n"
              << "  Resizes: " << metrics.resizes << "\n";
}

int main() {
    try {
        ChainedTable<int, std::string> chained(4);
        for (int key : {1, 5, 9, 13}) {
            chained.put(key, "asset-" + std::to_string(key));
        }

        auto chain_value = chained.get(9);
        if (!chain_value || *chain_value != "asset-9") {
            throw std::runtime_error("Chaining lookup validation failed");
        }
        if (!chained.erase(5) || chained.get(5).has_value()) {
            throw std::runtime_error("Chaining deletion validation failed");
        }

        OpenAddressTable<int, std::string> opened(8);
        for (int key : {1, 9, 17, 25}) {
            opened.put(key, "asset-" + std::to_string(key));
        }
        if (!opened.erase(9)) {
            throw std::runtime_error("Open-address deletion failed");
        }
        if (opened.get(17) != std::optional<std::string>("asset-17")) {
            throw std::runtime_error("Tombstone disrupted a probe chain");
        }
        opened.put(33, "asset-33");

        for (int key = 0; key < 100; ++key) {
            opened.put(key, "asset-" + std::to_string(key));
        }
        for (int key = 0; key < 100; ++key) {
            auto value = opened.get(key);
            if (!value || *value != "asset-" + std::to_string(key)) {
                throw std::runtime_error("Resize verification failed");
            }
        }

        std::cout << "All correctness checks passed.\n\n";
        print_metrics("Separate chaining", chained.capacity(), chained.size(),
                      chained.load_factor(), chained.metrics);
        std::cout << '\n';
        print_metrics("Linear probing", opened.capacity(), opened.size(),
                      opened.load_factor(), opened.metrics);

        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Failure: " << error.what() << '\n';
        return 1;
    }
}
