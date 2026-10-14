"use strict";

/*
 * Deque and priority queue processing for an engineering operations console.
 * Run with Node.js: node deque_priority_queue.js
 */

class Deque {
    #items = [];
    #head = 0;
    #tail = 0;

    get size() {
        return this.#tail - this.#head;
    }

    get empty() {
        return this.size === 0;
    }

    pushBack(value) {
        this.#items[this.#tail++] = value;
    }

    pushFront(value) {
        this.#items[--this.#head] = value;
    }

    popFront() {
        if (this.empty) {
            throw new RangeError("Cannot remove from an empty deque.");
        }
        const value = this.#items[this.#head];
        delete this.#items[this.#head++];
        this.#compactIfNeeded();
        return value;
    }

    popBack() {
        if (this.empty) {
            throw new RangeError("Cannot remove from an empty deque.");
        }
        const value = this.#items[--this.#tail];
        delete this.#items[this.#tail];
        this.#compactIfNeeded();
        return value;
    }

    peekFront() {
        if (this.empty) throw new RangeError("Deque is empty.");
        return this.#items[this.#head];
    }

    peekBack() {
        if (this.empty) throw new RangeError("Deque is empty.");
        return this.#items[this.#tail - 1];
    }

    #compactIfNeeded() {
        if (this.#head > 64 && this.#head * 2 > this.#tail) {
            this.#items = this.#items.slice(this.#head, this.#tail);
            this.#tail -= this.#head;
            this.#head = 0;
        }
    }

    toArray() {
        return this.#items.slice(this.#head, this.#tail);
    }
}

class BinaryHeap {
    #values = [];
    #compare;

    constructor(compare) {
        if (typeof compare !== "function") {
            throw new TypeError("A comparison function is required.");
        }
        this.#compare = compare;
    }

    get size() {
        return this.#values.length;
    }

    push(value) {
        const values = this.#values;
        values.push(value);
        let child = values.length - 1;

        while (child > 0) {
            const parent = Math.floor((child - 1) / 2);
            if (this.#compare(values[child], values[parent]) >= 0) break;
            [values[child], values[parent]] = [values[parent], values[child]];
            child = parent;
        }
    }

    peek() {
        if (this.size === 0) throw new RangeError("Heap is empty.");
        return this.#values[0];
    }

    pop() {
        if (this.size === 0) throw new RangeError("Heap is empty.");
        const root = this.#values[0];
        const last = this.#values.pop();

        if (this.#values.length > 0) {
            this.#values[0] = last;
            let parent = 0;

            while (true) {
                const left = parent * 2 + 1;
                const right = left + 1;
                let best = parent;

                if (
                    left < this.size &&
                    this.#compare(this.#values[left], this.#values[best]) < 0
                ) {
                    best = left;
                }

                if (
                    right < this.size &&
                    this.#compare(this.#values[right], this.#values[best]) < 0
                ) {
                    best = right;
                }

                if (best === parent) break;
                [this.#values[parent], this.#values[best]] =
                    [this.#values[best], this.#values[parent]];
                parent = best;
            }
        }

        return root;
    }
}

class StablePriorityQueue {
    #heap;
    #sequence = 0;
    #active = new Map();

    constructor({ highestFirst = false } = {}) {
        this.highestFirst = highestFirst;

        // Sequence numbers provide FIFO order when priorities are equal.
        this.#heap = new BinaryHeap((a, b) => {
            if (a.priority !== b.priority) {
                return highestFirst
                    ? b.priority - a.priority
                    : a.priority - b.priority;
            }
            return a.sequence - b.sequence;
        });
    }

    get size() {
        return this.#active.size;
    }

    enqueue(value, priority) {
        if (!Number.isSafeInteger(priority)) {
            throw new TypeError("Priority must be a safe integer.");
        }

        const entry = {
            id: this.#sequence++,
            sequence: this.#sequence - 1,
            priority,
            value
        };

        this.#active.set(entry.id, entry);
        this.#heap.push(entry);
        return entry.id;
    }

    cancel(id) {
        // Heap entries are not removed in place. Inactive entries are skipped
        // when they reach the root, avoiding an O(n) search through the heap.
        return this.#active.delete(id);
    }

    #discardInactive() {
        while (
            this.#heap.size > 0 &&
            !this.#active.has(this.#heap.peek().id)
        ) {
            this.#heap.pop();
        }
    }

