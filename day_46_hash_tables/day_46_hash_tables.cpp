#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <list>
#include <optional>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

template <typename Key, typename Value, typename Hash = std::hash<Key>>
class ChainedHashTable {
private:
    struct Entry {
        Key key;
        Value value;
    };

    std::vector<std::list<Entry>> buckets_;
    std::size_t size_ = 0;
    double maximumLoadFactor_;
    Hash hash_;

    std::size_t bucketIndex(const Key& key) const {
        return hash_(key) % buckets_.size();
    }

    void rehash(std::size_t newCapacity) {
        if (newCapacity == 0) {
            throw std::invalid_argument("Capacity must be positive");
        }

        std::vector<std::list<Entry>> replacement(newCapacity);

        // Allocate the new bucket array before modifying the existing table.
        // Moving entries prevents copies of values when possible.
        for (auto& bucket : buckets_) {
            for (auto& entry : bucket) {
                const auto index = hash_(entry.key) % newCapacity;
                replacement[index].push_back(std::move(entry));
            }
        }

        buckets_.swap(replacement);
    }

public:
    explicit ChainedHashTable(
        std::size_t capacity = 8,
        double maximumLoadFactor = 0.75,
        Hash hash = Hash{})
        : buckets_(capacity),
          maximumLoadFactor_(maximumLoadFactor),
          hash_(std::move(hash)) {
        if (capacity == 0) {
            throw std::invalid_argument("Capacity must be positive");
        }
        if (!std::isfinite(maximumLoadFactor_) ||
            maximumLoadFactor_ <= 0.0) {
            throw std::invalid_argument(
                "Maximum load factor must be finite and positive");
        }
    }

    std::size_t size() const noexcept {
        return size_;
    }

    std::size_t capacity() const noexcept {
        return buckets_.size();
    }

    double loadFactor() const noexcept {
        return static_cast<double>(size_) / buckets_.size();
    }

    void insertOrAssign(const Key& key, Value value) {
        auto& bucket = buckets_[bucketIndex(key)];

        for (auto& entry : bucket) {
            if (entry.key == key) {
                entry.value = std::move(value);
                return;
            }
        }

        // Growth keeps average bucket length bounded under good hashing.
        if (static_cast<double>(size_ + 1) / buckets_.size()
            > maximumLoadFactor_) {
            if (buckets_.size() >
                std::numeric_limits<std::size_t>::max() / 2) {
                throw std::length_error("Hash table capacity overflow");
            }
            rehash(buckets_.size() * 2);
        }

        buckets_[bucketIndex(key)].push_back({key, std::move(value)});
        ++size_;
    }

    std::optional<std::reference_wrapper<const Value>>
    find(const Key& key) const {
        const auto& bucket = buckets_[bucketIndex(key)];

        for (const auto& entry : bucket) {
            if (entry.key == key) {
                return std::cref(entry.value);
            }
        }

        return std::nullopt;
    }

    bool erase(const Key& key) {
        auto& bucket = buckets_[bucketIndex(key)];

        for (auto iterator = bucket.begin(); iterator != bucket.end();
             ++iterator) {
            if (iterator->key == key) {
                bucket.erase(iterator);
                --size_;
                return true;
            }
        }

        return false;
    }

    std::vector<std::size_t> bucketLengths() const {
        std::vector<std::size_t> lengths;
        lengths.reserve(buckets_.size());

        for (const auto& bucket : buckets_) {
            lengths.push_back(bucket.size());
        }

        return lengths;
    }

    bool validate() const {
        std::size_t observed = 0;

        for (std::size_t index = 0; index < buckets_.size(); ++index) {
            for (const auto& entry : buckets_[index]) {
                if (bucketIndex(entry.key) != index) {
                    return false;
                }
                ++observed;
            }
        }

        return observed == size_;
    }
};

// Every key intentionally hashes to the same bucket, exposing worst-case
// behavior without relying on an accidental collision.
struct ConstantHash {
    std::size_t operator()(const std::string&) const noexcept {
        return 3;
    }
};

struct Deployment {
    std::string service;
    std::string environment;
    std::string version;
    bool healthy;
};

int main() {
    try {
        std::cout << "=== Deployment registry ===\n";

        // A composite string key identifies a service in an environment.
        ChainedHashTable<std::string, Deployment> registry(4);

        const std::vector<Deployment> deployments{
            {"payments", "production", "3.4.1", true},
            {"identity", "production", "2.8.0", true},
            {"payments", "staging", "3.5.0-rc1", false},
            {"search", "production", "1.9.2", true},
            {"billing", "production", "4.1.0", true},
        };

        for (const auto& deployment : deployments) {
            const std::string key =
                deployment.service + "@" + deployment.environment;
            registry.insertOrAssign(key, deployment);
        }

        registry.insertOrAssign(
            "payments@production",
            Deployment{"payments", "production", "3.4.2", true});

        const auto production = registry.find("payments@production");

        if (production) {
            const Deployment& deployment = production->get();
            std::cout << deployment.service << " "
                      << deployment.version << " healthy="
                      << std::boolalpha << deployment.healthy << '\n';
        }

        std::cout << "Registry size: " << registry.size() << '\n';
        std::cout << "Bucket capacity: " << registry.capacity() << '\n';
        std::cout << "Load factor: " << std::fixed << std::setprecision(3)
                  << registry.loadFactor() << '\n';

        const bool deleted = registry.erase("payments@staging");
        std::cout << "Staging record deleted: " << deleted << '\n';
        std::cout << "Registry invariants valid: "
                  << registry.validate() << '\n';

        // A missing lookup has an explicit empty result instead of an
        // ambiguous default value.
        if (!registry.find("unknown@production")) {
            std::cout << "Unknown deployment was not found.\n";
        }

        std::cout << "\n=== Collision stress case ===\n";

        ChainedHashTable<std::string, int, ConstantHash> collisions(8);

        for (int id = 0; id < 6; ++id) {
            collisions.insertOrAssign("record-" + std::to_string(id), id);
        }

        const auto lengths = collisions.bucketLengths();
        std::cout << "Bucket lengths:";
        for (std::size_t length : lengths) {
            std::cout << ' ' << length;
        }
        std::cout << '\n';

        const auto collisionValue = collisions.find("record-4");
        if (collisionValue) {
            std::cout << "Collision-chain lookup: "
                      << collisionValue->get() << '\n';
        }

        collisions.erase("record-2");
        std::cout << "After deletion, record-4 remains: "
                  << static_cast<bool>(collisions.find("record-4")) << '\n';

        std::cout << "Collision table valid: "
                  << collisions.validate() << '\n';

        std::cout << "\n=== Standard unordered_map comparison ===\n";

        std::unordered_map<std::string, Deployment> standardRegistry;
        for (const auto& deployment : deployments) {
            standardRegistry[
                deployment.service + "@" + deployment.environment
            ] = deployment;
        }

        std::cout << "Standard container size: "
                  << standardRegistry.size() << '\n';
        std::cout << "Standard container load factor: "
                  << standardRegistry.load_factor() << '\n';

        // unordered_map provides a production-quality general-purpose
        // implementation. Custom tables are useful when bucket behavior,
        // memory layout, or collision strategies need explicit control.
    } catch (const std::exception& error) {
        std::cerr << "Registry failure: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
