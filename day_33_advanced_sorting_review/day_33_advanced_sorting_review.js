'use strict';

/*
 * Advanced Sorting Review
 *
 * This Node.js-compatible file complements the Python implementation by
 * emphasizing JavaScript-specific structures and execution patterns:
 *
 * - array-based heap construction
 * - counting sort with typed arrays
 * - stable record sorting
 * - event-driven review of sorting jobs
 * - sorting as a preprocessing step for problem solving
 * - validation and asynchronous benchmarking
 *
 * Run with:
 *   node advanced-sorting-review.js
 */


// ---------------------------------------------------------------------------
// Validation and shared utilities
// ---------------------------------------------------------------------------

function validateIntegerArray(values) {
    if (!Array.isArray(values)) {
        throw new TypeError('expected an array');
    }

    for (const value of values) {
        // Number.isInteger avoids JavaScript's implicit conversion behavior.
        // NaN, Infinity, strings, and booleans are rejected.
        if (!Number.isInteger(value)) {
            throw new TypeError(
                `all values must be integers; received ${String(value)}`
            );
        }
    }

    return [...values];
}

function isSorted(values) {
    for (let i = 1; i < values.length; i += 1) {
        if (values[i - 1] > values[i]) {
            return false;
        }
    }

    return true;
}

function assertSortedAndPreserved(sorter, values) {
    const original = [...values];
    const result = sorter(values);

    if (!isSorted(result)) {
        throw new Error(`${sorter.name} returned unsorted data`);
    }

    const left = [...original].sort((a, b) => a - b);
    const right = [...result].sort((a, b) => a - b);

    if (JSON.stringify(left) !== JSON.stringify(right)) {
        throw new Error(`${sorter.name} did not preserve all elements`);
    }

    return result;
}


// ---------------------------------------------------------------------------
// Counting sort
// ---------------------------------------------------------------------------

function countingSort(values, options = {}) {
    const data = validateIntegerArray(values);

    if (data.length <= 1) {
        return data;
    }

    const {
        stable = true,
        maxRangeRatio = 50
    } = options;

    let minimum = data[0];
    let maximum = data[0];

    for (const value of data) {
        minimum = Math.min(minimum, value);
        maximum = Math.max(maximum, value);
    }

    const range = maximum - minimum + 1;

    if (!Number.isSafeInteger(range) || range <= 0) {
        throw new RangeError('numeric range cannot be represented safely');
    }

    /*
     * A normal JavaScript Array could allocate a huge sparse structure.
     * A range guard makes the algorithm fail explicitly when the numeric
     * domain is inappropriate for counting sort.
     */
    if (range > Math.max(1, data.length * maxRangeRatio)) {
        throw new RangeError(
            `counting sort rejected sparse range: n=${data.length}, k=${range}`
        );
    }

    // Uint32Array is appropriate because each count is non-negative.
    const counts = new Uint32Array(range);

    for (const value of data) {
        counts[value - minimum] += 1;
    }

    if (!stable) {
        const result = [];

        for (let offset = 0; offset < counts.length; offset += 1) {
            for (let occurrence = 0; occurrence < counts[offset]; occurrence += 1) {
                result.push(offset + minimum);
            }
        }

        return result;
    }

    // Convert frequency counts into cumulative end positions.
    for (let i = 1; i < counts.length; i += 1) {
        counts[i] += counts[i - 1];
    }

    const result = new Array(data.length);

    /*
     * Reverse traversal is the critical stability rule. For equal keys, the
     * later input occurrence is placed later than the earlier occurrence.
     */
    for (let i = data.length - 1; i >= 0; i -= 1) {
        const value = data[i];
        const offset = value - minimum;

        counts[offset] -= 1;
        result[counts[offset]] = value;
    }

    return result;
}


// ---------------------------------------------------------------------------
// Heap sort
// ---------------------------------------------------------------------------

