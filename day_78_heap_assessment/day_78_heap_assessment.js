"use strict";

/*
 * Heap Assessment: Priority Queues and Heap Algorithms
 * Runtime: Node.js 18+
 *
 * Includes:
 * - Binary min heap and max heap
 * - Indexed priority queue
 * - Kth largest element
 * - Top K frequent elements
 * - Merge K sorted streams
 * - Running median
 * - Event-driven task scheduling
 * - Asynchronous priority execution
 * - Cancellation and error handling
 */

const assert = require("node:assert/strict");
const { EventEmitter } = require("node:events");

class HeapError extends Error {
    constructor(message) {
        super(message);
        this.name = "HeapError";
    }
}

class BinaryHeap {
    constructor(comparator = (a, b) => a - b) {
        this.items = [];
        this.compare = comparator;
    }

    get size() {
        return this.items.length;
    }

    get empty() {
        return this.size === 0;
    }

    peek() {
        if (this.empty) {
            throw new HeapError("Heap is empty.");
        }

        return this.items[0];
    }

    push(value) {
        this.items.push(value);
        this._siftUp(this.size - 1);
    }

    pop() {
        if (this.empty) {
            throw new HeapError("Heap is empty.");
        }

        const root = this.items[0];
        const last = this.items.pop();

        if (!this.empty) {
            this.items[0] = last;
            this._siftDown(0);
        }

        return root;
    }

    _siftUp(index) {
        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);

            if (this.compare(
                this.items[index],
                this.items[parent]
            ) >= 0) {
                break;
            }

            [this.items[index], this.items[parent]] =
                [this.items[parent], this.items[index]];

            index = parent;
        }
    }

    _siftDown(index) {
        const n = this.size;

        while (true) {
            let smallest = index;
            const left = index * 2 + 1;
            const right = left + 1;

            if (
                left < n &&
                this.compare(
                    this.items[left],
                    this.items[smallest]
                ) < 0
            ) {
                smallest = left;
            }

            if (
                right < n &&
                this.compare(
                    this.items[right],
                    this.items[smallest]
                ) < 0
            ) {
                smallest = right;
            }

            if (smallest === index) {
                break;
            }

            [this.items[index], this.items[smallest]] =
                [this.items[smallest], this.items[index]];

            index = smallest;
        }
    }

    static heapify(values, comparator) {
        const heap = new BinaryHeap(comparator);
        heap.items = [...values];

        for (
            let i = Math.floor(heap.size / 2) - 1;
            i >= 0;
            i--
        ) {
            heap._siftDown(i);
        }

        return heap;
    }
}

function validateNumbers(values) {
    if (
        !Array.isArray(values) ||
        !values.every(Number.isSafeInteger)
    ) {
        throw new HeapError(
            "Expected an array of safe integers."
        );
    }

    return values;
}

function kthLargest(values, k) {
    const nums = validateNumbers(values);

    if (!Number.isInteger(k) || k < 1 || k > nums.length) {
        throw new HeapError("Invalid k.");
    }

    const heap = new BinaryHeap((a, b) => a - b);

    for (const value of nums) {
        heap.push(value);

        if (heap.size > k) {
            heap.pop();
        }
    }

    return heap.peek();
}

function topKFrequent(values, k) {
    const nums = validateNumbers(values);
    const frequencies = new Map();

    for (const value of nums) {
        frequencies.set(
            value,
            (frequencies.get(value) || 0) + 1
        );
    }

    if (
        !Number.isInteger(k) ||
        k < 0 ||
        k > frequencies.size
    ) {
        throw new HeapError("Invalid k.");
    }

    const heap = new BinaryHeap((a, b) => {
        return a.frequency - b.frequency ||
            a.value - b.value;
    });

    for (const [value, frequency] of frequencies) {
        heap.push({ value, frequency });

        if (heap.size > k) {
            heap.pop();
        }
    }

    return heap.items
        .sort((a, b) =>
            b.frequency - a.frequency ||
            a.value - b.value
        )
        .map(item => item.value);
}

function mergeKSortedArrays(arrays) {
    if (!Array.isArray(arrays)) {
        throw new HeapError("Expected an array of arrays.");
    }

    const heap = new BinaryHeap((a, b) =>
        a.value - b.value ||
        a.arrayIndex - b.arrayIndex
    );

    arrays.forEach((array, index) => {
        validateNumbers(array);

        for (let i = 1; i < array.length; i++) {
            if (array[i] < array[i - 1]) {
                throw new HeapError("Arrays must be sorted.");
            }
        }

        if (array.length) {
            heap.push({
                value: array[0],
                arrayIndex: index,
                elementIndex: 0
            });
        }
    });

    const result = [];

    while (!heap.empty) {
        const current = heap.pop();

        result.push(current.value);

        const nextIndex = current.elementIndex + 1;
        const source = arrays[current.arrayIndex];

        if (nextIndex < source.length) {
            heap.push({
                value: source[nextIndex],
                arrayIndex: current.arrayIndex,
                elementIndex: nextIndex
            });
        }
    }

    return result;
}

class RunningMedian {
    constructor() {
        this.lower = new BinaryHeap((a, b) => b - a);
        this.upper = new BinaryHeap((a, b) => a - b);
    }

    add(value) {
        if (!Number.isSafeInteger(value)) {
            throw new HeapError("Invalid median value.");
        }

        if (this.lower.empty || value <= this.lower.peek()) {
            this.lower.push(value);
        } else {
            this.upper.push(value);
        }

        if (this.lower.size > this.upper.size + 1) {
            this.upper.push(this.lower.pop());
        }

        if (this.upper.size > this.lower.size) {
            this.lower.push(this.upper.pop());
        }
    }

