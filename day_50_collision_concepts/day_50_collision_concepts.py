#!/usr/bin/env python3
"""Hash collisions, separate chaining, open addressing, and load-factor analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterator, TypeVar

K = TypeVar("K")
V = TypeVar("V")
EMPTY = object()
DELETED = object()


def stable_hash(key: object) -> int:
    """Deterministic hash for demonstration; not suitable for adversarial keys."""
    if isinstance(key, int):
        return key
    if isinstance(key, str):
        value = 0
        for character in key:
            value = (value * 31 + ord(character)) & 0xFFFFFFFF
        return value
    raise TypeError("Keys must be integers or strings")


@dataclass
class Metrics:
    operations: int = 0
    probes: int = 0
    collisions: int = 0


class ChainedHashMap(Generic[K, V]):
    """Hash map using linked collision chains represented by Python lists."""

    def __init__(self, capacity: int = 8) -> None:
        if capacity < 1:
            raise ValueError("Capacity must be positive")
        self._buckets: list[list[tuple[K, V]]] = [
            [] for _ in range(capacity)
        ]
        self._size = 0
        self.metrics = Metrics()

    @property
    def load_factor(self) -> float:
        return self._size / len(self._buckets)

    def _index(self, key: K) -> int:
        return stable_hash(key) % len(self._buckets)

    def put(self, key: K, value: V) -> None:
        index = self._index(key)
        bucket = self._buckets[index]
        self.metrics.operations += 1

        for position, (existing_key, _) in enumerate(bucket):
            self.metrics.probes += 1
            if existing_key == key:
                bucket[position] = (key, value)
                return
            self.metrics.collisions += 1

        if bucket:
            self.metrics.collisions += 1
        bucket.append((key, value))
        self._size += 1

        if self.load_factor > 0.75:
            self._resize(len(self._buckets) * 2)

    def get(self, key: K, default: V | None = None) -> V | None:
        self.metrics.operations += 1
        for existing_key, value in self._buckets[self._index(key)]:
            self.metrics.probes += 1
            if existing_key == key:
                return value
        return default

    def remove(self, key: K) -> bool:
        bucket = self._buckets[self._index(key)]
        self.metrics.operations += 1
        for position, (existing_key, _) in enumerate(bucket):
            self.metrics.probes += 1
            if existing_key == key:
                del bucket[position]
                self._size -= 1
                return True
        return False

    def _resize(self, capacity: int) -> None:
        entries = [
            entry for bucket in self._buckets for entry in bucket
        ]
        self._buckets = [[] for _ in range(capacity)]
        self._size = 0
        for key, value in entries:
            self._buckets[self._index(key)].append((key, value))
            self._size += 1

    def items(self) -> Iterator[tuple[K, V]]:
        for bucket in self._buckets:
            yield from bucket

    def __len__(self) -> int:
        return self._size


class OpenAddressHashMap(Generic[K, V]):
    """Linear-probing hash map with tombstones and dynamic resizing."""

    def __init__(self, capacity: int = 8) -> None:
        if capacity < 4:
            raise ValueError("Capacity must be at least four")
        self._keys: list[object] = [EMPTY] * capacity
        self._values: list[object] = [EMPTY] * capacity
        self._size = 0
        self._deleted = 0
        self.metrics = Metrics()

    @property
    def load_factor(self) -> float:
        return self._size / len(self._keys)

    def _find(self, key: K) -> tuple[int, bool]:
        capacity = len(self._keys)
        index = stable_hash(key) % capacity
        first_deleted: int | None = None

        for _ in range(capacity):
            self.metrics.probes += 1
            existing = self._keys[index]

            if existing is EMPTY:
                return (
                    first_deleted if first_deleted is not None else index,
                    False,
                )

            if existing is DELETED:
                if first_deleted is None:
                    first_deleted = index
            elif existing == key:
                return index, True
            else:
                self.metrics.collisions += 1

            index = (index + 1) % capacity

        if first_deleted is not None:
            return first_deleted, False
        raise RuntimeError("Hash table has no available slot")

    def put(self, key: K, value: V) -> None:
        self.metrics.operations += 1

        if (self._size + self._deleted + 1) / len(self._keys) > 0.65:
            self._resize(len(self._keys) * 2)

        index, found = self._find(key)
        if found:
            self._values[index] = value
            return

        if self._keys[index] is DELETED:
            self._deleted -= 1
        self._keys[index] = key
        self._values[index] = value
        self._size += 1

    def get(self, key: K, default: V | None = None) -> V | None:
        self.metrics.operations += 1
        try:
            index, found = self._find(key)
        except RuntimeError:
            return default
        return self._values[index] if found else default  # type: ignore[return-value]

    def remove(self, key: K) -> bool:
        self.metrics.operations += 1
        try:
            index, found = self._find(key)
        except RuntimeError:
            return False
        if not found:
            return False

        self._keys[index] = DELETED
        self._values[index] = DELETED
        self._size -= 1
        self._deleted += 1

        if self._deleted > self._size and self._deleted > 8:
            self._resize(len(self._keys))
        return True

    def _resize(self, capacity: int) -> None:
        old_entries = [
            (key, value)
            for key, value in zip(self._keys, self._values)
            if key is not EMPTY and key is not DELETED
        ]
        self._keys = [EMPTY] * capacity
        self._values = [EMPTY] * capacity
        self._size = 0
        self._deleted = 0

        for key, value in old_entries:
            index, _ = self._find(key)  # type: ignore[arg-type]
            self._keys[index] = key
            self._values[index] = value
            self._size += 1

    def __len__(self) -> int:
        return self._size


def demonstrate_collision_handling() -> None:
    print("Separate chaining")
    chained: ChainedHashMap[int, str] = ChainedHashMap(4)
    for key in (1, 5, 9, 13):
        chained.put(key, f"record-{key}")
    print("Entries:", sorted(chained.items()))
    print("Load factor:", round(chained.load_factor, 3))
    print("Lookup 9:", chained.get(9))
    print("Remove 5:", chained.remove(5))
    print("Lookup missing key:", chained.get(99))
    print("Metrics:", chained.metrics)

    print("\nOpen addressing")
    open_map: OpenAddressHashMap[int, str] = OpenAddressHashMap(8)
    for key in (1, 9, 17, 25):
        open_map.put(key, f"record-{key}")
    print("Load factor:", round(open_map.load_factor, 3))
    print("Lookup 17:", open_map.get(17))
    print("Remove 9:", open_map.remove(9))
    open_map.put(33, "record-33")
    print("Lookup after deletion:", open_map.get(33))
    print("Metrics:", open_map.metrics)


def run_tests() -> None:
    chained: ChainedHashMap[int, str] = ChainedHashMap(4)
    chained.put(1, "a")
    chained.put(5, "b")
    assert chained.get(1) == "a"
    assert chained.get(5) == "b"
    chained.put(1, "updated")
    assert chained.get(1) == "updated"
    assert chained.remove(5)
    assert chained.get(5) is None
    assert not chained.remove(5)

    opened: OpenAddressHashMap[int, str] = OpenAddressHashMap(8)
    for key in (1, 9, 17, 25):
        opened.put(key, str(key))
    assert all(opened.get(key) == str(key) for key in (1, 9, 17, 25))
    assert opened.remove(9)
    assert opened.get(17) == "17"
    opened.put(33, "33")
    assert opened.get(33) == "33"

    for key in range(100):
        opened.put(key, str(key))
    assert all(opened.get(key) == str(key) for key in range(100))

    try:
        ChainedHashMap(0)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid capacity was accepted")

    print("All tests passed.")


if __name__ == "__main__":
    run_tests()
    demonstrate_collision_handling()
