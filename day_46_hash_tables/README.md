# Hash Tables: Key-Value Storage, Buckets, and Lookup Performance

## Technical scope

A hash table stores associations between keys and values. A key identifies an entry, while the associated value contains the data retrieved through that key. Hash tables are widely used for service registries, caches, configuration stores, frequency counters, indexes, and in-memory lookup structures.

The central operation is to transform a key into a hash value and use that value to select a bucket. The bucket identifies where an entry should be stored or searched for. Since different keys can produce the same bucket index, a correct implementation must resolve collisions rather than assume every key maps to a unique location.

This repository examines hash tables through five complementary implementations: Python provides a dynamically resized table with explicit invariants, JavaScript explores `Map` semantics and asynchronous request deduplication, C++ models a deployment registry, Java uses domain-specific service identities, and PostgreSQL represents bucket placement and lookup measurements relationally.

## Key-value storage and hash functions

A key-value entry is a logical association such as `payments@production → 3.4.1`. The key must support the equality rules expected by the data structure. A hash function computes an integer from the key, and the bucket index is derived from that integer and the current capacity.

For a nonnegative hash value and capacity \(m\), a common bucket-selection rule is

\[
\operatorname{bucket}(k)=h(k)\bmod m
\]

The hash function and bucket-selection rule serve different purposes. The hash function distributes keys across an integer space. The modulo operation maps that space into the finite bucket array.

Changing the capacity changes bucket indices, even when keys and hash values remain unchanged. A resize therefore requires existing entries to be redistributed.

A hash function does not need to produce a unique value for every key. Instead, it should distribute typical keys effectively, while the implementation must always distinguish keys using equality.

### Key equality and immutability

Keys that compare equal must have equal hash values. If an object's equality-relevant state changes after insertion, a hash table may no longer be able to locate the entry at the bucket originally selected for it.

Immutable keys avoid this problem. Composite identities can use immutable tuples in Python, records in Java, or a dedicated key type in C++. JavaScript `Map` permits object keys, but object keys are compared by identity rather than by the equality of their properties.

Hash values should not be treated as permanent identifiers. Python string hashes may differ across processes, and capacity changes alter bucket placement independently of the key's hash.

## Buckets and collision resolution

A bucket represents the entries associated with a bucket index. The implementations distinguish the logical key from its physical bucket.

Python, C++, and the conceptual JavaScript table use separate chaining. Each bucket contains a collection of entries. A lookup selects the relevant bucket, examines its entries, and returns the value only when a matching key is found.

Separate chaining has several useful properties:

- Multiple keys can occupy the same bucket without overwriting one another.
- Deletion removes a matching entry from its bucket.
- Lookup cost depends on the number of entries examined in the selected bucket.
- A poor hash function can create long chains even when the overall table contains relatively few entries.

Open addressing is an alternative collision-resolution strategy. It stores entries directly in an array and searches other slots when the initial position is occupied. Its deletion behavior requires particular care because simply clearing a slot can interrupt a probe sequence. The implementations in this repository use separate chaining to make collision handling and deletion behavior explicit.

## Lookup, insertion, and deletion

A lookup hashes the key, identifies a bucket, and compares candidate keys. A missing key must be distinguishable from a stored value such as zero, an empty string, or `None`.

Insertion has two possible outcomes. If the key already exists, its value is updated. Otherwise, a new entry is added and the entry count increases. The Python and C++ implementations preserve this distinction.

Deletion searches the selected bucket and removes the matching entry. Deleting a nonexistent key is handled explicitly: Python raises `KeyError`, the C++ table returns `false`, and the JavaScript model returns `false`.

The expected cost of these operations depends on hash distribution and load factor. The load factor is

\[
\alpha=\frac{n}{m}
\]

where \(n\) is the number of entries and \(m\) is the number of buckets.

For separate chaining, the load factor represents the average number of entries per bucket. Keeping it within a chosen threshold can reduce typical bucket traversal costs. It does not guarantee constant-time behavior when a hash function creates severe collisions.

## Python implementation

The Python script begins with built-in dictionaries and then implements a generic `HashTable` using a list of buckets. Each bucket is a list of `Entry` objects containing a key and value.

The custom table supports:

- `__getitem__` and `__setitem__` for dictionary-style access.
- `get` for lookups with a default value.
- `__contains__` for membership testing.
- `__delitem__` for deletion with missing-key detection.
- `items` and `__iter__` for traversal.
- `bucket_lengths` for inspecting collision distribution.
- `validate` for checking bucket placement, uniqueness, and entry counts.

