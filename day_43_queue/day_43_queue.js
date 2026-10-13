"use strict";

/*
 * Queue: FIFO Data Structure
 *
 * Implements Queue, Enqueue, Dequeue, Front, and Rear.
 * Also demonstrates asynchronous processing, bounded queues,
 * event-driven notifications, and queue behavior under failures.
 *
 * Run with Node.js:
 *   node queue_implementation.js
 */

class QueueEmptyError extends Error {
  constructor(message = "Cannot remove or inspect an element in an empty queue.") {
    super(message);
    this.name = "QueueEmptyError";
  }
}

class QueueFullError extends Error {
  constructor(message = "Queue capacity has been reached.") {
    super(message);
    this.name = "QueueFullError";
  }
}

class Queue {
  constructor(iterable = []) {
    this._items = [];
    this._head = 0;

    for (const item of iterable) {
      this.enqueue(item);
    }
  }

  enqueue(item) {
    this._items.push(item);
    return this.size();
  }

  dequeue() {
    if (this.isEmpty()) {
      throw new QueueEmptyError();
    }

    const item = this._items[this._head];
    this._items[this._head] = undefined;
    this._head += 1;

    // Periodically compact the array so removed entries do not accumulate.
    // Dequeue remains amortized O(1), rather than shifting on every call.
    if (this._head >= 64 && this._head * 2 >= this._items.length) {
      this._items = this._items.slice(this._head);
      this._head = 0;
    }

    return item;
  }

  front() {
    if (this.isEmpty()) {
      throw new QueueEmptyError("Cannot inspect the front of an empty queue.");
    }
    return this._items[this._head];
  }

  rear() {
    if (this.isEmpty()) {
      throw new QueueEmptyError("Cannot inspect the rear of an empty queue.");
    }
    return this._items[this._items.length - 1];
  }

  size() {
    return this._items.length - this._head;
  }

  isEmpty() {
    return this.size() === 0;
  }

  clear() {
    this._items = [];
    this._head = 0;
  }

  toArray() {
    return this._items.slice(this._head);
  }

  [Symbol.iterator]() {
    return this.toArray()[Symbol.iterator]();
  }
}

class BoundedQueue extends Queue {
  constructor(capacity) {
    super();

    if (!Number.isSafeInteger(capacity) || capacity <= 0) {
      throw new TypeError("Capacity must be a positive safe integer.");
    }

    this.capacity = capacity;
  }

  enqueue(item) {
    if (this.size() >= this.capacity) {
      throw new QueueFullError();
    }
    return super.enqueue(item);
  }

  isFull() {
    return this.size() === this.capacity;
  }
}

class EventQueue extends Queue {
  constructor() {
    super();
    this.listeners = new Map();
  }

  on(eventName, listener) {
    if (typeof listener !== "function") {
      throw new TypeError("Listener must be a function.");
    }

    if (!this.listeners.has(eventName)) {
      this.listeners.set(eventName, new Set());
    }

    this.listeners.get(eventName).add(listener);

    return () => this.listeners.get(eventName)?.delete(listener);
  }

  emit(eventName, payload) {
    for (const listener of this.listeners.get(eventName) ?? []) {
      listener(payload);
    }
  }

  enqueue(item) {
    const size = super.enqueue(item);
    this.emit("enqueue", { item, size });
    return size;
  }

  dequeue() {
    const item = super.dequeue();
    this.emit("dequeue", { item, size: this.size() });
    return item;
  }
}

class AsyncWorkQueue {
  constructor(worker, concurrency = 2) {
    if (typeof worker !== "function") {
      throw new TypeError("Worker must be a function.");
    }

    if (!Number.isSafeInteger(concurrency) || concurrency <= 0) {
      throw new TypeError("Concurrency must be a positive integer.");
    }

    this.worker = worker;
    this.concurrency = concurrency;
    this.pending = new Queue();
    this.active = 0;
    this.closed = false;
    this.idleWaiters = [];
  }

  enqueue(task) {
    if (this.closed) {
      throw new Error("Cannot enqueue work after the queue has closed.");
    }

    if (typeof task !== "function") {
      throw new TypeError("Each task must be a function.");
    }

    return new Promise((resolve, reject) => {
      this.pending.enqueue({ task, resolve, reject });
      this._pump();
    });
  }

