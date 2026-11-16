"use strict";

/*
 * Heap sort, K-way merging, and multiway merging.
 * Runtime: Node.js 18 or later.
 * Dependencies: Node.js standard library only.
 */

const fs = require("node:fs/promises");
const { performance } = require("node:perf_hooks");
const { EventEmitter } = require("node:events");

const MergeStrategy = Object.freeze({
    HEAP: "heap",
    PAIRWISE: "pairwise"
});

class MinHeap {
    constructor(compare = (a, b) => a - b) {
        if (typeof compare !== "function") {
            throw new TypeError("Comparator must be a function.");
        }

        this.items = [];
        this.compare = compare;
    }

    get size() {
        return this.items.length;
    }

    peek() {
        return this.items.length === 0 ? undefined : this.items[0];
    }

    push(value) {
        const items = this.items;
        items.push(value);

        let index = items.length - 1;

        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);

            if (this.compare(items[index], items[parent]) >= 0) {
                break;
            }

            [items[index], items[parent]] = [
                items[parent],
                items[index]
            ];

            index = parent;
        }
    }

    pop() {
        if (this.items.length === 0) {
            throw new Error("Cannot remove from an empty heap.");
        }

        const root = this.items[0];
        const last = this.items.pop();

        if (this.items.length > 0) {
            this.items[0] = last;
            this._siftDown(0);
        }

        return root;
    }

    _siftDown(start) {
        let index = start;
        const items = this.items;

        while (true) {
            const left = 2 * index + 1;
            const right = 2 * index + 2;

            let smallest = index;

            if (
                left < items.length &&
                this.compare(items[left], items[smallest]) < 0
            ) {
                smallest = left;
            }

            if (
                right < items.length &&
                this.compare(items[right], items[smallest]) < 0
            ) {
                smallest = right;
            }

            if (smallest === index) {
                break;
            }

            [items[index], items[smallest]] = [
                items[smallest],
                items[index]
            ];

            index = smallest;
        }
    }
}

class HeapAlgorithms {
    static validateIntegerArray(values) {
        if (!Array.isArray(values)) {
            throw new TypeError("Expected an array.");
        }

        if (!values.every(Number.isSafeInteger)) {
            throw new TypeError(
                "Every element must be a safe JavaScript integer."
            );
        }
    }

    static heapSort(values, descending = false) {
        this.validateIntegerArray(values);

        const array = [...values];
        const n = array.length;

        const siftDown = (root, heapSize) => {
            let current = root;

            while (true) {
                let largest = current;
                const left = current * 2 + 1;
                const right = current * 2 + 2;

                if (
                    left < heapSize &&
                    array[left] > array[largest]
                ) {
                    largest = left;
                }

                if (
                    right < heapSize &&
                    array[right] > array[largest]
                ) {
                    largest = right;
                }

                if (largest === current) {
                    break;
                }

                [array[current], array[largest]] = [
                    array[largest],
                    array[current]
                ];

                current = largest;
            }
        };

        // Build the max heap in linear time.
        for (let i = Math.floor(n / 2) - 1; i >= 0; i--) {
            siftDown(i, n);
        }

        for (let end = n - 1; end > 0; end--) {
            [array[0], array[end]] = [array[end], array[0]];
            siftDown(0, end);
        }

        return descending ? array.reverse() : array;
    }

    static validateSortedLists(lists) {
        if (!Array.isArray(lists)) {
            throw new TypeError("Expected an array of sorted arrays.");
        }

        lists.forEach((list, source) => {
            this.validateIntegerArray(list);

            for (let i = 1; i < list.length; i++) {
                if (list[i - 1] > list[i]) {
                    throw new RangeError(
                        `Source ${source} is not sorted at index ${i}.`
                    );
                }
            }
        });
    }