function heapSort(values) {
    const data = validateIntegerArray(values);

    function siftDown(root, heapSize) {
        while (true) {
            const left = root * 2 + 1;
            const right = left + 1;
            let largest = root;

            if (left < heapSize && data[left] > data[largest]) {
                largest = left;
            }

            if (right < heapSize && data[right] > data[largest]) {
                largest = right;
            }

            if (largest === root) {
                return;
            }

            [data[root], data[largest]] = [data[largest], data[root]];
            root = largest;
        }
    }

    /*
     * Only internal nodes have children, so heap construction begins at the
     * final internal node and works toward the root.
     */
    for (let root = Math.floor(data.length / 2) - 1; root >= 0; root -= 1) {
        siftDown(root, data.length);
    }

    /*
     * The root is always the maximum element. Moving it to the final active
     * position shrinks the heap while preserving the sorted suffix.
     */
    for (let end = data.length - 1; end > 0; end -= 1) {
        [data[0], data[end]] = [data[end], data[0]];
        siftDown(0, end);
    }

    return data;
}


// ---------------------------------------------------------------------------
// Additional comparison algorithm: merge sort
// ---------------------------------------------------------------------------

function mergeSort(values) {
    const data = validateIntegerArray(values);

    if (data.length <= 1) {
        return data;
    }

    const middle = Math.floor(data.length / 2);
    const left = mergeSort(data.slice(0, middle));
    const right = mergeSort(data.slice(middle));

    const result = [];
    let leftIndex = 0;
    let rightIndex = 0;

    /*
     * Choosing the left element when values are equal preserves the relative
     * order of equal records when the same merge pattern is applied to
     * objects with comparable keys.
     */
    while (leftIndex < left.length && rightIndex < right.length) {
        if (left[leftIndex] <= right[rightIndex]) {
            result.push(left[leftIndex]);
            leftIndex += 1;
        } else {
            result.push(right[rightIndex]);
            rightIndex += 1;
        }
    }

    result.push(...left.slice(leftIndex));
    result.push(...right.slice(rightIndex));

    return result;
}


// ---------------------------------------------------------------------------
// Sorting-based problem solving
// ---------------------------------------------------------------------------

function containsDuplicateBySorting(values) {
    const data = validateIntegerArray(values).sort((a, b) => a - b);

    for (let i = 1; i < data.length; i += 1) {
        if (data[i] === data[i - 1]) {
            return true;
        }
    }

    return false;
}

function twoSumSorted(values, target) {
    const data = validateIntegerArray(values).sort((a, b) => a - b);

    if (!Number.isInteger(target)) {
        throw new TypeError('target must be an integer');
    }

    let left = 0;
    let right = data.length - 1;

    while (left < right) {
        const total = data[left] + data[right];

        if (total === target) {
            return {
                left: data[left],
                right: data[right]
            };
        }

        if (total < target) {
            left += 1;
        } else {
            right -= 1;
        }
    }

    return null;
}

function mergeIntervals(intervals) {
    if (!Array.isArray(intervals)) {
        throw new TypeError('intervals must be an array');
    }

    const normalized = intervals.map((interval) => {
        if (!Array.isArray(interval) || interval.length !== 2) {
            throw new TypeError('each interval must contain [start, end]');
        }

        const [start, end] = interval;

        if (!Number.isInteger(start) || !Number.isInteger(end)) {
            throw new TypeError('interval endpoints must be integers');
        }

        if (start > end) {
            throw new RangeError('interval start cannot exceed its end');
        }

        return [start, end];
    });

    normalized.sort((a, b) => a[0] - b[0]);

    if (normalized.length === 0) {
        return [];
    }

    const merged = [normalized[0].slice()];

    for (const [start, end] of normalized.slice(1)) {
        const current = merged[merged.length - 1];

        if (start <= current[1]) {
            current[1] = Math.max(current[1], end);
        } else {
            merged.push([start, end]);
        }
    }

    return merged;
}

