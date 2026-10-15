"use strict";

/*
 * Stack and queue assessment using event-driven workflow simulation,
 * monotonic data structures, and executable assertions.
 */

const assert = require("node:assert/strict");

class EventQueue {
    #events = [];
    #head = 0;

    enqueue(event) {
        if (event === null || typeof event !== "object") {
            throw new TypeError("An event must be an object");
        }
        this.#events.push(Object.freeze({ ...event }));
    }

    dequeue() {
        if (this.isEmpty()) {
            throw new RangeError("The event queue is empty");
        }

        const event = this.#events[this.#head++];

        // Periodic compaction avoids repeatedly shifting an array.
        if (this.#head >= 64 && this.#head * 2 >= this.#events.length) {
            this.#events = this.#events.slice(this.#head);
            this.#head = 0;
        }

        return event;
    }

    isEmpty() {
        return this.#head >= this.#events.length;
    }

    get size() {
        return this.#events.length - this.#head;
    }
}

class UndoHistory {
    #undo = [];
    #redo = [];
    #state = "";

    apply(change) {
        if (typeof change !== "string" || change.length === 0) {
            throw new TypeError("A non-empty change description is required");
        }

        this.#undo.push(this.#state);
        this.#state = change;
        this.#redo.length = 0;
    }

    undo() {
        if (this.#undo.length === 0) {
            return false;
        }

        this.#redo.push(this.#state);
        this.#state = this.#undo.pop();
        return true;
    }

    redo() {
        if (this.#redo.length === 0) {
            return false;
        }

        this.#undo.push(this.#state);
        this.#state = this.#redo.pop();
        return true;
    }

    get state() {
        return this.#state;
    }
}

function validateBrackets(source) {
    const pairs = new Map([
        [")", "("],
        ["]", "["],
        ["}", "{"],
    ]);
    const opening = new Set(pairs.values());
    const stack = [];

    for (const character of source) {
        if (opening.has(character)) {
            stack.push(character);
        } else if (pairs.has(character)) {
            if (stack.pop() !== pairs.get(character)) {
                return false;
            }
        }
    }

    return stack.length === 0;
}

function nextGreaterIndices(values) {
    const result = Array(values.length).fill(-1);
    const stack = [];

    for (let index = 0; index < values.length; index++) {
        while (
            stack.length > 0 &&
            values[stack[stack.length - 1]] < values[index]
        ) {
            result[stack.pop()] = index;
        }
        stack.push(index);
    }

    return result;
}

function maximumInWindows(values, width) {
    if (
        !Number.isInteger(width) ||
        width < 1 ||
        width > values.length
    ) {
        throw new RangeError("Invalid sliding-window width");
    }

    const candidates = [];
    let head = 0;
    const output = [];

    for (let index = 0; index < values.length; index++) {
        while (
            head < candidates.length &&
            candidates[head] <= index - width
        ) {
            head++;
        }

        while (
            candidates.length > head &&
            values[candidates[candidates.length - 1]] <= values[index]
        ) {
            candidates.pop();
        }

        candidates.push(index);

        if (index >= width - 1) {
            output.push(values[candidates[head]]);
        }

        // Remove consumed prefix entries before they grow indefinitely.
        if (head >= 64 && head * 2 >= candidates.length) {
            candidates.splice(0, head);
            head = 0;
        }
    }

    return output;
}

function processEvents(events, handler) {
    const queue = new EventQueue();
    const processed = [];

    for (const event of events) {
        queue.enqueue(event);
    }

    while (!queue.isEmpty()) {
        const event = queue.dequeue();

        // A failed handler does not silently mark the event successful.
        const result = handler(event);
        processed.push({ event, result });
    }

    return processed;
}

function runAssessment() {
    console.log("Event-driven queue");

    const events = [
        { type: "PUSH", value: 14 },
        { type: "PUSH", value: 27 },
        { type: "PEEK" },
        { type: "POP" },
    ];

    const stack = [];

    const results = processEvents(events, (event) => {
        switch (event.type) {
            case "PUSH":
                if (!Number.isSafeInteger(event.value)) {
                    throw new TypeError("Stack values must be safe integers");
                }
                stack.push(event.value);
                return "pushed";
            case "PEEK":
                if (stack.length === 0) {
                    throw new RangeError("Cannot peek at an empty stack");
                }
                return stack[stack.length - 1];
            case "POP":
                if (stack.length === 0) {
                    throw new RangeError("Cannot pop an empty stack");
                }
                return stack.pop();
            default:
                throw new TypeError(`Unsupported event: ${event.type}`);
        }
    });

    console.log(results);
    assert.deepEqual(results.map((entry) => entry.result), [
        "pushed", "pushed", 27, 27,
    ]);

    console.log("\nUndo and redo");

    const history = new UndoHistory();
    history.apply("initial draft");
    history.apply("draft with tests");

    assert.equal(history.state, "draft with tests");
    assert.equal(history.undo(), true);
    assert.equal(history.state, "initial draft");
    assert.equal(history.redo(), true);
    assert.equal(history.state, "draft with tests");
    console.log("Undo/redo transitions passed");

    console.log("\nAssessment algorithms");

    assert.equal(validateBrackets("{[()]}"), true);
    assert.equal(validateBrackets("([)]"), false);
    assert.deepEqual(nextGreaterIndices([2, 1, 2, 4, 3]), [3, 2, 3, -1, -1]);
    assert.deepEqual(
        maximumInWindows([1, 3, -1, -3, 5, 3, 6, 7], 3),
        [3, 3, 5, 5, 6, 7]
    );

    console.log("Bracket validation passed");
    console.log("Next-greater indices:", nextGreaterIndices([2, 1, 2, 4, 3]));
    console.log(
        "Window maxima:",
        maximumInWindows([1, 3, -1, -3, 5, 3, 6, 7], 3)
    );

    assert.throws(() => maximumInWindows([1, 2], 0), RangeError);
    assert.throws(
        () => processEvents([{ type: "UNKNOWN" }], () => {
            throw new TypeError("Unknown event");
        }),
        TypeError
    );

    console.log("\nAll JavaScript assessment cases passed.");
}

runAssessment();