    static mergeTwo(left, right) {
        this.validateIntegerArray(left);
        this.validateIntegerArray(right);

        for (let i = 1; i < left.length; i++) {
            if (left[i - 1] > left[i]) {
                throw new RangeError("Left input is not sorted.");
            }
        }

        for (let i = 1; i < right.length; i++) {
            if (right[i - 1] > right[i]) {
                throw new RangeError("Right input is not sorted.");
            }
        }

        const result = [];
        let i = 0;
        let j = 0;

        while (i < left.length && j < right.length) {
            if (left[i] <= right[j]) {
                result.push(left[i++]);
            } else {
                result.push(right[j++]);
            }
        }

        return result.concat(left.slice(i), right.slice(j));
    }

    static mergeKHeap(lists) {
        this.validateSortedLists(lists);

        const heap = new MinHeap((a, b) => {
            if (a.value !== b.value) {
                return a.value - b.value;
            }

            if (a.source !== b.source) {
                return a.source - b.source;
            }

            return a.index - b.index;
        });

        let totalElements = 0;

        lists.forEach((list, source) => {
            totalElements += list.length;

            if (list.length > 0) {
                heap.push({
                    value: list[0],
                    source,
                    index: 0
                });
            }
        });

        const output = [];

        while (heap.size > 0) {
            const current = heap.pop();

            output.push(current.value);

            const nextIndex = current.index + 1;
            const source = lists[current.source];

            if (nextIndex < source.length) {
                heap.push({
                    value: source[nextIndex],
                    source: current.source,
                    index: nextIndex
                });
            }
        }

        if (output.length !== totalElements) {
            throw new Error("Merge element-count invariant failed.");
        }

        return output;
    }

    static mergeKPairwise(lists) {
        this.validateSortedLists(lists);

        let active = lists.map(list => [...list]);

        if (active.length === 0) {
            return [];
        }

        while (active.length > 1) {
            const next = [];

            for (let i = 0; i < active.length; i += 2) {
                if (i + 1 < active.length) {
                    next.push(this.mergeTwo(active[i], active[i + 1]));
                } else {
                    next.push(active[i]);
                }
            }

            active = next;
        }

        return active[0];
    }

    static mergeK(lists, strategy = MergeStrategy.HEAP) {
        const started = performance.now();

        let output;

        if (strategy === MergeStrategy.HEAP) {
            output = this.mergeKHeap(lists);
        } else if (strategy === MergeStrategy.PAIRWISE) {
            output = this.mergeKPairwise(lists);
        } else {
            throw new RangeError("Unknown merge strategy.");
        }

        return {
            values: output,
            statistics: {
                inputLists: lists.length,
                totalElements: output.length,
                strategy,
                elapsedMilliseconds: performance.now() - started
            }
        };
    }
}

/*
 * An event-driven merge service.
 *
 * Each source can be registered independently. Once all sources
 * have been supplied, the service publishes a merged result.
 */
class MergeCoordinator extends EventEmitter {
    constructor(expectedSources) {
        super();

        if (!Number.isInteger(expectedSources) || expectedSources < 1) {
            throw new RangeError("Expected source count must be positive.");
        }

        this.expectedSources = expectedSources;
        this.sources = new Map();
        this.completed = false;
    }

    registerSource(sourceId, sortedValues) {
        if (this.completed) {
            throw new Error("Merge operation is already completed.");
        }

        if (
            typeof sourceId !== "string" ||
            sourceId.trim().length === 0
        ) {
            throw new TypeError("Source ID must be a non-empty string.");
        }

        if (this.sources.has(sourceId)) {
            throw new Error(`Duplicate source: ${sourceId}`);
        }

        HeapAlgorithms.validateSortedLists([sortedValues]);

        if (this.sources.size >= this.expectedSources) {
            throw new Error("Too many sources registered.");
        }

        this.sources.set(sourceId, [...sortedValues]);

        this.emit("sourceRegistered", {
            sourceId,
            elementCount: sortedValues.length
        });

        if (this.sources.size === this.expectedSources) {
            this.completed = true;

            const result = HeapAlgorithms.mergeK(
                [...this.sources.values()]
            );

            this.emit("merged", result);
            return result;
        }

        return null;
    }