    median() {
        if (this.lower.empty) {
            throw new HeapError("No values available.");
        }

        if (this.lower.size > this.upper.size) {
            return this.lower.peek();
        }

        return (this.lower.peek() + this.upper.peek()) / 2;
    }
}

const PRIORITY = Object.freeze({
    CRITICAL: 0,
    HIGH: 1,
    NORMAL: 2,
    LOW: 3
});

class PriorityTaskScheduler extends EventEmitter {
    constructor() {
        super();

        this.queue = new BinaryHeap((a, b) =>
            a.priority - b.priority ||
            a.sequence - b.sequence
        );

        this.sequence = 0;
        this.tasks = new Map();
        this.cancelled = new Set();
    }

    submit(id, description, priority) {
        if (
            typeof id !== "string" ||
            !id.trim() ||
            this.tasks.has(id)
        ) {
            throw new HeapError("Invalid or duplicate task ID.");
        }

        if (
            typeof description !== "string" ||
            !description.trim()
        ) {
            throw new HeapError("Invalid task description.");
        }

        if (!Object.values(PRIORITY).includes(priority)) {
            throw new HeapError("Unknown priority.");
        }

        const task = Object.freeze({
            id,
            description,
            priority,
            sequence: this.sequence++
        });

        this.tasks.set(id, "PENDING");
        this.queue.push(task);

        this.emit("submitted", task);

        return task;
    }

    cancel(id) {
        if (this.tasks.get(id) !== "PENDING") {
            return false;
        }

        // Lazy deletion avoids expensive arbitrary heap removal.
        this.cancelled.add(id);
        this.tasks.set(id, "CANCELLED");

        this.emit("cancelled", id);

        return true;
    }

    async executeNext(handler) {
        if (typeof handler !== "function") {
            throw new HeapError("Handler must be a function.");
        }

        while (!this.queue.empty) {
            const task = this.queue.pop();

            if (this.cancelled.has(task.id)) {
                this.cancelled.delete(task.id);
                continue;
            }

            this.tasks.set(task.id, "RUNNING");
            this.emit("started", task);

            try {
                const result = await handler(task);

                this.tasks.set(task.id, "COMPLETED");

                this.emit("completed", {
                    task,
                    result
                });

                return result;

            } catch (error) {
                this.tasks.set(task.id, "FAILED");

                this.emit("failed", {
                    task,
                    error
                });

                throw error;
            }
        }

        return null;
    }
}

function slidingWindowMaximum(values, windowSize) {
    const nums = validateNumbers(values);

    if (
        !Number.isInteger(windowSize) ||
        windowSize < 1 ||
        windowSize > nums.length
    ) {
        throw new HeapError("Invalid window size.");
    }

    const deque = [];
    const result = [];

    for (let i = 0; i < nums.length; i++) {
        while (deque.length && deque[0] <= i - windowSize) {
            deque.shift();
        }

        while (
            deque.length &&
            nums[deque[deque.length - 1]] <= nums[i]
        ) {
            deque.pop();
        }

        deque.push(i);

        if (i >= windowSize - 1) {
            result.push(nums[deque[0]]);
        }
    }

    return result;
}

function connectRopes(values) {
    const nums = validateNumbers(values);

    if (nums.some(value => value < 0)) {
        throw new HeapError("Negative rope lengths are invalid.");
    }

    const heap = BinaryHeap.heapify(nums, (a, b) => a - b);

    let total = 0;

    while (heap.size > 1) {
        const combined = heap.pop() + heap.pop();

        total += combined;
        heap.push(combined);
    }

    return total;
}

async function main() {
    console.log("HEAP AND PRIORITY QUEUE ASSESSMENT\n");

    console.log("Kth largest:", kthLargest(
        [7, 10, 4, 3, 20, 15], 3
    ));

    console.log("Top frequent:", topKFrequent(
        [1, 1, 1, 2, 2, 3], 2
    ));

    console.log("Merged arrays:", mergeKSortedArrays([
        [1, 4, 7],
        [2, 5, 8],
        [3, 6, 9]
    ]));

    const median = new RunningMedian();

    for (const value of [5, 15, 1, 3]) {
        median.add(value);
        console.log("Running median:", median.median());
    }

    console.log("Sliding maximum:", slidingWindowMaximum(
        [1, 3, -1, -3, 5, 3, 6, 7], 3
    ));

    console.log("Rope connection cost:", connectRopes([4, 3, 2, 6]));

    const scheduler = new PriorityTaskScheduler();

    scheduler.on("completed", ({ task }) => {
        console.log("Completed:", task.id);
    });

    scheduler.on("failed", ({ task, error }) => {
        console.error("Failed:", task.id, error.message);
    });

    scheduler.submit("A", "Routine report", PRIORITY.LOW);
    scheduler.submit("B", "Security incident", PRIORITY.CRITICAL);
    scheduler.submit("C", "Database backup", PRIORITY.NORMAL);

    await scheduler.executeNext(async task => {
        return `Executed ${task.description}`;
    });

    // Basic correctness checks.
    assert.equal(kthLargest([3, 2, 1, 5, 6, 4], 2), 5);
    assert.deepEqual(
        slidingWindowMaximum([1, 3, -1, -3, 5, 3, 6, 7], 3),
        [3, 3, 5, 5, 6, 7]
    );

    assert.equal(connectRopes([4, 3, 2, 6]), 29);

    assert.throws(
        () => kthLargest([1, 2], 3),
        HeapError
    );

    console.log("\nAll correctness checks passed.");
}

main().catch(error => {
    console.error("Assessment failed:", error.message);
    process.exitCode = 1;
});
