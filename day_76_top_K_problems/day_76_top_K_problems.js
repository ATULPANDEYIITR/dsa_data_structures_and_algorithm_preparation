"use strict";

/*
 * Top-K Selection Engine
 *
 * Node.js 18+.
 *
 * Demonstrates:
 * - Bounded binary heaps
 * - Quickselect
 * - Frequency aggregation
 * - Binary-search window selection
 * - Asynchronous request processing
 * - Event-driven operation logging
 * - Validation and failure isolation
 *
 * No third-party dependencies.
 */

const { EventEmitter } = require("node:events");
const assert = require("node:assert/strict");

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

function validateArray(values) {
    if (!Array.isArray(values)) {
        throw new ValidationError("Input must be an array");
    }

    if (!values.every(Number.isSafeInteger)) {
        throw new ValidationError("All elements must be safe integers");
    }
}

function validateK(k, n, allowZero = false) {
    if (!Number.isSafeInteger(k)) {
        throw new ValidationError("k must be a safe integer");
    }

    const minimum = allowZero ? 0 : 1;

    if (k < minimum || k > n) {
        throw new ValidationError(`k must be between ${minimum} and ${n}`);
    }
}

/*
 * Comparator-driven binary heap.
 * A comparator returning a negative number means the first
 * element has higher priority.
 */
class BinaryHeap {
    constructor(compare) {
        this.data = [];
        this.compare = compare;
    }

    get size() {
        return this.data.length;
    }

    peek() {
        return this.data[0];
    }

    push(value) {
        this.data.push(value);

        let index = this.data.length - 1;

        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);

            if (this.compare(this.data[index], this.data[parent]) >= 0) {
                break;
            }

            [this.data[index], this.data[parent]] =
                [this.data[parent], this.data[index]];

            index = parent;
        }
    }

    pop() {
        if (this.data.length === 0) {
            throw new Error("Cannot remove from an empty heap");
        }

        const result = this.data[0];
        const last = this.data.pop();

        if (this.data.length > 0) {
            this.data[0] = last;
            this.siftDown(0);
        }

        return result;
    }

    siftDown(index) {
        const length = this.data.length;

        while (true) {
            let smallest = index;
            const left = 2 * index + 1;
            const right = 2 * index + 2;

            if (
                left < length &&
                this.compare(this.data[left], this.data[smallest]) < 0
            ) {
                smallest = left;
            }

            if (
                right < length &&
                this.compare(this.data[right], this.data[smallest]) < 0
            ) {
                smallest = right;
            }

            if (smallest === index) {
                return;
            }

            [this.data[index], this.data[smallest]] =
                [this.data[smallest], this.data[index]];

            index = smallest;
        }
    }
}

function kthLargest(values, k) {
    validateArray(values);
    validateK(k, values.length);

    const heap = new BinaryHeap((a, b) => a - b);

    for (const value of values) {
        heap.push(value);

        if (heap.size > k) {
            heap.pop();
        }
    }

    return heap.peek();
}

function kthSmallest(values, k) {
    validateArray(values);
    validateK(k, values.length);

    const heap = new BinaryHeap((a, b) => b - a);

    for (const value of values) {
        heap.push(value);

        if (heap.size > k) {
            heap.pop();
        }
    }

    return heap.peek();
}