    getProgress() {
        return {
            registered: this.sources.size,
            expected: this.expectedSources,
            complete: this.completed
        };
    }
}

/*
 * Asynchronous chunk sorting and multiway merging.
 * A concurrency limit prevents unbounded scheduling.
 */
async function externalStyleMerge(values, chunkSize = 1000) {
    if (!Number.isSafeInteger(chunkSize) || chunkSize <= 0) {
        throw new RangeError("Chunk size must be positive.");
    }

    HeapAlgorithms.validateIntegerArray(values);

    const chunks = [];

    for (let i = 0; i < values.length; i += chunkSize) {
        chunks.push(
            HeapAlgorithms.heapSort(
                values.slice(i, i + chunkSize)
            )
        );

        // Yield control periodically in event-driven applications.
        if (chunks.length % 8 === 0) {
            await new Promise(resolve => setImmediate(resolve));
        }
    }

    return HeapAlgorithms.mergeKHeap(chunks);
}

async function saveJSON(filename, data) {
    const temporary = `${filename}.tmp`;

    try {
        await fs.writeFile(
            temporary,
            JSON.stringify(data, null, 2),
            { encoding: "utf8", flag: "w" }
        );

        await fs.rename(temporary, filename);
    } catch (error) {
        await fs.unlink(temporary).catch(() => {});
        throw error;
    }
}

function runTests() {
    const input = [45, 12, 89, 3, 67, 21, 90, 4, 45];

    const sorted = HeapAlgorithms.heapSort(input);

    console.log("Heap sort:", sorted);

    if (JSON.stringify(sorted) !== JSON.stringify([...input].sort((a, b) => a - b))) {
        throw new Error("Heap sort test failed.");
    }

    const sources = [
        [1, 4, 7, 10],
        [2, 5, 8, 11],
        [3, 6, 9, 12],
        [0, 13, 15]
    ];

    const heapResult = HeapAlgorithms.mergeKHeap(sources);
    const pairwiseResult = HeapAlgorithms.mergeKPairwise(sources);

    console.log("Heap merge:", heapResult);
    console.log("Pairwise merge:", pairwiseResult);

    if (JSON.stringify(heapResult) !== JSON.stringify(pairwiseResult)) {
        throw new Error("Merge strategies disagree.");
    }

    const edgeCases = [
        [],
        [[]],
        [[], [], []],
        [[1, 1, 1], [1, 1], [1]],
        [[-10, -5], [-8, 0], [2, 3]]
    ];

    for (const test of edgeCases) {
        console.log("Edge case:", HeapAlgorithms.mergeKHeap(test));
    }

    try {
        HeapAlgorithms.mergeKHeap([[1, 5, 3], [2, 4]]);
        throw new Error("Unsorted-input validation failed.");
    } catch (error) {
        if (!(error instanceof RangeError)) {
            throw error;
        }

        console.log("Correctly rejected unsorted input.");
    }

    const coordinator = new MergeCoordinator(2);

    coordinator.on("sourceRegistered", event => {
        console.log("Source registered:", event);
    });

    coordinator.on("merged", result => {
        console.log("Event-driven result:", result.values);
    });

    coordinator.registerSource("database-A", [1, 4, 7]);
    coordinator.registerSource("database-B", [2, 3, 8]);

    return externalStyleMerge(
        [19, 4, 7, 2, 15, 1, 8, 3, 11, 6],
        3
    );
}

async function main() {
    const externalResult = await runTests();

    console.log("External-style merge:", externalResult);

    await saveJSON("heap_merge_results.json", {
        algorithm: "heap-sort-and-multiway-merge",
        sortedValues: externalResult,
        generatedAt: new Date().toISOString()
    });

    console.log("All JavaScript checks passed.");
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
