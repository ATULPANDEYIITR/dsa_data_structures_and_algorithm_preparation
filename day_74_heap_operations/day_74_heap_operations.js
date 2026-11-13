"use strict";

/*
 * HEAP OPERATIONS
 *
 * Binary heap implementation with:
 * - Insert
 * - Extract minimum
 * - Extract maximum
 * - Heapify
 *
 * Node.js 18+ compatible.
 *
 * Includes event-driven operation notifications,
 * validation, asynchronous batch processing,
 * and invariant verification.
 */

const { EventEmitter } = require("node:events");

class HeapError extends Error {
    constructor(message) {
        super(message);
        this.name = "HeapError";
    }
}

class BinaryHeap {
    constructor(compare) {
        this.data = [];
        this.compare = compare;
    }

    get size() {
        return this.data.length;
    }

    peek() {
        return this.data.length ? this.data[0] : null;
    }

    insert(value) {
        this.data.push(value);
        this.siftUp(this.data.length - 1);
    }

    siftUp(index) {
        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);

            if (this.compare(this.data[parent], this.data[index]) <= 0) {
                break;
            }

            [this.data[parent], this.data[index]] =
                [this.data[index], this.data[parent]];

            index = parent;
        }
    }

    siftDown(index) {
        const size = this.data.length;

        while (true) {
            let best = index;
            const left = 2 * index + 1;
            const right = 2 * index + 2;

            if (
                left < size &&
                this.compare(this.data[left], this.data[best]) < 0
            ) {
                best = left;
            }

            if (
                right < size &&
                this.compare(this.data[right], this.data[best]) < 0
            ) {
                best = right;
            }

            if (best === index) break;

            [this.data[index], this.data[best]] =
                [this.data[best], this.data[index]];

            index = best;
        }
    }

    extract() {
        if (!this.data.length) {
            throw new HeapError("Cannot extract from an empty heap.");
        }

        const result = this.data[0];
        const last = this.data.pop();

        if (this.data.length) {
            this.data[0] = last;
            this.siftDown(0);
        }

        return result;
    }

    heapify(values) {
        this.data = [...values];

        // Bottom-up construction is O(n).
        for (
            let index = Math.floor(this.data.length / 2) - 1;
            index >= 0;
            index--
        ) {
            this.siftDown(index);
        }
    }

    validate() {
        for (let i = 1; i < this.data.length; i++) {
            const parent = Math.floor((i - 1) / 2);

            if (this.compare(this.data[parent], this.data[i]) > 0) {
                return false;
            }
        }

        return true;
    }
}

class DoubleEndedPriorityQueue extends EventEmitter {
    constructor(values = []) {
        super();

        this.minimumHeap = new BinaryHeap((a, b) => a - b);
        this.maximumHeap = new BinaryHeap((a, b) => b - a);

        this.counts = new Map();
        this.logicalSize = 0;

        this.metrics = {
            inserted: 0,
            extractedMinimum: 0,
            extractedMaximum: 0,
            heapified: 0
        };

        this.heapify(values);
    }

    static validateValue(value) {
        if (!Number.isSafeInteger(value)) {
            throw new TypeError(
                "Values must be safe JavaScript integers."
            );
        }
    }

    get size() {
        return this.logicalSize;
    }

    heapify(values) {
        if (!Array.isArray(values)) {
            throw new TypeError("Heapify requires an array.");
        }

        values.forEach(DoubleEndedPriorityQueue.validateValue);

        this.minimumHeap.heapify(values);
        this.maximumHeap.heapify(values);

        this.counts.clear();

        for (const value of values) {
            this.counts.set(
                value,
                (this.counts.get(value) || 0) + 1
            );
        }

        this.logicalSize = values.length;
        this.metrics.heapified++;

        this.emit("heapified", { size: this.size });
    }

    insert(value) {
        DoubleEndedPriorityQueue.validateValue(value);

        this.minimumHeap.insert(value);
        this.maximumHeap.insert(value);

        this.counts.set(
            value,
            (this.counts.get(value) || 0) + 1
        );

        this.logicalSize++;
        this.metrics.inserted++;

        this.emit("insert", {
            value,
            size: this.size
        });

        return this.size;
    }