The `_resize` method creates a new bucket array and redistributes every existing entry. It does not merely change the capacity number, because doing so would leave entries in incorrect buckets.

The collision demonstration uses a custom key class whose instances all return the same hash. This forces multiple distinct keys into one bucket and confirms that equality, not the hash value alone, determines which entry is retrieved.

Frequency counting illustrates a practical application. Each event name maps to its current count, so an update replaces repeated scanning of the entire event list with repeated dictionary operations.

The benchmark measures lookup behavior for a fixed workload. Its output is observational rather than a universal performance guarantee. Timing depends on the interpreter, hardware, key distribution, and system load.

## JavaScript implementation

The JavaScript file distinguishes plain objects from `Map`.

A plain object stores properties under string or symbol property names. When an ordinary object is used as a property key, it is converted to a property name, so distinct objects may unexpectedly address the same property. A `Map` supports arbitrary key types and distinguishes object keys by identity.

The custom `ChainedHashTable` demonstrates a separate-chaining model with an explicit bucket array. Its deterministic polynomial hash makes bucket selection reproducible for the example, but it is not intended as a secure hash function or a replacement for the runtime's built-in `Map`.

The event aggregation example stores a small metrics object for each service. The implementation uses `Map` to associate service identifiers with mutable aggregate values and validates status codes before updating counters.

The asynchronous request-deduplication example illustrates another use of a key-value structure. An in-flight request map associates an account identifier with a pending promise. Concurrent callers for the same identifier can share that promise instead of initiating duplicate work.

The `finally` block removes the pending promise after completion. The identity check prevents an older operation from accidentally deleting a different promise stored under the same key.

This pattern requires careful cache-lifetime decisions in production. A permanent response cache needs expiration, invalidation, and failure policies. An in-flight request map serves a different purpose because its entries exist only while operations are pending.

## C++ deployment registry case study

The C++ program models deployments across services and environments. A composite key such as `payments@production` identifies a deployment, while the value stores the service name, environment, version, and health state.

The `ChainedHashTable` template separates storage mechanics from the deployment domain. It uses a vector of linked-list buckets, tracks entry count and capacity, supports lookup and deletion, and grows the table when the configured load-factor threshold is exceeded.

Lookup returns an `std::optional` containing a reference wrapper. This makes absence explicit without requiring a special deployment value to represent failure.

The registry updates an existing version without creating a duplicate key. Its invariant checker verifies that each entry resides in the bucket selected by its key and that the observed entry count matches the maintained count.

A custom constant hash function deliberately sends every key to the same bucket. This exposes the worst-case behavior of separate chaining: lookup and insertion can require linear traversal when the chain grows with the number of entries.

The program also compares the custom implementation with `std::unordered_map`, which provides a standard general-purpose hash table. A custom implementation is useful for studying memory layout, collision strategies, or domain-specific constraints, but a production system should generally prefer a well-tested standard container unless there is a measurable reason not to.

## Java enterprise registry

The Java program models deployments through `ServiceKey`, `Deployment`, and `DeploymentRegistry`.

`ServiceKey` is a record with a service name and environment. Its generated equality and hash-code behavior makes independently constructed keys with equal normalized components equivalent in a `HashMap`.

The `Deployment` class separates identity from mutable deployment state. It validates versions and revision numbers, supports version upgrades, and rejects stale updates using an expected revision. This models a common enterprise requirement: an update should not silently overwrite a change based on outdated state.

State transitions are explicit. A retired deployment cannot be reactivated, and invalid transitions from the registered state are rejected. These rules are domain constraints rather than responsibilities of the hash table itself.

The registry uses `putIfAbsent` to prevent duplicate deployment registration and `Optional` to represent a potentially missing entry. A snapshot copies the map structure, but it is not deeply immutable because the contained deployment objects remain mutable.

The aggregation example uses `Map.merge` to maintain environment counts. A `TreeMap` is used only for deterministic display, since `HashMap` does not guarantee iteration order.

The distinction between identity and hash values remains essential. Equal keys must have equal hash codes, while unequal keys may legitimately share the same hash code. `HashMap` resolves collisions internally and checks key equality before returning a matching entry.

## PostgreSQL relational model

The SQL script creates a dedicated `hash_table_lab` schema.

