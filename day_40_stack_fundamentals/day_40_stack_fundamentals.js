"use strict";

/*
 * Stack fundamentals in JavaScript.
 *
 * Run with:
 *   node stack_fundamentals.js
 *
 * This implementation focuses on array-backed stacks, linked nodes,
 * browser-style navigation history, and asynchronous work scheduling.
 */

class StackUnderflowError extends Error {
    constructor(message = "Cannot access an empty stack.") {
        super(message);
        this.name = "StackUnderflowError";
    }
}

class StackOverflowError extends Error {
    constructor(message = "Stack capacity exceeded.") {
        super(message);
        this.name = "StackOverflowError";
    }
}

class ArrayStack {
    #items = [];
    #capacity;

    constructor(capacity = Infinity) {
        if (
            capacity !== Infinity &&
            (!Number.isSafeInteger(capacity) || capacity < 0)
        ) {
            throw new RangeError("Capacity must be a non-negative safe integer.");
        }
        this.#capacity = capacity;
    }

    push(value) {
        if (this.#items.length >= this.#capacity) {
            throw new StackOverflowError();
        }
        this.#items.push(value);
        return this.#items.length;
    }

    pop() {
        if (this.isEmpty()) {
            throw new StackUnderflowError("Cannot pop from an empty stack.");
        }
        return this.#items.pop();
    }

    peek() {
        if (this.isEmpty()) {
            throw new StackUnderflowError("Cannot peek at an empty stack.");
        }
        return this.#items[this.#items.length - 1];
    }

    isEmpty() {
        return this.#items.length === 0;
    }

    get size() {
        return this.#items.length;
    }

    // Return a detached copy so callers cannot mutate internal storage.
    snapshot() {
        return [...this.#items];
    }

    *[Symbol.iterator]() {
        for (let index = this.#items.length - 1; index >= 0; index--) {
            yield this.#items[index];
        }
    }
}

class LinkedNode {
    constructor(value, next = null) {
        this.value = value;
        this.next = next;
    }
}

class LinkedListStack {
    #top = null;
    #size = 0;

    push(value) {
        this.#top = new LinkedNode(value, this.#top);
        this.#size++;
        return this.#size;
    }

    pop() {
        if (this.isEmpty()) {
            throw new StackUnderflowError("Cannot pop from an empty stack.");
        }

        const removed = this.#top;
        this.#top = removed.next;
        removed.next = null;
        this.#size--;
        return removed.value;
    }

    peek() {
        if (this.isEmpty()) {
            throw new StackUnderflowError("Cannot peek at an empty stack.");
        }
        return this.#top.value;
    }

    isEmpty() {
        return this.#size === 0;
    }

    get size() {
        return this.#size;
    }

    snapshot() {
        const values = [];
        for (const value of this) {
            values.push(value);
        }
        return values;
    }

    *[Symbol.iterator]() {
        let node = this.#top;
        while (node !== null) {
            yield node.value;
            node = node.next;
        }
    }
}

/*
 * Browser navigation illustrates why a stack is useful:
 * visiting a page saves the current page in the back history.
 * Going back transfers the current page to forward history.
 * Visiting a new page clears forward history.
 */
class NavigationHistory {
    #back = new ArrayStack();
    #forward = new ArrayStack();
    #current;

    constructor(initialUrl) {
        this.#validateUrl(initialUrl);
        this.#current = initialUrl;
    }

    #validateUrl(url) {
        if (typeof url !== "string" || url.trim() === "") {
            throw new TypeError("A non-empty URL string is required.");
        }
    }

    visit(url) {
        this.#validateUrl(url);
        this.#back.push(this.#current);
        this.#current = url;
        this.#forward = new ArrayStack();
        return this.state();
    }

    back() {
        if (this.#back.isEmpty()) {
            return this.state();
        }
        this.#forward.push(this.#current);
        this.#current = this.#back.pop();
        return this.state();
    }

    forward() {
        if (this.#forward.isEmpty()) {
            return this.state();
        }
        this.#back.push(this.#current);
        this.#current = this.#forward.pop();
        return this.state();
    }

    state() {
        return Object.freeze({
            current: this.#current,
            backAvailable: !this.#back.isEmpty(),
            forwardAvailable: !this.#forward.isEmpty(),
            backStack: this.#back.snapshot(),
            forwardStack: this.#forward.snapshot()
        });
    }
}

/*
 * A small asynchronous worker consumes jobs in LIFO order.
 * This is useful for understanding stack-based task processing, but it
 * is intentionally not a FIFO queue and should not replace one when
 * fairness or arrival order is required.
 */
class AsyncLifoWorker {
    #pending = new ArrayStack();
    #running = false;

    submit(job) {
        if (typeof job !== "function") {
            throw new TypeError("A job must be a function.");
        }
        this.#pending.push(job);
    }

    async drain() {
        if (this.#running) {
            throw new Error("A drain operation is already running.");
        }

        this.#running = true;
        const results = [];

        try {
            while (!this.#pending.isEmpty()) {
                const job = this.#pending.pop();
                // Await each job before starting the next one to preserve
                // deterministic sequential LIFO processing.
                results.push(await job());
            }
            return results;
        } finally {
            this.#running = false;
        }
    }

    get pendingCount() {
        return this.#pending.size;
    }
}

function check(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

async function main() {
    console.log("ARRAY STACK");
    const arrayStack = new ArrayStack(3);
    arrayStack.push("compile");
    arrayStack.push("test");
    arrayStack.push("deploy");
    console.log("Top:", arrayStack.peek());
    console.log("Pop:", arrayStack.pop());
    console.log("Remaining top-first:", [...arrayStack]);

    console.log("\nLINKED-LIST STACK");
    const linkedStack = new LinkedListStack();
    linkedStack.push({ id: "task-1" });
    linkedStack.push({ id: "task-2" });
    console.log("Top task:", linkedStack.peek());
    console.log("Removed task:", linkedStack.pop());
    console.log("Size:", linkedStack.size);

    console.log("\nCAPACITY AND UNDERFLOW");
    try {
        arrayStack.push("extra");
        arrayStack.push("overflow");
    } catch (error) {
        console.log(error.name + ":", error.message);
    }

    while (!arrayStack.isEmpty()) {
        arrayStack.pop();
    }

    try {
        arrayStack.pop();
    } catch (error) {
        console.log(error.name + ":", error.message);
    }

    console.log("\nNAVIGATION HISTORY");
    const browser = new NavigationHistory("https://example.com");
    browser.visit("https://example.com/products");
    browser.visit("https://example.com/products/stack");
    console.log("Current:", browser.state().current);
    console.log("Back:", browser.back().current);
    console.log("Forward:", browser.forward().current);
    browser.back();
    browser.visit("https://example.com/contact");
    console.log("Forward after new visit:", browser.state().forwardAvailable);

    console.log("\nASYNC LIFO WORKER");
    const worker = new AsyncLifoWorker();
    worker.submit(async () => "first submitted");
    worker.submit(async () => "second submitted");
    worker.submit(async () => "third submitted");
    console.log(await worker.drain());

    console.log("\nSELF-CHECKS");
    const stack = new ArrayStack();
    check(stack.isEmpty(), "new stack must be empty");
    stack.push(0);
    stack.push(false);
    stack.push(null);
    check(stack.size === 3, "falsy values must remain valid elements");
    check(stack.pop() === null, "null must be popped as a value");
    check(stack.pop() === false, "false must be popped as a value");
    check(stack.pop() === 0, "zero must be popped as a value");
    check(stack.isEmpty(), "all values were removed");
    console.log("All checks passed.");
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
