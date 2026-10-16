#!/usr/bin/env python3
"""Hash tables: key/value storage, hashing, buckets, collision handling, and performance."""

from __future__ import annotations

from dataclasses import dataclass
from collections import Counter
from typing import Generic, Hashable, Iterable, Iterator, TypeVar
import math
import random
import time

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


def demonstrate_dictionary_basics() -> None:
    print("\n=== Python dictionary fundamentals ===")
    inventory = {
        "SSD-1TB": 24,
        "RAM-16GB": 48,
        "GPU-MID": 12,
    }

    inventory["SSD-1TB"] = 26
    inventory["CPU-8C"] = 15

    print("Inventory:", inventory)
    print("GPU quantity:", inventory.get("GPU-MID", 0))
    print("Unknown item:", inventory.get("MONITOR", 0))

    removed = inventory.pop("RAM-16GB", None)
    print("Removed quantity:", removed)
    print("Current keys:", list(inventory))
    print("Contains CPU:", "CPU-8C" in inventory)


def demonstrate_hash_properties() -> None:
    print("\n=== Hash function and key requirements ===")
    keys = ["SSD-1TB", "RAM-16GB", "GPU-MID", "SSD-1TB"]

    for key in keys:
        print(f"{key!r}: hash={hash(key)}")

    first = ("warehouse-1", 42)
    second = ("warehouse-1", 42)
    print("Equal keys:", first == second)
    print("Equal hashes:", hash(first) == hash(second))

    # Hash values can differ between Python processes because string hashing
    # is randomized. Never persist hash(key) as a permanent identifier.


@dataclass
class Entry(Generic[K, V]):
    key: K
    value: V


class HashTable(Generic[K, V]):
    """Separate-chaining hash table with dynamic resizing."""

    def __init__(
        self,
        capacity: int = 8,
        max_load_factor: float = 0.75,
    ) -> None:
        if capacity < 1:
            raise ValueError("Capacity must be positive")
        if not math.isfinite(max_load_factor) or max_load_factor <= 0:
            raise ValueError("Load factor threshold must be finite and positive")

        self._buckets: list[list[Entry[K, V]]] = [
            [] for _ in range(capacity)
        ]
        self._size = 0
        self._max_load_factor = max_load_factor

    def _index(self, key: K) -> int:
        # Python normalizes negative modulo results, keeping the index valid.
        return hash(key) % len(self._buckets)

    def _find_entry(self, key: K) -> Entry[K, V] | None:
        for entry in self._buckets[self._index(key)]:
            if entry.key == key:
                return entry
        return None

    def __len__(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        return len(self._buckets)

    @property
    def load_factor(self) -> float:
        return self._size / self.capacity

    def __contains__(self, key: object) -> bool:
        try:
            hash(key)
        except TypeError:
            return False
        return self._find_entry(key) is not None

    def __getitem__(self, key: K) -> V:
        entry = self._find_entry(key)
        if entry is None:
            raise KeyError(key)
        return entry.value

    def get(self, key: K, default: V | None = None) -> V | None:
        entry = self._find_entry(key)
        return default if entry is None else entry.value

    def __setitem__(self, key: K, value: V) -> None:
        # Updating an existing key must not increase the entry count.
        entry = self._find_entry(key)
        if entry is not None:
            entry.value = value
            return

        if (self._size + 1) / self.capacity > self._max_load_factor:
            self._resize(self.capacity * 2)

        self._buckets[self._index(key)].append(Entry(key, value))
        self._size += 1

    def __delitem__(self, key: K) -> None:
        bucket = self._buckets[self._index(key)]

        for position, entry in enumerate(bucket):
            if entry.key == key:
                del bucket[position]
                self._size -= 1
                return

        raise KeyError(key)

    def _resize(self, new_capacity: int) -> None:
        old_entries = [
            entry
            for bucket in self._buckets
            for entry in bucket
        ]

        self._buckets = [[] for _ in range(new_capacity)]

        # Rehash every entry because its bucket index depends on capacity.
        for entry in old_entries:
            self._buckets[self._index(entry.key)].append(entry)

    def __iter__(self) -> Iterator[K]:
        for bucket in self._buckets:
            for entry in bucket:
                yield entry.key

    def items(self) -> Iterator[tuple[K, V]]:
        for bucket in self._buckets:
            for entry in bucket:
                yield entry.key, entry.value

    def bucket_lengths(self) -> list[int]:
        return [len(bucket) for bucket in self._buckets]

    def validate(self) -> bool:
        observed = 0
        seen: set[K] = set()

        for index, bucket in enumerate(self._buckets):
            for entry in bucket:
                observed += 1
                if self._index(entry.key) != index:
                    raise AssertionError("Entry stored in the wrong bucket")
                if entry.key in seen:
                    raise AssertionError("Duplicate key detected")
                seen.add(entry.key)

        if observed != self._size:
            raise AssertionError("Entry count does not match table size")

        return True


class DeliberatelyCollidingKey:
    """Test key whose instances all produce the same hash."""

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier

    def __hash__(self) -> int:
        return 7

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, DeliberatelyCollidingKey)
            and self.identifier == other.identifier
        )

    def __repr__(self) -> str:
        return f"CollisionKey({self.identifier!r})"


