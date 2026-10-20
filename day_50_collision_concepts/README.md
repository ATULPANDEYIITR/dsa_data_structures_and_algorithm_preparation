# Hash Collisions and Hash-Table Performance

## Purpose

Hash tables map keys to storage locations using a hash function. They support efficient insertion, lookup, and deletion when keys are distributed reasonably across the available storage.

A **hash collision** occurs when different keys map to the same bucket or initial slot. Collisions are a normal consequence of mapping a large key space into a finite table. Correctness depends on resolving them without losing or confusing entries.

This project compares two collision-resolution strategies:

- **Separate chaining:** Each bucket stores a collection of entries that map to that bucket.
- **Open addressing:** Entries occupy slots within the table, and a probing sequence searches for an available slot when collisions occur.

The implementations also measure load factor, examine collision-heavy workloads, handle deletion, resize tables, and verify correctness.

## Core Concepts

### Hash functions and collisions

A hash function transforms a key into an integer. The table converts that integer into an index, commonly using a modulo operation:

\[
\operatorname{index}(k)=h(k)\bmod m
\]

Here, \(h(k)\) is the hash value and \(m\) is the table capacity.

Different keys can have the same index even when their hash values differ. For example, with a capacity of eight, hash values 1, 9, 17, and 25 all produce index 1.

A collision does not mean two keys are equal. The implementation must still compare the original keys to distinguish entries.

The Python and C++ implementations use reproducible demonstration hashes. Java uses `String.hashCode()`, while JavaScript uses a custom deterministic hash. The SQL implementation defines a stable hash function for reproducible experiments. These functions illustrate distribution and collision handling; they are not cryptographic hash functions.

### Separate chaining

Separate chaining stores colliding entries in the same bucket. A bucket can contain multiple distinct keys.

When inserting a key, the table searches its bucket for an existing matching key. It updates the associated value if the key exists; otherwise, it appends a new entry.

Lookup searches only the selected bucket. Deletion removes the matching entry without disturbing other entries in that bucket.

Advantages:

- The table can store more entries than it has buckets.
- Deletion is straightforward.
- High occupancy does not make insertion impossible by itself.

Trade-offs:

- Entries require additional storage for bucket collections and their elements.
- A poorly distributed hash function can produce long chains.
- Traversing a long chain increases lookup latency.

The Python implementation uses lists of key-value pairs. The C++ implementation uses vectors of pairs, while Java and JavaScript use collections of entries.

### Open addressing

Open addressing stores entries directly in an array of slots. When a collision occurs, the algorithm probes alternative slots until it finds the key or a suitable insertion position.

This project uses **linear probing**:

\[
\operatorname{slot}_i(k)=(h(k)+i)\bmod m
\]

The search examines consecutive slots, wrapping around to the beginning when necessary.

Linear probing has good memory locality because nearby entries occupy adjacent positions. Its main disadvantage is primary clustering: occupied runs grow and attract additional entries, increasing probe lengths.

The implementation distinguishes three slot states:

| State | Meaning |
|---|---|
| Empty | No entry has occupied the slot since the last rebuild. A search can stop here. |
| Occupied | The slot contains a key-value entry. |
| Deleted | The entry was removed, but the slot must not terminate a search. |

A deleted slot is called a **tombstone**. If deletion changed a slot directly to empty, lookup could stop before reaching another key that had been displaced by a collision.

Tombstones can be reused for insertion. Excessive tombstones can increase search costs, so rebuilding the table can restore a cleaner probe sequence.

### Load factor

Load factor measures occupancy relative to capacity:

\[
\alpha=\frac{n}{m}
\]

where \(n\) is the number of stored entries and \(m\) is the number of buckets or slots.

For separate chaining, the load factor can exceed one because buckets may contain multiple entries. For open addressing, the number of occupied entries cannot exceed the number of slots.