function maximumNonOverlappingJobs(jobs) {
    if (!Array.isArray(jobs)) {
        throw new TypeError('jobs must be an array');
    }

    const ordered = jobs.map((job) => ({ ...job })).sort(
        (a, b) => a.finish - b.finish
    );

    const selected = [];
    let currentFinish = null;

    for (const job of ordered) {
        if (
            !Number.isInteger(job.start) ||
            !Number.isInteger(job.finish) ||
            job.start > job.finish
        ) {
            throw new RangeError('invalid job interval');
        }

        if (currentFinish === null || job.start >= currentFinish) {
            selected.push(job);
            currentFinish = job.finish;
        }
    }

    return selected;
}

function kthLargestWithMinHeap(values, k) {
    const data = validateIntegerArray(values);

    if (!Number.isInteger(k) || k < 1 || k > data.length) {
        throw new RangeError('k must identify an element in the array');
    }

    /*
     * JavaScript has no built-in binary heap. A small min-heap implementation
     * demonstrates the data structure used to retain only k candidates.
     */
    const heap = [];

    function push(value) {
        heap.push(value);

        let index = heap.length - 1;

        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);

            if (heap[parent] <= heap[index]) {
                break;
            }

            [heap[parent], heap[index]] = [heap[index], heap[parent]];
            index = parent;
        }
    }

    function replaceRoot(value) {
        heap[0] = value;

        let index = 0;

        while (true) {
            const left = index * 2 + 1;
            const right = left + 1;
            let smallest = index;

            if (left < heap.length && heap[left] < heap[smallest]) {
                smallest = left;
            }

            if (right < heap.length && heap[right] < heap[smallest]) {
                smallest = right;
            }

            if (smallest === index) {
                break;
            }

            [heap[index], heap[smallest]] = [heap[smallest], heap[index]];
            index = smallest;
        }
    }

    for (const value of data) {
        if (heap.length < k) {
            push(value);
        } else if (value > heap[0]) {
            replaceRoot(value);
        }
    }

    return heap[0];
}


// ---------------------------------------------------------------------------
// Stable sorting of records
// ---------------------------------------------------------------------------

function stablePrioritySort(records) {
    if (!Array.isArray(records)) {
        throw new TypeError('records must be an array');
    }

    for (const record of records) {
        if (!Number.isInteger(record.priority)) {
            throw new TypeError('record priority must be an integer');
        }
    }

    /*
     * Array.prototype.sort is stable in modern ECMAScript implementations.
     * Returning 0 for equal priorities therefore preserves their original
     * order instead of introducing an artificial secondary key.
     */
    return [...records].sort(
        (a, b) => a.priority - b.priority
    );
}


// ---------------------------------------------------------------------------
// Event-driven workflow
// ---------------------------------------------------------------------------

class SortingReview {
    constructor() {
        this.listeners = new Map();
    }

    on(eventName, listener) {
        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, []);
        }

        this.listeners.get(eventName).push(listener);
    }

    emit(eventName, payload) {
        const listeners = this.listeners.get(eventName) || [];

        for (const listener of listeners) {
            listener(payload);
        }
    }

    reviewDataset(name, values) {
        const data = validateIntegerArray(values);

        this.emit('started', {
            name,
            size: data.length
        });

        try {
            const counting = countingSort(data);
            const heap = heapSort(data);

            if (
                JSON.stringify(counting) !==
                JSON.stringify(heap)
            ) {
                throw new Error('sorting implementations disagree');
            }

            const result = {
                name,
                size: data.length,
                result: counting
            };

            this.emit('completed', result);
            return result;
        } catch (error) {
            this.emit('failed', {
                name,
                error
            });

            throw error;
        }
    }
}


// ---------------------------------------------------------------------------
// Asynchronous benchmark
// ---------------------------------------------------------------------------

function seededRandom(seed) {
    let state = seed >>> 0;

    return function next() {
        state = (1664525 * state + 1013904223) >>> 0;
        return state / 0x100000000;
    };
}

function generateDataset(size, maximum, seed = 42) {
    if (
        !Number.isInteger(size) ||
        size < 0 ||
        !Number.isInteger(maximum) ||
        maximum < 0
    ) {
        throw new RangeError('invalid dataset parameters');
    }

    const random = seededRandom(seed);
    const result = new Array(size);

    for (let i = 0; i < size; i += 1) {
        result[i] = Math.floor(random() * (maximum + 1));
    }

    return result;
}