function quickselectLargest(values, k) {
    validateArray(values);
    validateK(k, values.length);

    const array = [...values];
    const target = k - 1;

    let left = 0;
    let right = array.length - 1;

    while (left <= right) {
        const pivot = array[
            left + Math.floor(Math.random() * (right - left + 1))
        ];

        let low = left;
        let current = left;
        let high = right;

        while (current <= high) {
            if (array[current] > pivot) {
                [array[current], array[low]] =
                    [array[low], array[current]];
                current++;
                low++;
            } else if (array[current] < pivot) {
                [array[current], array[high]] =
                    [array[high], array[current]];
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
            return array[target];
        }
    }

    throw new Error("Quickselect failed");
}

function topKFrequent(values, k) {
    validateArray(values);

    const frequencies = new Map();

    for (const value of values) {
        frequencies.set(value, (frequencies.get(value) || 0) + 1);
    }

    validateK(k, frequencies.size, true);

    const heap = new BinaryHeap((a, b) => {
        if (a.frequency !== b.frequency) {
            return a.frequency - b.frequency;
        }

        return b.value - a.value;
    });

    for (const [value, frequency] of frequencies) {
        heap.push({ value, frequency });

        if (heap.size > k) {
            heap.pop();
        }
    }

    const result = [];

    while (heap.size > 0) {
        result.push(heap.pop().value);
    }

    return result.reverse();
}

function kClosestElements(values, k, target) {
    validateArray(values);

    if (!Number.isSafeInteger(target)) {
        throw new ValidationError("Target must be a safe integer");
    }

    for (let i = 1; i < values.length; i++) {
        if (values[i - 1] > values[i]) {
            throw new ValidationError("Array must be sorted");
        }
    }

    validateK(k, values.length, true);

    if (k === 0) {
        return [];
    }

    let left = 0;
    let right = values.length - k;

    while (left < right) {
        const middle = Math.floor((left + right) / 2);

        const leftDistance = target - values[middle];
        const rightDistance = values[middle + k] - target;

        if (leftDistance > rightDistance) {
            left = middle + 1;
        } else {
            right = middle;
        }
    }

    return values.slice(left, left + k);
}

class TopKEngine extends EventEmitter {
    constructor() {
        super();
        this.operations = new Map([
            ["kthLargest", kthLargest],
            ["kthSmallest", kthSmallest],
            ["topKFrequent", topKFrequent]
        ]);
    }

    async execute(request) {
        if (!request || typeof request !== "object") {
            throw new ValidationError("Request must be an object");
        }

        const { operation, values, k, target } = request;

        const start = process.hrtime.bigint();

        try {
            let result;

            if (operation === "kClosestElements") {
                result = kClosestElements(values, k, target);
            } else {
                const handler = this.operations.get(operation);

                if (!handler) {
                    throw new ValidationError("Unknown operation");
                }

                result = handler(values, k);
            }

            const elapsedMs =
                Number(process.hrtime.bigint() - start) / 1e6;

            const response = {
                operation,
                result,
                elapsedMs
            };

            this.emit("completed", response);

            return response;
        } catch (error) {
            this.emit("failed", {
                operation,
                message: error.message
            });

            throw error;
        }
    }

    async executeBatch(requests, concurrency = 2) {
        if (!Array.isArray(requests)) {
            throw new ValidationError("Batch must be an array");
        }

        if (!Number.isSafeInteger(concurrency) || concurrency < 1) {
            throw new ValidationError("Invalid concurrency");
        }

        const results = new Array(requests.length);
        let nextIndex = 0;

        const workers = Array.from(
            { length: Math.min(concurrency, requests.length) },
            async () => {
                while (true) {
                    const index = nextIndex++;

                    if (index >= requests.length) {
                        return;
                    }

                    try {
                        results[index] = await this.execute(requests[index]);
                    } catch (error) {
                        results[index] = {
                            error: error.message
                        };
                    }
                }
            }
        );

        await Promise.all(workers);
        return results;
    }
}

async function main() {
    const engine = new TopKEngine();

    engine.on("completed", event => {
        console.log(
            `[COMPLETED] ${event.operation}:`,
            event.result,
            `(${event.elapsedMs.toFixed(4)} ms)`
        );
    });

    engine.on("failed", event => {
        console.error(`[FAILED] ${event.operation}: ${event.message}`);
    });

    const values = [3, 2, 1, 5, 6, 4];

    console.log("TOP-K SELECTION ENGINE");
    console.log("Second largest:", kthLargest(values, 2));
    console.log("Third smallest:", kthSmallest(values, 3));
    console.log("Quickselect:", quickselectLargest(values, 2));

    console.log(
        "Top frequent:",
        topKFrequent([1, 1, 1, 2, 2, 3], 2)
    );

    console.log(
        "Closest elements:",
        kClosestElements([1, 2, 3, 4, 5], 4, 3)
    );

    assert.equal(kthLargest(values, 2), 5);
    assert.equal(kthSmallest(values, 2), 2);
    assert.equal(quickselectLargest(values, 2), 5);
    assert.deepEqual(topKFrequent([1, 1, 1, 2, 2, 3], 2), [1, 2]);
    assert.deepEqual(kClosestElements([1, 2, 3, 4, 5], 4, 3), [1, 2, 3, 4]);

    console.log("\nAsynchronous batch execution:");

    const batch = await engine.executeBatch([
        {
            operation: "kthLargest",
            values: [10, 30, 20],
            k: 2
        },
        {
            operation: "topKFrequent",
            values: [5, 5, 4, 4, 3],
            k: 2
        },
        {
            operation: "kClosestElements",
            values: [1, 2, 3, 4, 5],
            k: 2,
            target: 4
        },
        {
            operation: "kthLargest",
            values: [1, 2],
            k: 5
        }
    ]);

    console.log("Batch results:", batch);
    console.log("\nAll assertions passed.");
}

main().catch(error => {
    console.error("Fatal error:", error.message);
    process.exitCode = 1;
});
