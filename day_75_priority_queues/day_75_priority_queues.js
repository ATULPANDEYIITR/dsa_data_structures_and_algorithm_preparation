"use strict";

/*
 * Priority Queues: Event-Driven Scheduling and Selection.
 *
 * Features:
 * - Stable min-priority and max-priority queues.
 * - Binary heap implementation.
 * - Asynchronous task scheduling.
 * - Priority updates and cancellation.
 * - Event-driven processing.
 * - Top-K selection.
 * - K-th largest element.
 * - Running median.
 *
 * Runtime: Node.js 18+
 */

const { EventEmitter } = require("node:events");
const { randomUUID } = require("node:crypto");

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

class EmptyQueueError extends Error {
    constructor() {
        super("Priority queue is empty");
        this.name = "EmptyQueueError";
    }
}

const PriorityMode = Object.freeze({
    MIN: "min",
    MAX: "max"
});

const TaskState = Object.freeze({
    PENDING: "pending",
    RUNNING: "running",
    COMPLETED: "completed",
    CANCELLED: "cancelled",
    FAILED: "failed"
});

class BinaryHeap {
    constructor(mode = PriorityMode.MIN) {
        if (!Object.values(PriorityMode).includes(mode)) {
            throw new ValidationError("Invalid priority mode");
        }

        this.mode = mode;
        this.items = [];
        this.sequence = 0;
    }

    compare(a, b) {
        if (a.priority !== b.priority) {
            return this.mode === PriorityMode.MIN
                ? a.priority < b.priority
                : a.priority > b.priority;
        }

        return a.sequence < b.sequence;
    }

    swap(i, j) {
        [this.items[i], this.items[j]] =
            [this.items[j], this.items[i]];
    }

    push(priority, value) {
        if (!Number.isSafeInteger(priority)) {
            throw new ValidationError(
                "Priority must be a safe integer"
            );
        }

        const entry = {
            priority,
            sequence: this.sequence++,
            value
        };

        this.items.push(entry);
        this.bubbleUp(this.items.length - 1);
    }

    bubbleUp(index) {
        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);

            if (!this.compare(this.items[index], this.items[parent])) {
                break;
            }

            this.swap(index, parent);
            index = parent;
        }
    }

    bubbleDown(index) {
        const size = this.items.length;

        while (true) {
            let best = index;
            const left = 2 * index + 1;
            const right = 2 * index + 2;

            if (
                left < size &&
                this.compare(this.items[left], this.items[best])
            ) {
                best = left;
            }

            if (
                right < size &&
                this.compare(this.items[right], this.items[best])
            ) {
                best = right;
            }

            if (best === index) {
                break;
            }

            this.swap(index, best);
            index = best;
        }
    }

    peek() {
        if (this.items.length === 0) {
            throw new EmptyQueueError();
        }

        return this.items[0].value;
    }

    pop() {
        if (this.items.length === 0) {
            throw new EmptyQueueError();
        }

        const result = this.items[0].value;
        const last = this.items.pop();

        if (this.items.length > 0) {
            this.items[0] = last;
            this.bubbleDown(0);
        }

        return result;
    }

    get size() {
        return this.items.length;
    }

    get empty() {
        return this.items.length === 0;
    }
}

class Scheduler extends EventEmitter {
    constructor() {
        super();

        this.heap = new BinaryHeap(PriorityMode.MAX);
        this.tasks = new Map();
        this.sequence = 0;
        this.processing = false;
    }

    submit(description, priority) {
        if (typeof description !== "string" || !description.trim()) {
            throw new ValidationError(
                "Task description cannot be empty"
            );
        }

        if (!Number.isSafeInteger(priority)) {
            throw new ValidationError(
                "Priority must be a safe integer"
            );
        }

        const id = randomUUID();

        const task = {
            id,
            description,
            priority,
            state: TaskState.PENDING,
            version: 0,
            sequence: this.sequence++
        };

        this.tasks.set(id, task);
        this.enqueue(task);

        this.emit("submitted", { ...task });

        return id;
    }