async function benchmark(sorters, dataset) {
    /*
     * setImmediate yields to the Node.js event loop between measurements.
     * This is useful when a larger synchronous benchmark would otherwise
     * monopolize the event loop.
     */
    const measurements = {};

    for (const [name, sorter] of Object.entries(sorters)) {
        await new Promise((resolve) => setImmediate(resolve));

        const input = [...dataset];
        const start = process.hrtime.bigint();

        const output = sorter(input);

        const elapsedNanoseconds =
            process.hrtime.bigint() - start;

        if (!isSorted(output)) {
            throw new Error(`${name} failed benchmark validation`);
        }

        measurements[name] =
            Number(elapsedNanoseconds) / 1_000_000;

    }

    return measurements;
}


// ---------------------------------------------------------------------------
// Counting-sort suitability analysis
// ---------------------------------------------------------------------------

function explainCountingSortSuitability(values) {
    const data = validateIntegerArray(values);

    if (data.length === 0) {
        return 'empty input: counting sort has no counting domain to allocate';
    }

    const minimum = Math.min(...data);
    const maximum = Math.max(...data);
    const range = maximum - minimum + 1;

    if (range <= data.length * 10) {
        return (
            `counting sort is well matched: n=${data.length}, k=${range}`
        );
    }

    return (
        `comparison sorting may be preferable: n=${data.length}, k=${range}`
    );
}


// ---------------------------------------------------------------------------
// Demonstrations
// ---------------------------------------------------------------------------

function demonstrateCountingSort() {
    const input = [7, -2, 5, 5, 0, -2, 3, 9, 1];

    console.log('\nCounting sort');
    console.log('input:', input);
    console.log('stable output:', countingSort(input));
    console.log(
        'suitability:',
        explainCountingSortSuitability(input)
    );

    try {
        countingSort([1, 1_000_000_000]);
    } catch (error) {
        console.log('sparse-range protection:', error.message);
    }
}

function demonstrateHeapSort() {
    const input = [19, 3, 14, 7, 2, 18, 11, 5];

    console.log('\nHeap sort');
    console.log('input:', input);
    console.log('output:', heapSort(input));
}

function demonstrateSortingProblems() {
    console.log('\nSorting-based problem solving');

    console.log(
        'duplicate detection:',
        containsDuplicateBySorting([4, 9, 1, 4, 7])
    );

    console.log(
        'two-sum after sorting:',
        twoSumSorted([10, 3, 7, 2, 15], 9)
    );

    console.log(
        'merged intervals:',
        mergeIntervals([
            [1, 5],
            [2, 7],
            [10, 12],
            [11, 15]
        ])
    );

    console.log(
        '2nd largest:',
        kthLargestWithMinHeap([91, 13, 55, 72, 40, 99], 2)
    );

    const jobs = [
        { name: 'API maintenance', start: 1, finish: 3 },
        { name: 'database migration', start: 3, finish: 5 },
        { name: 'security review', start: 0, finish: 2 },
        { name: 'release validation', start: 5, finish: 7 },
        { name: 'performance test', start: 4, finish: 6 }
    ];

    console.log(
        'scheduled jobs:',
        maximumNonOverlappingJobs(jobs).map((job) => job.name)
    );
}

function demonstrateStableRecords() {
    const records = [
        { id: 'R1', priority: 2, message: 'first priority two' },
        { id: 'R2', priority: 1, message: 'first priority one' },
        { id: 'R3', priority: 2, message: 'second priority two' },
        { id: 'R4', priority: 1, message: 'second priority one' },
        { id: 'R5', priority: 2, message: 'third priority two' }
    ];

    console.log('\nStable record sorting');

    const result = stablePrioritySort(records);

    console.log(
        result.map((record) => `${record.priority}:${record.id}`).join(' ')
    );
}