    dequeue() {
        this.#discardInactive();
        if (this.#heap.size === 0) {
            throw new RangeError("Priority queue is empty.");
        }

        const entry = this.#heap.pop();
        this.#active.delete(entry.id);
        return entry.value;
    }

    peek() {
        this.#discardInactive();
        if (this.#heap.size === 0) {
            throw new RangeError("Priority queue is empty.");
        }
        return this.#heap.peek().value;
    }
}

class EngineeringEventProcessor {
    #urgent = new Deque();
    #scheduled = new StablePriorityQueue({ highestFirst: true });
    #knownIds = new Set();

    submit(event, { urgent = false } = {}) {
        if (!event || typeof event.id !== "string" || !event.id.trim()) {
            throw new TypeError("Event requires a non-empty identifier.");
        }
        if (!Number.isSafeInteger(event.priority) || event.priority < 0) {
            throw new RangeError("Event priority must be a non-negative integer.");
        }
        if (this.#knownIds.has(event.id)) {
            throw new Error(`Duplicate event identifier: ${event.id}`);
        }

        this.#knownIds.add(event.id);
        const record = Object.freeze({ ...event });

        if (urgent) {
            this.#urgent.pushFront(record);
        } else {
            this.#scheduled.enqueue(record, record.priority);
        }
    }

    nextUrgent() {
        if (this.#urgent.empty) return null;
        const event = this.#urgent.popFront();
        this.#knownIds.delete(event.id);
        return event;
    }

    nextScheduled() {
        if (this.#scheduled.size === 0) return null;
        const event = this.#scheduled.dequeue();
        this.#knownIds.delete(event.id);
        return event;
    }
}

async function processEvents(events, processor) {
    // Async iteration makes the consumer compatible with streaming producers.
    for await (const incoming of events) {
        processor.submit(incoming.event, incoming.options);
    }

    const handled = [];
    let event;

    while ((event = processor.nextUrgent()) !== null) {
        handled.push({ channel: "urgent", event });
    }

    while ((event = processor.nextScheduled()) !== null) {
        handled.push({ channel: "scheduled", event });
    }

    return handled;
}

async function* eventStream() {
    yield {
        event: { id: "INC-401", title: "Production outage", priority: 10 },
        options: { urgent: true }
    };
    yield {
        event: { id: "SEC-402", title: "Dependency vulnerability", priority: 9 },
        options: {}
    };
    yield {
        event: { id: "DOC-403", title: "Update runbook", priority: 2 },
        options: {}
    };
    yield {
        event: { id: "INC-404", title: "Database latency", priority: 8 },
        options: { urgent: true }
    };
}

function assert(condition, message) {
    if (!condition) throw new Error(`Assertion failed: ${message}`);
}

async function main() {
    const deque = new Deque();
    deque.pushBack("build");
    deque.pushBack("test");
    deque.pushFront("rollback");
    assert(deque.popFront() === "rollback", "front removal");
    assert(deque.popBack() === "test", "back removal");

    const minQueue = new StablePriorityQueue();
    minQueue.enqueue("routine", 2);
    minQueue.enqueue("urgent", 9);
    assert(minQueue.dequeue() === "routine", "min-priority order");

    const maxQueue = new StablePriorityQueue({ highestFirst: true });
    maxQueue.enqueue("routine", 2);
    maxQueue.enqueue("urgent", 9);
    assert(maxQueue.dequeue() === "urgent", "max-priority order");

    const cancellationQueue = new StablePriorityQueue({ highestFirst: true });
    const obsoleteId = cancellationQueue.enqueue("obsolete", 8);
    cancellationQueue.enqueue("security patch", 10);
    assert(cancellationQueue.cancel(obsoleteId), "cancellation succeeds");
    assert(cancellationQueue.dequeue() === "security patch", "cancelled entry skipped");

    const processor = new EngineeringEventProcessor();
    const handled = await processEvents(eventStream(), processor);

    console.log("Event processing order");
    for (const record of handled) {
        console.log(
            `${record.channel.padEnd(9)} ${record.event.id} ` +
            `priority=${record.event.priority}: ${record.event.title}`
        );
    }

    console.log("\nDeque and heap assertions passed.");
}

main().catch(error => {
    console.error("Processing failed:", error.message);
    process.exitCode = 1;
});