def demonstrate_custom_table() -> None:
    print("\n=== Custom hash table ===")
    table: HashTable[str, int] = HashTable(capacity=4)

    for key, value in [
        ("ticket-1001", 1200),
        ("ticket-1002", 1800),
        ("ticket-1003", 950),
        ("ticket-1004", 2100),
        ("ticket-1005", 1650),
    ]:
        table[key] = value

    table["ticket-1001"] = 1250

    print("Entries:", sorted(table.items()))
    print("Ticket value:", table["ticket-1001"])
    print("Missing value:", table.get("ticket-9999", 0))
    print("Capacity after growth:", table.capacity)
    print("Load factor:", round(table.load_factor, 3))
    print("Bucket lengths:", table.bucket_lengths())

    del table["ticket-1002"]
    print("After deletion:", sorted(table.items()))

    try:
        print(table["ticket-1002"])
    except KeyError as error:
        print("Expected missing-key error:", error)

    assert table.validate()
    assert len(table) == 4
    assert table["ticket-1001"] == 1250

    # Mutable keys are dangerous: changing hash-relevant state after insertion
    # can make an entry unreachable. Use immutable keys whenever possible.
    print("Invariant validation passed.")


def demonstrate_collisions() -> None:
    print("\n=== Collision handling ===")
    table: HashTable[DeliberatelyCollidingKey, str] = HashTable(4)

    keys = [
        DeliberatelyCollidingKey("A"),
        DeliberatelyCollidingKey("B"),
        DeliberatelyCollidingKey("C"),
    ]

    for key in keys:
        table[key] = f"record-{key.identifier}"

    print("All entries share one hash value:", len({hash(k) for k in keys}) == 1)
    print("Bucket lengths:", table.bucket_lengths())
    print("Lookup through collision chain:", table[keys[1]])

    del table[keys[0]]
    print("Remaining records:", sorted(value for _, value in table.items()))
    assert table[keys[2]] == "record-C"
    assert table.validate()


def demonstrate_frequency_counting() -> None:
    print("\n=== Frequency counting ===")
    events = [
        "login",
        "download",
        "login",
        "upload",
        "login",
        "download",
        "logout",
    ]

    frequencies = Counter(events)
    print("Event frequencies:", dict(frequencies))
    print("Most common event:", frequencies.most_common(1)[0])

    # A dictionary-based counter is expected O(n) for n events under
    # reasonably distributed hashes.
    counts: dict[str, int] = {}
    for event in events:
        counts[event] = counts.get(event, 0) + 1

    assert counts == dict(frequencies)


def demonstrate_performance() -> None:
    print("\n=== Lookup performance experiment ===")
    rng = random.Random(2026)
    count = 50_000
    values = list(range(count))
    rng.shuffle(values)

    mapping = {value: value * 3 for value in values}
    queries = [rng.randrange(count) for _ in range(10_000)]

    start = time.perf_counter()
    checksum = sum(mapping[key] for key in queries)
    elapsed = time.perf_counter() - start

    print(f"Stored entries: {len(mapping)}")
    print(f"Lookups: {len(queries)}")
    print(f"Lookup elapsed time: {elapsed:.6f} seconds")
    print("Checksum:", checksum)

    # This is an observational benchmark, not a universal timing guarantee.
    # Hardware, interpreter version, key distribution, and system load matter.


def demonstrate_edge_cases() -> None:
    print("\n=== Edge cases ===")
    table: HashTable[str, object] = HashTable(capacity=1)

    table["empty-string"] = ""
    table["zero"] = 0
    table["none"] = None

    assert "empty-string" in table
    assert table["empty-string"] == ""
    assert table["zero"] == 0
    assert "none" in table
    assert table["none"] is None

    # Membership checks presence, not truthiness of the stored value.
    print("Empty string is present:", "empty-string" in table)
    print("Zero is present:", "zero" in table)
    print("None is present:", "none" in table)

    try:
        table[["mutable", "list"]] = "invalid"
    except TypeError as error:
        print("Unhashable key rejected:", error)

    try:
        del table["missing"]
    except KeyError:
        print("Deleting a missing key raises KeyError.")

    assert table.validate()


def main() -> None:
    demonstrate_dictionary_basics()
    demonstrate_hash_properties()
    demonstrate_custom_table()
    demonstrate_collisions()
    demonstrate_frequency_counting()
    demonstrate_performance()
    demonstrate_edge_cases()

    print("\nAll hash-table demonstrations completed successfully.")


if __name__ == "__main__":
    main()
