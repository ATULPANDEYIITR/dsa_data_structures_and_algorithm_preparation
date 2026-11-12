"use strict";

/*
 * Heap Fundamentals
 * Event-driven priority queue for an operations scheduling system.
 *
 * Demonstrates:
 * - Complete binary tree representation
 * - Min and max heaps
 * - Parent-child index calculations
 * - Bottom-up heap construction
 * - Event-driven insertion and extraction
 * - Stable priority ordering
 * - Validation and failure handling
 */

const { EventEmitter } = require("node:events");

class HeapError extends Error {
    constructor(message) {
        super(message);
        this.name = "HeapError";
    }
}

class PriorityHeap {
    constructor(mode = "min", items = []) {
        if (!["min", "max"].includes(mode)) {
            throw new TypeError("Mode must be min or max.");
        }

        this.mode = mode;
        this.data = [];

        for (const item of items) {
            this._validateItem(item);
        }

        this.data = items.map(item => ({ ...item }));
        this.heapify();
    }

    _validateItem(item) {
        if (
            !item ||
            !Number.isFinite(item.priority) ||
            typeof item.id !== "string" ||
            item.id.trim() === ""
        ) {
            throw new TypeError("Invalid priority queue item.");
        }
    }

    static parent(index) {
        return index > 0 ? Math.floor((index - 1) / 2) : null;
    }

    static left(index) {
        return 2 * index + 1;
    }

    static right(index) {
        return 2 * index + 2;
    }

    get size() {
        return this.data.length;
    }

    get empty() {
        return this.size === 0;
    }

    _higher(a, b) {
        if (a.priority !== b.priority) {
            return this.mode === "min"
                ? a.priority < b.priority
                : a.priority > b.priority;
        }

        // Earlier sequence numbers win when priorities are equal.
        return a.sequence < b.sequence;
    }

    _swap(i, j) {
        [this.data[i], this.data[j]] = [
            this.data[j],
            this.data[i]
        ];
    }

    _siftUp(index) {
        while (index > 0) {
            const parent = PriorityHeap.parent(index);

            if (!this._higher(this.data[index], this.data[parent])) {
                break;
            }

            this._swap(index, parent);
            index = parent;
        }
    }

    _siftDown(index) {
        while (true) {
            let best = index;
            const left = PriorityHeap.left(index);
            const right = PriorityHeap.right(index);

            if (
                left < this.size &&
                this._higher(this.data[left], this.data[best])
            ) {
                best = left;
            }

            if (
                right < this.size &&
                this._higher(this.data[right], this.data[best])
            ) {
                best = right;
            }

            if (best === index) break;

            this._swap(index, best);
            index = best;
        }
    }

    heapify() {
        // Leaves already satisfy the heap property.
        for (
            let index = Math.floor(this.size / 2) - 1;
            index >= 0;
            index--
        ) {
            this._siftDown(index);
        }

        this.assertValid();
    }

    push(item) {
        this._validateItem(item);

        const entry = {
            ...item,
            sequence: Number.isSafeInteger(item.sequence)
                ? item.sequence
                : PriorityHeap.nextSequence++
        };

        this.data.push(entry);
        this._siftUp(this.size - 1);
        this.assertValid();
    }

    peek() {
        if (this.empty) {
            throw new HeapError("Cannot inspect an empty heap.");
        }

        return { ...this.data[0] };
    }

    pop() {
        if (this.empty) {
            throw new HeapError("Cannot extract from an empty heap.");
        }

        const root = this.data[0];
        const last = this.data.pop();

        if (!this.empty) {
            this.data[0] = last;
            this._siftDown(0);
        }

        this.assertValid();
        return { ...root };
    }

    validate() {
        for (let i = 0; i < this.size; i++) {
            for (const child of [
                PriorityHeap.left(i),
                PriorityHeap.right(i)
            ]) {
                if (
                    child < this.size &&
                    this._higher(this.data[child], this.data[i])
                ) {
                    return false;
                }
            }
        }

        return true;
    }

    assertValid() {
        if (!this.validate()) {
            throw new HeapError("Heap-order invariant violated.");
        }
    }

    snapshot() {
        return this.data.map((item, index) => ({
            index,
            parentIndex: PriorityHeap.parent(index),
            leftIndex: PriorityHeap.left(index),
            rightIndex: PriorityHeap.right(index),
            id: item.id,
            priority: item.priority
        }));
    }
}

PriorityHeap.nextSequence = 0;

class JobScheduler extends EventEmitter {
    constructor() {
        super();
        this.queue = new PriorityHeap("max");
        this.completed = new Set();
        this.running = false;
    }

    submit(job) {
        if (this.completed.has(job.id)) {
            throw new HeapError("Job has already been completed.");
        }

        this.queue.push(job);
        this.emit("job:submitted", { ...job });
    }

    async process(handler) {
        if (this.running) {
            throw new HeapError("Scheduler is already processing.");
        }

        if (typeof handler !== "function") {
            throw new TypeError("A job handler is required.");
        }

        this.running = true;
        const results = [];

        try {
            while (!this.queue.empty) {
                const job = this.queue.pop();

                this.emit("job:started", job);

                try {
                    const result = await handler(job);
                    this.completed.add(job.id);

                    const record = {
                        id: job.id,
                        status: "completed",
                        result
                    };

                    results.push(record);
                    this.emit("job:completed", record);
                } catch (error) {
                    const record = {
                        id: job.id,
                        status: "failed",
                        error: error.message
                    };

                    results.push(record);
                    this.emit("job:failed", record);
                }
            }

            return results;
        } finally {
            this.running = false;
        }
    }
}

async function main() {
    const scheduler = new JobScheduler();

    scheduler.on("job:submitted", job => {
        console.log("SUBMITTED:", job.id);
    });

    scheduler.on("job:started", job => {
        console.log("STARTED:", job.id, "priority:", job.priority);
    });

    scheduler.on("job:completed", job => {
        console.log("COMPLETED:", job.id);
    });

    scheduler.on("job:failed", job => {
        console.log("FAILED:", job.id, job.error);
    });

    scheduler.submit({ id: "backup", priority: 3 });
    scheduler.submit({ id: "security-scan", priority: 10 });
    scheduler.submit({ id: "report", priority: 5 });
    scheduler.submit({ id: "monitoring", priority: 8 });

    console.log("\nMAX HEAP REPRESENTATION:");
    console.log(scheduler.queue.snapshot());

    console.log("\nPROCESSING JOBS:");

    const results = await scheduler.process(async job => {
        // Simulate an operation that can fail.
        if (job.id === "report") {
            throw new Error("Report generation failed.");
        }

        return `${job.id} processed successfully`;
    });

    console.log("\nRESULTS:", results);

    const minHeap = new PriorityHeap("min");

    minHeap.push({ id: "low", priority: 2 });
    minHeap.push({ id: "high", priority: 9 });
    minHeap.push({ id: "medium", priority: 5 });

    console.log("\nMIN HEAP ROOT:", minHeap.peek());
    console.log("MIN HEAP EXTRACTION:", minHeap.pop());

    try {
        new PriorityHeap("min").pop();
    } catch (error) {
        console.log("\nEXPECTED ERROR:", error.message);
    }

    const sample = new PriorityHeap("min", [
        { id: "a", priority: 7 },
        { id: "b", priority: 2 },
        { id: "c", priority: 5 }
    ]);

    if (!sample.validate()) {
        throw new Error("Heap validation failed.");
    }

    console.log("\nALL CHECKS PASSED.");
}

main().catch(error => {
    console.error("FATAL ERROR:", error.message);
    process.exitCode = 1;
});