A higher load factor generally increases collision-resolution work. Open addressing is particularly sensitive because fewer empty slots remain available for terminating unsuccessful searches.

The implementations use growth thresholds of 0.75 for chaining and 0.65 for linear probing in their demonstrations. These are configurable engineering choices, not universal optimal values.

Open addressing also tracks tombstones when evaluating whether to resize. A table with many deleted slots can be expensive to search even if its live-entry load factor is low.

## Performance Characteristics

Let \(n\) be the number of entries and \(m\) the table capacity.

| Operation or property | Separate chaining | Linear probing |
|---|---|---|
| Average lookup with good distribution | Expected \(O(1+\alpha)\) | Expected \(O(1)\) at controlled occupancy |
| Worst-case lookup | \(O(n)\) | \(O(n)\) |
| Average insertion | Expected \(O(1+\alpha)\) | Expected \(O(1)\) at controlled occupancy |
| Deletion | Remove an entry from its chain | Mark the slot as deleted |
| Storage overhead | Bucket collections and entry objects | Slot states and entry storage |
| Locality | Depends on bucket representation | Often good for adjacent slots |
| Main degradation risk | Long chains | Clustering and excessive tombstones |
| Resize cost | \(O(n+m)\) for rebuilding and bucket initialization | \(O(n+m)\) for rebuilding the slot array |

The table presents expected behavior under reasonable hash distribution, not a guarantee for every workload. Repeated collisions can make operations linear in the number of entries.

For linear probing, performance deteriorates sharply as occupancy approaches full capacity. For separate chaining, high load factor can remain functional but increases expected chain traversal.

The exact cost also depends on key comparison, memory allocation, cache behavior, hash computation, and the distribution of successful versus unsuccessful searches.

## Python Implementation

The Python script defines two generic hash-map classes.

`ChainedHashMap` uses a list of buckets containing key-value pairs. It supports insertion, value replacement, lookup, deletion, iteration, load-factor calculation, and growth.

`OpenAddressHashMap` maintains separate key and value arrays. Unique sentinel objects represent empty and deleted slots, preventing confusion between a missing entry and a valid value. Its probing routine remembers the first tombstone while continuing to search for an existing key.

The script includes:

- Collision-heavy integer keys.
- Value replacement without duplicate entries.
- Deletion and unsuccessful lookup.
- Automatic resizing.
- Probe and collision counters.
- Assertions for expected behavior and edge cases.

Run it with Python 3.10 or later. It uses only the standard library.

## JavaScript Implementation

The JavaScript file complements the Python implementation through an event-driven runtime-friendly cache model.

`ChainedCache` and `LinearProbeCache` expose `set`, `get`, and `delete` operations. JavaScript `Symbol` values represent empty and deleted slots, ensuring that the sentinels cannot accidentally equal ordinary string or numeric keys.

The classes maintain operation metrics and resize their internal storage when occupancy exceeds the configured threshold. The test routine verifies deletion, collision-chain preservation, and behavior after growth.

The demonstration runs directly under Node.js without external packages. Its deterministic hash supports reproducible experiments, but production applications should select a hash strategy appropriate to their key types and threat model.

## C++17 Implementation

The C++ program models an inventory index for an application server.

`ChainedTable` and `OpenAddressTable` use templates so their storage logic is not restricted to one value type. Lookup returns `std::optional`, distinguishing a missing key from a successful lookup.

The open-addressing implementation represents each slot with an explicit state and optional key-value fields. Its bounded probing loop prevents an infinite search if no available slot exists.

The program measures probes, collisions, and resize events. It verifies lookup and deletion behavior before executing a larger workload to exercise resizing.

The integer hash is deterministic, and the string hash uses FNV-1a for demonstration. FNV-1a is not a cryptographic defense against deliberate collision attacks. Production services processing untrusted keys should assess their hash implementation, input limits, memory usage, and denial-of-service risks.

Compile with a C++17-compatible compiler.

## Java 17 Implementation