    enqueue(task) {
        this.heap.push(task.priority, {
            id: task.id,
            version: task.version,
            sequence: task.sequence
        });
    }

    updatePriority(id, priority) {
        const task = this.tasks.get(id);

        if (!task) {
            throw new ValidationError("Unknown task");
        }

        if (task.state !== TaskState.PENDING) {
            throw new ValidationError(
                "Only pending tasks can be updated"
            );
        }

        if (!Number.isSafeInteger(priority)) {
            throw new ValidationError("Invalid priority");
        }

        task.priority = priority;
        task.version++;

        // Old entries become stale and are discarded on extraction.
        this.enqueue(task);

        this.emit("priorityChanged", {
            id,
            priority
        });
    }

    cancel(id) {
        const task = this.tasks.get(id);

        if (!task) {
            throw new ValidationError("Unknown task");
        }

        if (task.state !== TaskState.PENDING) {
            throw new ValidationError(
                "Only pending tasks can be cancelled"
            );
        }

        task.state = TaskState.CANCELLED;
        task.version++;

        this.emit("cancelled", { id });
    }

    next() {
        while (!this.heap.empty) {
            const entry = this.heap.pop();
            const task = this.tasks.get(entry.id);

            if (!task) {
                continue;
            }

            if (task.version !== entry.version) {
                continue;
            }

            if (task.state !== TaskState.PENDING) {
                continue;
            }

            task.state = TaskState.RUNNING;
            this.emit("started", { ...task });

            return task;
        }

        return null;
    }

    async processAll(handler) {
        if (typeof handler !== "function") {
            throw new ValidationError(
                "A task handler function is required"
            );
        }

        if (this.processing) {
            throw new ValidationError(
                "Scheduler is already processing"
            );
        }

        this.processing = true;
        const results = [];

        try {
            let task;

            while ((task = this.next()) !== null) {
                try {
                    const result = await handler({ ...task });

                    task.state = TaskState.COMPLETED;

                    this.emit("completed", {
                        id: task.id,
                        result
                    });

                    results.push({
                        id: task.id,
                        state: task.state
                    });
                } catch (error) {
                    task.state = TaskState.FAILED;

                    this.emit("failed", {
                        id: task.id,
                        error: error.message
                    });

                    results.push({
                        id: task.id,
                        state: task.state,
                        error: error.message
                    });
                }
            }
        } finally {
            this.processing = false;
        }

        return results;
    }

    report() {
        const result = {};

        for (const state of Object.values(TaskState)) {
            result[state] = 0;
        }

        for (const task of this.tasks.values()) {
            result[task.state]++;
        }

        return result;
    }
}

function topKLargest(numbers, k) {
    if (!Number.isSafeInteger(k) || k < 0) {
        throw new ValidationError("k must be non-negative");
    }

    const heap = new BinaryHeap(PriorityMode.MIN);

    for (const number of numbers) {
        if (!Number.isSafeInteger(number)) {
            throw new ValidationError("Invalid numeric element");
        }

        if (heap.size < k) {
            heap.push(number, number);
        } else if (k > 0 && number > heap.peek()) {
            heap.pop();
            heap.push(number, number);
        }
    }

    const result = [];

    while (!heap.empty) {
        result.push(heap.pop());
    }

    return result.sort((a, b) => b - a);
}

function kthLargest(numbers, k) {
    if (!Number.isSafeInteger(k) || k <= 0) {
        throw new ValidationError("k must be positive");
    }

    if (k > numbers.length) {
        throw new ValidationError("k exceeds array length");
    }

    return topKLargest(numbers, k).at(-1);
}

class RunningMedian {
    constructor() {
        this.lower = new BinaryHeap(PriorityMode.MAX);
        this.upper = new BinaryHeap(PriorityMode.MIN);
    }