function demonstrateEventDrivenReview() {
    console.log('\nEvent-driven sorting review');

    const review = new SortingReview();

    review.on('started', ({ name, size }) => {
        console.log(`started ${name}, size=${size}`);
    });

    review.on('completed', ({ name, result }) => {
        console.log(`completed ${name}:`, result);
    });

    review.on('failed', ({ name, error }) => {
        console.log(`failed ${name}: ${error.message}`);
    });

    review.reviewDataset('release-metrics', [8, 3, 5, 3, 1, 9, 2]);
}


// ---------------------------------------------------------------------------
// Complexity reference
// ---------------------------------------------------------------------------

function printComplexityTable() {
    console.log('\nFinal comparison');
    console.log(
        'Algorithm          Average Time   Worst Time    Extra Space   Stable'
    );
    console.log(
        'Bubble Sort        O(n²)           O(n²)         O(1)          Yes'
    );
    console.log(
        'Selection Sort     O(n²)           O(n²)         O(1)          Usually No'
    );
    console.log(
        'Insertion Sort     O(n²)           O(n²)         O(1)          Yes'
    );
    console.log(
        'Merge Sort         O(n log n)      O(n log n)    O(n)          Yes'
    );
    console.log(
        'Quick Sort         O(n log n)      O(n²)         Depends       Usually No'
    );
    console.log(
        'Counting Sort      O(n + k)        O(n + k)      O(n + k)      Can be'
    );
    console.log(
        'Heap Sort          O(n log n)      O(n log n)    O(1)          No'
    );
}


// ---------------------------------------------------------------------------
// Assertions
// ---------------------------------------------------------------------------

function runAssertions() {
    const cases = [
        [],
        [1],
        [4, 1, 3, 2],
        [5, 5, 5],
        [-10, 0, 7, -3, 2, -3],
        [100, 1, 50, 1, 100]
    ];

    const sorters = [
        countingSort,
        heapSort,
        mergeSort
    ];

    for (const sorter of sorters) {
        for (const input of cases) {
            const expected = [...input].sort((a, b) => a - b);
            const result = assertSortedAndPreserved(sorter, input);

            if (JSON.stringify(result) !== JSON.stringify(expected)) {
                throw new Error(
                    `${sorter.name} failed deterministic assertion`
                );
            }
        }
    }

    if (!containsDuplicateBySorting([1, 2, 2])) {
        throw new Error('duplicate detection failed');
    }

    if (containsDuplicateBySorting([1, 2, 3])) {
        throw new Error('duplicate detection false positive');
    }

    if (
        JSON.stringify(
            mergeIntervals([[1, 3], [3, 5]])
        ) !== JSON.stringify([[1, 5]])
    ) {
        throw new Error('interval merge failed');
    }

    if (
        kthLargestWithMinHeap([9, 2, 7, 5], 1) !== 9 ||
        kthLargestWithMinHeap([9, 2, 7, 5], 4) !== 2
    ) {
        throw new Error('kth-largest calculation failed');
    }
}


// ---------------------------------------------------------------------------
// Main execution
// ---------------------------------------------------------------------------

async function main() {
    console.log('='.repeat(78));
    console.log('ADVANCED SORTING REVIEW');
    console.log('='.repeat(78));

    runAssertions();

    demonstrateCountingSort();
    demonstrateHeapSort();
    demonstrateSortingProblems();
    demonstrateStableRecords();
    demonstrateEventDrivenReview();

    const dataset = generateDataset(10_000, 10_000, 42);

    console.log('\nAsynchronous benchmark in milliseconds');

    const measurements = await benchmark(
        {
            'Merge Sort': mergeSort,
            'Heap Sort': heapSort,
            'Counting Sort': countingSort
        },
        dataset
    );

    for (const [name, milliseconds] of Object.entries(measurements)) {
        console.log(
            `  ${name.padEnd(16)} ${milliseconds.toFixed(3)} ms`
        );
    }

    printComplexityTable();

    console.log('\nAll JavaScript assertions passed.');
}

main().catch((error) => {
    console.error(`Execution failed: ${error.message}`);
    process.exitCode = 1;
});