The Java implementation models an enterprise cache registry with explicit domain types.

`CachePolicy` is a record that validates capacity and load-factor requirements. `ResolutionStrategy` distinguishes the two supported collision-resolution approaches, while `CacheMetrics` records probes, collisions, and resizing events.

The `CacheStore` interface defines a shared operational contract. `ChainedStore` and `ProbingStore` implement the contract using different storage mechanisms. `CacheEntry` validates entry keys and values at construction time.

The demonstration tests key replacement, missing entries, deletion, tombstone behavior, and larger workloads that trigger resizing. It also verifies that invalid keys are rejected.

Java's `String.hashCode()` provides a convenient deterministic hash for the example, but it is not designed to resist adversarial collision attacks. A production enterprise cache should consider concurrency requirements, memory limits, key normalization, observability, and the security characteristics of its input data.

Compile and run the public class with Java 17 or later.

## PostgreSQL Implementation

The SQL script represents hash-table behavior using relational tables and stored functions.

### Relational model

| Table | Purpose |
|---|---|
| `hash_table_configs` | Stores strategy, capacity, and load-factor policy. |
| `hash_buckets` | Represents individual bucket or slot states. |
| `hash_entries` | Stores keys, JSONB values, hash codes, and assigned buckets. |
| `hash_operation_log` | Records operations and their measured probe and collision counts. |

Primary keys, foreign keys, unique constraints, and check constraints protect relational integrity. Indexes support bucket-based access and hash-code analysis.

The `demo_hash_key` function produces repeatable hash values. `create_hash_table` creates a logical table and its initial buckets. The insertion, lookup, and deletion functions demonstrate strategy-specific behavior, while the reporting view aggregates occupancy and load factor.

The sample workload inserts colliding keys into both strategies, looks up an existing entry, deletes a key from the open-addressing table, inserts another colliding key, and queries operation metrics. A nested exception block demonstrates how duplicate-key failure can be handled without aborting the enclosing transaction.

### SQL model limitations

This schema is an educational logical model, not an implementation of PostgreSQL's native hash index internals.

The separate-chaining branch records a threshold warning rather than automatically rebuilding and redistributing all existing entries. The open-addressing branch models tombstones and bounded probing. A production-grade implementation would need a complete, concurrency-safe resize procedure, careful locking, and comprehensive reconciliation of bucket states.

The schema also illustrates an important distinction: a relational database's unique constraint protects logical key uniqueness independently of collision-resolution strategy.

Execute the script in PostgreSQL 14 or later. The transaction ensures that schema creation and the included workload are committed together if execution completes successfully.

## Operational Considerations

### Hash quality and adversarial input

A poor hash distribution concentrates entries in a small number of buckets or slots. Predictable hashes can also expose applications to deliberate collision attacks.

A production design should consider keyed hashing where appropriate, validate input size, limit memory consumption, and monitor unusual collision rates. A deterministic demonstration hash should not be treated as a security boundary.

### Resizing and latency

Resizing requires allocating new storage and reinserting existing entries. This is typically linear in the number of entries, with additional cost for initializing capacity.

Amortized insertion performance can remain efficient across many operations, but an individual resize can cause a latency spike. Systems with strict latency requirements may need incremental rehashing or capacity planning.

### Deletion correctness

Chaining removes entries without affecting other keys in the same bucket. Open addressing requires tombstones or a correct cluster-repair algorithm. Clearing a displaced entry's slot directly to empty can make later entries unreachable.

### Metrics and testing

Probe counts and collision counts provide useful evidence about distribution, but they are not direct measurements of elapsed time. Benchmarking should use representative keys, realistic operation mixes, multiple table sizes, and consistent runtime conditions.

Correctness tests should cover empty tables, missing keys, duplicate insertion, collisions, wraparound probing, repeated deletion, resizing, and recovery after deletion. A fast hash table is not useful if its collision-handling rules lose entries or return incorrect values.
