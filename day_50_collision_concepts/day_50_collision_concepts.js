"use strict";

/*
 * Collision analysis for an in-memory cache.
 * Compares separate chaining with open addressing and measures probe behavior.
 */

const EMPTY = Symbol("empty");
const DELETED = Symbol("deleted");

function stableHash(key) {
    if (typeof key === "number" && Number.isSafeInteger(key)) {
        return key >>> 0;
    }
    if (typeof key === "string") {
        let hash = 0;
        for (let i = 0; i < key.length; i++) {
            hash = (Math.imul(hash, 31) + key.charCodeAt(i)) >>> 0;
        }
        return hash;
    }
    throw new TypeError("Keys must be strings or safe integers");
}

class ChainedCache {
    constructor(capacity = 8) {
        if (!Number.isInteger(capacity) || capacity < 1) {
            throw new RangeError("Capacity must be a positive integer");
        }
        this.buckets = Array.from({ length: capacity }, () => []);
        this.size = 0;
        this.stats = { probes: 0, collisions: 0, resizes: 0 };
    }

    get loadFactor() {
        return this.size / this.buckets.length;
    }

    index(key) {
        return stableHash(key) % this.buckets.length;
    }

    set(key, value) {
        const bucket = this.buckets[this.index(key)];
        for (const entry of bucket) {
            this.stats.probes++;
            if (entry.key === key) {
                entry.value = value;
                return;
            }
            this.stats.collisions++;
        }

        if (bucket.length > 0) this.stats.collisions++;
        bucket.push({ key, value });
        this.size++;

        if (this.loadFactor > 0.75) {
            this.resize(this.buckets.length * 2);
        }
    }

    get(key) {
        for (const entry of this.buckets[this.index(key)]) {
            this.stats.probes++;
            if (entry.key === key) return entry.value;
        }
        return undefined;
    }

    delete(key) {
        const bucket = this.buckets[this.index(key)];
        const index = bucket.findIndex(entry => entry.key === key);
        this.stats.probes += index < 0 ? bucket.length : index + 1;
        if (index < 0) return false;
        bucket.splice(index, 1);
        this.size--;
        return true;
    }

    resize(capacity) {
        const entries = this.buckets.flat();
        this.buckets = Array.from({ length: capacity }, () => []);
        this.size = 0;
        for (const entry of entries) {
            this.buckets[this.index(entry.key)].push(entry);
            this.size++;
        }
        this.stats.resizes++;
    }
}

class LinearProbeCache {
    constructor(capacity = 8) {
        if (!Number.isInteger(capacity) || capacity < 4) {
            throw new RangeError("Capacity must be an integer of at least four");
        }
        this.keys = Array(capacity).fill(EMPTY);
        this.values = Array(capacity).fill(EMPTY);
        this.size = 0;
        this.deleted = 0;
        this.stats = { probes: 0, collisions: 0, resizes: 0 };
    }

    get loadFactor() {
        return this.size / this.keys.length;
    }

    locate(key) {
        let index = stableHash(key) % this.keys.length;
        let firstDeleted = -1;

        for (let count = 0; count < this.keys.length; count++) {
            this.stats.probes++;
            const existing = this.keys[index];

            if (existing === EMPTY) {
                return {
                    index: firstDeleted >= 0 ? firstDeleted : index,
                    found: false
                };
            }

            if (existing === DELETED) {
                if (firstDeleted < 0) firstDeleted = index;
            } else if (existing === key) {
                return { index, found: true };
            } else {
                this.stats.collisions++;
            }

            index = (index + 1) % this.keys.length;
        }

        if (firstDeleted >= 0) {
            return { index: firstDeleted, found: false };
        }
        throw new Error("No available table slot");
    }

    set(key, value) {
        // Count tombstones in the occupancy threshold to prevent failed searches.
        if ((this.size + this.deleted + 1) / this.keys.length > 0.65) {
            this.resize(this.keys.length * 2);
        }

        const { index, found } = this.locate(key);
        if (found) {
            this.values[index] = value;
            return;
        }

        if (this.keys[index] === DELETED) this.deleted--;
        this.keys[index] = key;
        this.values[index] = value;
        this.size++;
    }

    get(key) {
        const { index, found } = this.locate(key);
        return found ? this.values[index] : undefined;
    }

    delete(key) {
        const { index, found } = this.locate(key);
        if (!found) return false;
        this.keys[index] = DELETED;
        this.values[index] = DELETED;
        this.size--;
        this.deleted++;
        if (this.deleted > this.size && this.deleted > 8) {
            this.resize(this.keys.length);
        }
        return true;
    }

    resize(capacity) {
        const entries = [];
        for (let i = 0; i < this.keys.length; i++) {
            if (this.keys[i] !== EMPTY && this.keys[i] !== DELETED) {
                entries.push([this.keys[i], this.values[i]]);
            }
        }

        this.keys = Array(capacity).fill(EMPTY);
        this.values = Array(capacity).fill(EMPTY);
        this.size = 0;
        this.deleted = 0;

        for (const [key, value] of entries) {
            const { index } = this.locate(key);
            this.keys[index] = key;
            this.values[index] = value;
            this.size++;
        }
        this.stats.resizes++;
    }
}

function runTests() {
    const chained = new ChainedCache(4);
    for (const key of [1, 5, 9, 13]) chained.set(key, `value-${key}`);
    if (chained.get(9) !== "value-9") throw new Error("Chaining lookup failed");
    if (!chained.delete(5) || chained.get(5) !== undefined) {
        throw new Error("Chaining deletion failed");
    }

    const opened = new LinearProbeCache(8);
    for (const key of [1, 9, 17, 25]) opened.set(key, `value-${key}`);
    if (opened.get(17) !== "value-17") throw new Error("Probe lookup failed");
    if (!opened.delete(9) || opened.get(17) !== "value-17") {
        throw new Error("Tombstone broke a collision chain");
    }
    opened.set(33, "value-33");
    if (opened.get(33) !== "value-33") throw new Error("Insertion failed");

    for (let key = 0; key < 100; key++) opened.set(key, `value-${key}`);
    for (let key = 0; key < 100; key++) {
        if (opened.get(key) !== `value-${key}`) {
            throw new Error(`Resize test failed at key ${key}`);
        }
    }

    console.log("All tests passed.");
}

function report(name, cache) {
    console.log(name, {
        capacity: cache.buckets?.length ?? cache.keys.length,
        size: cache.size,
        loadFactor: Number(cache.loadFactor.toFixed(3)),
        stats: cache.stats
    });
}

function main() {
    runTests();

    const chained = new ChainedCache(4);
    const opened = new LinearProbeCache(8);

    for (const key of [1, 5, 9, 13, 17, 21]) {
        chained.set(key, `item-${key}`);
    }
    for (const key of [1, 9, 17, 25]) {
        opened.set(key, `item-${key}`);
    }

    console.log("Collision-heavy cache workload");
    report("Separate chaining", chained);
    report("Linear probing", opened);
}

main();
