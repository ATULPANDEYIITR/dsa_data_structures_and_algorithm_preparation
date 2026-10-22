"use strict";

/**
 * Recursion practice with explicit state validation, call tracing,
 * recursive algorithms, memoization, and an event-driven work queue.
 */

class RecursionInputError extends Error {}

function requireSafeInteger(value, name) {
    if (!Number.isSafeInteger(value)) {
        throw new RecursionInputError(`${name} must be a safe integer`);
    }
}

function factorial(n) {
    requireSafeInteger(n, "n");
    if (n < 0 || n > 170) {
        throw new RecursionInputError("n must be between 0 and 170");
    }
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

function createFibonacci() {
    const cache = new Map([[0, 0], [1, 1]]);

    function calculate(n) {
        requireSafeInteger(n, "n");
        if (n < 0 || n > 78) {
            throw new RecursionInputError("n must be between 0 and 78");
        }
        if (cache.has(n)) return cache.get(n);
        const result = calculate(n - 1) + calculate(n - 2);
        cache.set(n, result);
        return result;
    }

    return calculate;
}

const fibonacci = createFibonacci();

function power(base, exponent) {
    requireSafeInteger(base, "base");
    requireSafeInteger(exponent, "exponent");
    if (exponent < 0) {
        throw new RecursionInputError("Exponent must be non-negative");
    }
    if (exponent === 0) return 1;

    const half = power(base, Math.floor(exponent / 2));
    const squared = half * half;
    return exponent % 2 === 0 ? squared : base * squared;
}

function sumTo(n) {
    requireSafeInteger(n, "n");
    if (n < 0 || n > 1000) {
        throw new RecursionInputError("n must be between 0 and 1000");
    }
    if (n === 0) return 0;
    return n + sumTo(n - 1);
}

function reverseString(value) {
    if (typeof value !== "string") {
        throw new RecursionInputError("value must be a string");
    }
    // Array.from preserves Unicode code points, unlike indexing UTF-16 units.
    const characters = Array.from(value);
    function reverseAt(index) {
        if (index < 0) return "";
        return characters[index] + reverseAt(index - 1);
    }
    return reverseAt(characters.length - 1);
}

function reverseArray(values) {
    if (!Array.isArray(values)) {
        throw new RecursionInputError("values must be an array");
    }
    function reverseRange(left, right) {
        if (left >= right) return values.slice();
        const copy = values.slice();
        [copy[left], copy[right]] = [copy[right], copy[left]];
        return reverseRangeIn(copy, left + 1, right - 1);
    }
    function reverseRangeIn(copy, left, right) {
        if (left >= right) return copy;
        [copy[left], copy[right]] = [copy[right], copy[left]];
        return reverseRangeIn(copy, left + 1, right - 1);
    }
    return reverseRange(0, values.length - 1);
}

function sumArray(values, index = 0) {
    if (!Array.isArray(values)) {
        throw new RecursionInputError("values must be an array");
    }
    requireSafeInteger(index, "index");
    if (index < 0 || index > values.length) {
        throw new RecursionInputError("index is outside the array");
    }
    if (index === values.length) return 0;
    requireSafeInteger(values[index], "array element");
    return values[index] + sumArray(values, index + 1);
}

function binarySearch(sortedValues, target, left = 0, right = sortedValues.length - 1) {
    if (!Array.isArray(sortedValues)) {
        throw new RecursionInputError("sortedValues must be an array");
    }
    requireSafeInteger(target, "target");
    requireSafeInteger(left, "left");
    requireSafeInteger(right, "right");
    if (left < 0 || right >= sortedValues.length) {
        if (!(sortedValues.length === 0 && left === 0 && right === -1)) {
            throw new RecursionInputError("Invalid search boundaries");
        }
    }
    if (left > right) return -1;

    const middle = left + Math.floor((right - left) / 2);
    requireSafeInteger(sortedValues[middle], "array element");
    if (sortedValues[middle] === target) return middle;
    if (target < sortedValues[middle]) {
        return binarySearch(sortedValues, target, left, middle - 1);
    }
    return binarySearch(sortedValues, target, middle + 1, right);
}

class RecursionEventProcessor {
    #handlers = new Map();

    on(eventName, handler) {
        if (typeof handler !== "function") {
            throw new RecursionInputError("handler must be a function");
        }
        const handlers = this.#handlers.get(eventName) ?? [];
        handlers.push(handler);
        this.#handlers.set(eventName, handlers);
    }

    async emit(eventName, payload) {
        const handlers = this.#handlers.get(eventName) ?? [];
        // Await each handler to preserve event order and surface failures.
        for (const handler of handlers) {
            await handler(payload);
        }
    }
}

async function run() {
    const checks = [
        ["factorial", () => factorial(5), 120],
        ["fibonacci", () => fibonacci(10), 55],
        ["power", () => power(2, 10), 1024],
        ["sum", () => sumTo(10), 55],
        ["reverse string", () => reverseString("recursion"), "noisrucer"],
        ["reverse array", () => reverseArray([1, 2, 3]), [3, 2, 1]],
        ["array sum", () => sumArray([2, 4, 6]), 12],
        ["binary search", () => binarySearch([1, 3, 5, 7], 5), 2],
    ];

    for (const [name, calculate, expected] of checks) {
        const actual = calculate();
        if (JSON.stringify(actual) !== JSON.stringify(expected)) {
            throw new Error(`${name} failed: expected ${expected}, received ${actual}`);
        }
        console.log(`${name}: ${JSON.stringify(actual)}`);
    }

    for (const invalid of [
        () => factorial(-1),
        () => fibonacci(-1),
        () => power(2, -1),
        () => sumArray([1], 2),
    ]) {
        let rejected = false;
        try {
            invalid();
        } catch (error) {
            if (!(error instanceof RecursionInputError)) throw error;
            rejected = true;
        }
        if (!rejected) throw new Error("Invalid input was accepted");
    }

    const processor = new RecursionEventProcessor();
    const events = [];
    processor.on("frame", async (frame) => {
        events.push(`enter:${frame.depth}`);
    });
    processor.on("frame", async (frame) => {
        events.push(`exit:${frame.depth}`);
    });

    async function trace(n, depth = 0) {
        const frame = Object.freeze({ n, depth });
        await processor.emit("frame", frame);
        if (n > 0) await trace(n - 1, depth + 1);
    }

    await trace(2);
    console.log(`event sequence: ${events.join(", ")}`);
    console.log("All JavaScript recursion checks passed.");
}

run().catch((error) => {
    console.error(`Execution failed: ${error.message}`);
    process.exitCode = 1;
});