    clean(heap) {
        while (heap.size > 0) {
            const value = heap.peek();

            if ((this.counts.get(value) || 0) > 0) {
                break;
            }

            heap.extract();
        }
    }

    compactIfNeeded() {
        const totalEntries =
            this.minimumHeap.size + this.maximumHeap.size;

        if (totalEntries > Math.max(64, this.size * 4)) {
            const active = [];

            for (const [value, count] of this.counts) {
                for (let i = 0; i < count; i++) {
                    active.push(value);
                }
            }

            this.minimumHeap.heapify(active);
            this.maximumHeap.heapify(active);
        }
    }

    extract(heap, operation) {
        if (this.size === 0) {
            throw new HeapError("Priority queue is empty.");
        }

        this.clean(heap);

        const value = heap.extract();

        const remaining = this.counts.get(value) - 1;

        if (remaining === 0) {
            this.counts.delete(value);
        } else {
            this.counts.set(value, remaining);
        }

        this.logicalSize--;

        this.clean(
            heap === this.minimumHeap
                ? this.maximumHeap
                : this.minimumHeap
        );

        this.compactIfNeeded();

        this.metrics[operation]++;

        this.emit(operation, {
            value,
            size: this.size
        });

        return value;
    }

    extractMin() {
        return this.extract(
            this.minimumHeap,
            "extractedMinimum"
        );
    }

    extractMax() {
        return this.extract(
            this.maximumHeap,
            "extractedMaximum"
        );
    }

    peekMin() {
        if (!this.size) return null;
        this.clean(this.minimumHeap);
        return this.minimumHeap.peek();
    }

    peekMax() {
        if (!this.size) return null;
        this.clean(this.maximumHeap);
        return this.maximumHeap.peek();
    }

    verify() {
        const count = [...this.counts.values()]
            .reduce((sum, value) => sum + value, 0);

        return (
            count === this.size &&
            this.minimumHeap.validate() &&
            this.maximumHeap.validate()
        );
    }

    snapshot() {
        return Object.freeze({
            size: this.size,
            minimum: this.peekMin(),
            maximum: this.peekMax(),
            metrics: { ...this.metrics }
        });
    }

    // Sequential asynchronous processing preserves operation order.
    async processBatch(operations) {
        if (!Array.isArray(operations)) {
            throw new TypeError("Operations must be an array.");
        }

        const results = [];

        for (const operation of operations) {
            await Promise.resolve();

            switch (operation.type) {
                case "insert":
                    results.push(this.insert(operation.value));
                    break;

                case "extractMin":
                    results.push(this.extractMin());
                    break;

                case "extractMax":
                    results.push(this.extractMax());
                    break;

                default:
                    throw new HeapError(
                        `Unknown operation: ${operation.type}`
                    );
            }
        }

        return results;
    }
}

async function main() {
    const queue = new DoubleEndedPriorityQueue([
        45, 12, 30, 8, 25, 60, 18, 8
    ]);

    queue.on("insert", event => {
        console.log("Inserted:", event.value);
    });

    queue.on("extractedMinimum", event => {
        console.log("Extracted minimum:", event.value);
    });

    queue.on("extractedMaximum", event => {
        console.log("Extracted maximum:", event.value);
    });

    console.log("Initial:", queue.snapshot());

    await queue.processBatch([
        { type: "insert", value: 5 },
        { type: "insert", value: 75 },
        { type: "insert", value: 12 },
        { type: "extractMin" },
        { type: "extractMax" }
    ]);

    console.log("\nCurrent state:", queue.snapshot());

    if (!queue.verify()) {
        throw new Error("Heap invariant violation.");
    }

    const sorted = [];

    while (queue.size) {
        sorted.push(queue.extractMin());
    }

    console.log("\nSorted extraction:", sorted);

    try {
        queue.extractMin();
    } catch (error) {
        console.log("\nExpected failure:", error.message);
    }

    try {
        queue.insert(Number.MAX_SAFE_INTEGER + 1);
    } catch (error) {
        console.log("Validation failure:", error.message);
    }

    console.log("\nAll operations completed.");
}

main().catch(error => {
    console.error("Execution failed:", error);
    process.exitCode = 1;
});