`hash_tables` stores table metadata, including capacity, entry count, and the configured maximum load factor. `hash_entries` stores the logical key, value, computed demonstration hash, and current bucket index. A unique constraint on `(table_id, key_text)` prevents duplicate logical keys within one table.

The schema deliberately does not impose uniqueness on the hash value or bucket index. Several keys may legitimately share either value. Enforcing uniqueness on those columns would incorrectly reject collisions.

`lookup_events` records operations, whether lookups succeeded, and how many entries were examined in the selected bucket. This supports workload analysis without confusing a hash collision with a matching key.

The `demo_hash_key` function provides a deterministic educational hash. It is not a cryptographic hash and is not intended for hostile input. `bucket_for_key` maps that value to the current capacity.

Triggers maintain the stored hash and bucket index when entries are inserted or updated. Another trigger maintains the entry count after deletion. The `unique_key_per_table` constraint remains the final authority against duplicate keys.

`record_lookup` records lookup results and a bucket-scan measurement. `bucket_occupancy` includes empty buckets, which makes the distribution visible rather than reporting only buckets that contain entries. `bucket_statistics` exposes load factor and occupancy metrics.

`resize_hash_table` changes the capacity and redistributes the entries. The operation is executed within the surrounding transaction so the script can demonstrate a coherent database workflow.

The SQL demonstration also uses `INSERT ... ON CONFLICT` to update an existing value without inserting a duplicate logical key. A savepoint and exception handler demonstrate how a uniqueness violation can be handled without leaving the invalid row in the table.

The SQL model is an educational representation of hash-table behavior, not a replacement for PostgreSQL's internal hash structures. Its stored bucket indices are application-level data maintained by the script.

## Average-case performance and complexity

For a well-distributed hash function, typical hash-table operations have expected constant-time cost under an appropriate load factor.

| Operation | Expected cost | Worst-case cost for separate chaining |
|---|---|---|
| Lookup | \(O(1)\) | \(O(n)\) |
| Insert without resize | \(O(1)\) | \(O(n)\) |
| Delete | \(O(1)\) | \(O(n)\) |
| Resize and redistribute | \(O(n)\) | \(O(n)\) for the entries being moved |
| Traverse all entries | \(O(n+m)\) | \(O(n+m)\) |

Here, \(n\) is the number of entries and \(m\) is the bucket capacity. A full bucket scan or complete table traversal cannot be constant time because it must examine the relevant entries.

Resizing occasionally requires a linear-time operation. With geometric growth, the cost of repeated resizing can be amortized across many insertions, producing expected amortized constant-time insertion under suitable hash-distribution assumptions.

These are expected or amortized bounds, not unconditional guarantees. Poor hash distribution, adversarial keys, expensive equality comparisons, and excessive collisions can increase operation costs substantially.

## Edge cases and implementation limits

An empty table needs positive capacity before modulo-based bucket selection can occur. The Python and C++ implementations reject zero capacity.

An empty string, numeric zero, or `None` may be a valid stored value. Code should test key presence separately from the truthiness of the retrieved value.

A missing key is not the same as a stored value equal to a default. Use explicit membership checks, optional return values, or a dedicated missing-value sentinel where necessary.

A hash function should be consistent with the key's equality rules. If equal keys can produce different hashes, a lookup may fail even though an equal key is present.

A high load factor does not automatically mean that the table is defective. Its effect depends on the collision strategy, memory layout, key distribution, and workload. Separate chaining tolerates load factors above one, while open-addressed tables generally need unused slots to support probing.

## Security, correctness, and production behavior

Hash tables are not inherently secure against adversarial key distributions. An attacker who can force many keys into the same bucket may degrade performance. Untrusted inputs should be validated, and the chosen implementation should have suitable collision defenses for its threat model.

Hash values are not authentication tokens or stable identifiers. A hash collision is not proof that two values are equal, and a hash alone should not be used to authorize access to a record.

Concurrent access requires synchronization or a thread-safe data structure when multiple operations can modify the same table. The sample implementations are designed for sequential execution. Atomic updates, resize coordination, and memory visibility need explicit treatment in concurrent systems.

Performance measurements should use representative keys and query distributions. A benchmark that measures only successful lookups does not describe the cost of misses, insertion, deletion, resizing, or collision-heavy workloads.

The central engineering principle is that a hash table provides efficient key-based access when its hashing, equality, collision handling, capacity management, and mutation rules remain consistent. Those mechanisms are separate responsibilities, and correctness depends on their interaction.