  _pump() {
    while (this.active < this.concurrency && !this.pending.isEmpty()) {
      const entry = this.pending.dequeue();
      this.active += 1;

      Promise.resolve()
        .then(() => this.worker(entry.task))
        .then(entry.resolve, entry.reject)
        .finally(() => {
          this.active -= 1;
          this._pump();
          this._notifyIdleIfNeeded();
        });
    }

    this._notifyIdleIfNeeded();
  }

  _notifyIdleIfNeeded() {
    if (this.active === 0 && this.pending.isEmpty()) {
      const waiters = this.idleWaiters.splice(0);
      for (const resolve of waiters) {
        resolve();
      }
    }
  }

  onIdle() {
    if (this.active === 0 && this.pending.isEmpty()) {
      return Promise.resolve();
    }

    return new Promise((resolve) => this.idleWaiters.push(resolve));
  }

  async close() {
    this.closed = true;
    await this.onIdle();
  }

  get pendingCount() {
    return this.pending.size();
  }

  get activeCount() {
    return this.active;
  }
}

async function runExamples() {
  console.log("Basic FIFO queue");

  const queue = new Queue(["build", "test", "release"]);
  console.log("Initial queue:", queue.toArray());
  console.log("Front:", queue.front());
  console.log("Rear:", queue.rear());
  console.log("Dequeue:", queue.dequeue());
  console.log("Remaining:", queue.toArray());

  console.log("\nBounded queue");
  const bounded = new BoundedQueue(2);
  bounded.enqueue("request-101");
  bounded.enqueue("request-102");

  try {
    bounded.enqueue("request-103");
  } catch (error) {
    console.log(error.name + ":", error.message);
  }

  console.log("Removed:", bounded.dequeue());
  bounded.enqueue("request-103");
  console.log("After reuse:", bounded.toArray());

  console.log("\nEvent-driven queue");
  const events = new EventQueue();

  const unsubscribe = events.on("enqueue", ({ item, size }) => {
    console.log(`Added ${item}; queue size is ${size}`);
  });

  events.on("dequeue", ({ item, size }) => {
    console.log(`Removed ${item}; queue size is ${size}`);
  });

  events.enqueue("compile");
  events.enqueue("unit-test");
  console.log("Front:", events.front());
  console.log("Dequeued:", events.dequeue());
  unsubscribe();

  console.log("\nAsynchronous worker queue");
  const workQueue = new AsyncWorkQueue(async (task) => {
    // A real worker could perform a network call, build, or data operation.
    // This example returns results without depending on external services.
    return task();
  }, 2);

  const results = await Promise.all([
    workQueue.enqueue(async () => ({ job: "build", status: "completed" })),
    workQueue.enqueue(async () => ({ job: "test", status: "completed" })),
    workQueue.enqueue(async () => {
      throw new Error("Deployment validation failed.");
    }),
    workQueue.enqueue(async () => ({ job: "package", status: "completed" }))
  ].map((promise) => promise.catch((error) => ({
    status: "failed",
    reason: error.message
  }))));

  await workQueue.close();

  console.log("Task results:", results);
  console.log("Active workers:", workQueue.activeCount);
  console.log("Pending tasks:", workQueue.pendingCount);

  console.log("\nEmpty queue handling");
  const empty = new Queue();

  try {
    empty.dequeue();
  } catch (error) {
    console.log(error.name + ":", error.message);
  }
}

function runAssertions() {
  const queue = new Queue([1, 2, 3]);

  console.assert(queue.front() === 1, "Front should be the first item.");
  console.assert(queue.rear() === 3, "Rear should be the last item.");
  console.assert(queue.dequeue() === 1, "Dequeue should preserve FIFO order.");
  console.assert(queue.toArray().join(",") === "2,3", "Remaining order is incorrect.");

  const bounded = new BoundedQueue(1);
  bounded.enqueue("one");
  console.assert(bounded.isFull(), "Bounded queue should report full.");

  try {
    bounded.enqueue("two");
    console.assert(false, "Expected QueueFullError.");
  } catch (error) {
    console.assert(error instanceof QueueFullError);
  }

  console.log("Queue assertions passed.");
}

runAssertions();
runExamples().catch((error) => {
  console.error("Example execution failed:", error);
  process.exitCode = 1;
});