    add(value) {
        if (!Number.isSafeInteger(value)) {
            throw new ValidationError("Expected a safe integer");
        }

        if (this.lower.empty || value <= this.lower.peek()) {
            this.lower.push(value, value);
        } else {
            this.upper.push(value, value);
        }

        if (this.lower.size > this.upper.size + 1) {
            const moved = this.lower.pop();
            this.upper.push(moved, moved);
        } else if (this.upper.size > this.lower.size) {
            const moved = this.upper.pop();
            this.lower.push(moved, moved);
        }
    }

    median() {
        if (this.lower.empty) {
            throw new EmptyQueueError();
        }

        if (this.lower.size === this.upper.size) {
            return (this.lower.peek() + this.upper.peek()) / 2;
        }

        return this.lower.peek();
    }
}

function demonstrateQueues() {
    for (const mode of [PriorityMode.MIN, PriorityMode.MAX]) {
        const heap = new BinaryHeap(mode);

        for (const value of [40, 10, 30, 5, 20]) {
            heap.push(value, value);
        }

        const output = [];

        while (!heap.empty) {
            output.push(heap.pop());
        }

        console.log(`${mode.toUpperCase()} HEAP:`, output);
    }
}

async function demonstrateScheduler() {
    const scheduler = new Scheduler();

    for (const event of [
        "submitted",
        "started",
        "completed",
        "failed",
        "cancelled",
        "priorityChanged"
    ]) {
        scheduler.on(event, data => {
            console.log(`EVENT ${event}:`, data);
        });
    }

    const backup = scheduler.submit("Database backup", 3);
    const security = scheduler.submit("Security incident", 10);
    const report = scheduler.submit("Generate report", 2);
    const deployment = scheduler.submit("Deploy release", 7);

    scheduler.updatePriority(report, 8);
    scheduler.cancel(backup);

    const results = await scheduler.processAll(async task => {
        // Simulated asynchronous operation.
        await new Promise(resolve => setImmediate(resolve));

        if (task.id === deployment) {
            throw new Error("Deployment validation failed");
        }

        return `Processed: ${task.description}`;
    });

    console.log("PROCESSING RESULTS:", results);
    console.log("FINAL REPORT:", scheduler.report());
}

function demonstrateSelection() {
    const numbers = [17, 4, 29, 11, 8, 35, 21, 3, 29];

    console.log("\nSELECTION");
    console.log("Top 3:", topKLargest(numbers, 3));
    console.log("Third largest:", kthLargest(numbers, 3));
}

function demonstrateMedian() {
    const tracker = new RunningMedian();

    console.log("\nRUNNING MEDIAN");

    for (const value of [12, 4, 5, 3, 8, 7, 15, 20]) {
        tracker.add(value);
        console.log(value, "=>", tracker.median());
    }
}

function runTests() {
    const assert = require("node:assert/strict");

    const min = new BinaryHeap(PriorityMode.MIN);
    [8, 2, 5].forEach(v => min.push(v, v));

    assert.deepEqual(
        [min.pop(), min.pop(), min.pop()],
        [2, 5, 8]
    );

    const max = new BinaryHeap(PriorityMode.MAX);
    [8, 2, 5].forEach(v => max.push(v, v));

    assert.deepEqual(
        [max.pop(), max.pop(), max.pop()],
        [8, 5, 2]
    );

    assert.deepEqual(
        topKLargest([4, 9, 1, 7, 3], 2),
        [9, 7]
    );

    assert.equal(kthLargest([5, 1, 3, 2], 2), 3);

    const median = new RunningMedian();
    [1, 3, 2, 4].forEach(v => median.add(v));

    assert.equal(median.median(), 2.5);

    assert.throws(
        () => topKLargest([1, 2], -1),
        ValidationError
    );

    assert.throws(
        () => min.pop(),
        EmptyQueueError
    );

    console.log("\nAll tests passed.");
}

async function main() {
    demonstrateQueues();
    demonstrateSelection();
    demonstrateMedian();

    console.log("\nASYNC SCHEDULER");
    await demonstrateScheduler();

    runTests();
}

main().catch(error => {
    console.error("Application failure:", error.message);
    process.exitCode = 1;
});
