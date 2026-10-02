'use strict';

/*
 * Quick Sort in JavaScript
 *
 * This file uses JavaScript-specific mechanisms to model sorting as an
 * event-driven workflow. It demonstrates:
 * - pivot selection
 * - partition events
 * - recursive partitioning
 * - three-way partitioning for duplicate-heavy data
 * - worst-case behavior
 * - iterative quick sort to avoid deep call stacks
 * - merge sort as a comparison
 * - correctness checks
 * - asynchronous execution for large workloads
 *
 * Run with:
 *   node quick_sort.js
 */

class SortMetrics {
    constructor() {
        this.comparisons = 0;
        this.swaps = 0;
        this.partitionCalls = 0;
        this.recursiveCalls = 0;
        this.maxDepth = 0;
    }

    reset() {
        this.comparisons = 0;
        this.swaps = 0;
        this.partitionCalls = 0;
        this.recursiveCalls = 0;
        this.maxDepth = 0;
    }
}

function assertIntegerArray(values) {
    if (!Array.isArray(values)) {
        throw new TypeError('Input must be an array.');
    }

    for (const value of values) {
        if (!Number.isInteger(value)) {
            throw new TypeError(
                `Quick sort demonstration expects integers; received ${typeof value}.`
            );
        }
    }
}

function isSorted(values) {
    for (let index = 1; index < values.length; index += 1) {
        if (values[index - 1] > values[index]) {
            return false;
        }
    }
    return true;
}

function swap(values, left, right, metrics) {
    if (left === right) {
        return;
    }

    [values[left], values[right]] = [values[right], values[left]];
    metrics.swaps += 1;
}

function createDeterministicRandom(seed = 123456789) {
    /*
     * A tiny deterministic generator makes demonstrations reproducible.
     * It is not a cryptographic random-number generator.
     */
    let state = seed >>> 0;

    return function random() {
        state = (Math.imul(1664525, state) + 1013904223) >>> 0;
        return state / 0x100000000;
    };
}

function choosePivotIndex(values, low, high, strategy, random) {
    switch (strategy) {
        case 'first':
            return low;

        case 'last':
            return high;

        case 'middle':
            return Math.floor((low + high) / 2);

        case 'random':
            return low + Math.floor(random() * (high - low + 1));

        case 'median_of_three': {
            const middle = Math.floor((low + high) / 2);
            const candidates = [
                [values[low], low],
                [values[middle], middle],
                [values[high], high]
            ];

            candidates.sort((a, b) => a[0] - b[0]);
            return candidates[1][1];
        }

        default:
            throw new RangeError(`Unknown pivot strategy: ${strategy}`);
    }
}

function lomutoPartition(values, low, high, metrics) {
    metrics.partitionCalls += 1;

    const pivot = values[high];
    let boundary = low;

    for (let current = low; current < high; current += 1) {
        metrics.comparisons += 1;

        if (values[current] <= pivot) {
            swap(values, boundary, current, metrics);
            boundary += 1;
        }
    }

    swap(values, boundary, high, metrics);
    return boundary;
}

function quickSortRecursive(values, {
    strategy = 'median_of_three',
    metrics = new SortMetrics(),
    random = createDeterministicRandom()
} = {}) {
    assertIntegerArray(values);

    function sortRange(low, high, depth) {
        metrics.recursiveCalls += 1;
        metrics.maxDepth = Math.max(metrics.maxDepth, depth);

        if (low >= high) {
            return;
        }

        /*
         * Moving the chosen pivot to the end allows the Lomuto partition
         * routine to remain independent of the pivot-selection policy.
         */
        const pivotIndex = choosePivotIndex(
            values,
            low,
            high,
            strategy,
            random
        );

        swap(values, pivotIndex, high, metrics);

        const finalPivotIndex = lomutoPartition(
            values,
            low,
            high,
            metrics
        );

        sortRange(low, finalPivotIndex - 1, depth + 1);
        sortRange(finalPivotIndex + 1, high, depth + 1);
    }

    sortRange(0, values.length - 1, 1);
    return metrics;
}

function threeWayPartition(values, low, high, metrics) {
    metrics.partitionCalls += 1;

    const pivot = values[Math.floor((low + high) / 2)];

    let less = low;
    let current = low;
    let greater = high;

    while (current <= greater) {
        metrics.comparisons += 1;

        if (values[current] < pivot) {
            swap(values, less, current, metrics);
            less += 1;
            current += 1;
        } else if (values[current] > pivot) {
            swap(values, current, greater, metrics);
            greater -= 1;
        } else {
            current += 1;
        }
    }

    return [less, greater];
}

function quickSortThreeWay(values, metrics = new SortMetrics()) {
    assertIntegerArray(values);

    function sortRange(low, high, depth) {
        metrics.recursiveCalls += 1;
        metrics.maxDepth = Math.max(metrics.maxDepth, depth);

        if (low >= high) {
            return;
        }

        const [equalStart, equalEnd] = threeWayPartition(
            values,
            low,
            high,
            metrics
        );

        sortRange(low, equalStart - 1, depth + 1);
        sortRange(equalEnd + 1, high, depth + 1);
    }

    sortRange(0, values.length - 1, 1);
    return metrics;
}

function quickSortIterative(values, metrics = new SortMetrics()) {
    /*
     * An explicit stack replaces the JavaScript call stack. This is useful
     * when input characteristics could make recursive quick sort very deep.
     */
    assertIntegerArray(values);

    if (values.length < 2) {
        return metrics;
    }

    const stack = [[0, values.length - 1]];

    while (stack.length > 0) {
        const [low, high] = stack.pop();

        if (low >= high) {
            continue;
        }

        const pivotIndex = Math.floor((low + high) / 2);
        swap(values, pivotIndex, high, metrics);

        const finalPivot = lomutoPartition(
            values,
            low,
            high,
            metrics
        );

        const left = [low, finalPivot - 1];
        const right = [finalPivot + 1, high];

        /*
         * Push the larger partition first. The smaller partition is then
         * processed next, keeping the explicit stack smaller in practice.
         */
        const leftSize = left[1] - left[0] + 1;
        const rightSize = right[1] - right[0] + 1;

        if (leftSize > rightSize) {
            if (left[0] < left[1]) stack.push(left);
            if (right[0] < right[1]) stack.push(right);
        } else {
            if (right[0] < right[1]) stack.push(right);
            if (left[0] < left[1]) stack.push(left);
        }
    }

    return metrics;
}

function merge(values, temporary, left, middle, right, metrics) {
    let leftIndex = left;
    let rightIndex = middle + 1;
    let outputIndex = left;

    while (leftIndex <= middle && rightIndex <= right) {
        metrics.comparisons += 1;

        if (values[leftIndex] <= values[rightIndex]) {
            temporary[outputIndex] = values[leftIndex];
            leftIndex += 1;
        } else {
            temporary[outputIndex] = values[rightIndex];
            rightIndex += 1;
        }

        outputIndex += 1;
    }

    while (leftIndex <= middle) {
        temporary[outputIndex] = values[leftIndex];
        leftIndex += 1;
        outputIndex += 1;
    }

    while (rightIndex <= right) {
        temporary[outputIndex] = values[rightIndex];
        rightIndex += 1;
        outputIndex += 1;
    }

    for (let index = left; index <= right; index += 1) {
        values[index] = temporary[index];
    }
}

function mergeSort(values, metrics = new SortMetrics()) {
    assertIntegerArray(values);

    if (values.length < 2) {
        return metrics;
    }

    const temporary = new Array(values.length);

    function sortRange(left, right, depth) {
        metrics.recursiveCalls += 1;
        metrics.maxDepth = Math.max(metrics.maxDepth, depth);

        if (left >= right) {
            return;
        }

        const middle = Math.floor((left + right) / 2);

        sortRange(left, middle, depth + 1);
        sortRange(middle + 1, right, depth + 1);

        merge(values, temporary, left, middle, right, metrics);
    }

    sortRange(0, values.length - 1, 1);
    return metrics;
}

function printMetrics(label, metrics) {
    console.log(
        `${label.padEnd(22)} ` +
        `comparisons=${String(metrics.comparisons).padStart(6)} ` +
        `swaps=${String(metrics.swaps).padStart(5)} ` +
        `partitions=${String(metrics.partitionCalls).padStart(5)} ` +
        `depth=${String(metrics.maxDepth).padStart(4)}`
    );
}

function demonstratePartition() {
    console.log('\n=== Pivot and Partition ===');

    const values = [29, 10, 14, 37, 13, 8, 42, 18];
    const original = [...values];
    const metrics = new SortMetrics();

    const pivotIndex = lomutoPartition(
        values,
        0,
        values.length - 1,
        metrics
    );

    console.log(`Original: ${JSON.stringify(original)}`);
    console.log(`Pivot: ${original[original.length - 1]}`);
    console.log(`After:  ${JSON.stringify(values)}`);
    console.log(`Pivot final index: ${pivotIndex}`);
    console.log(
        `Left side <= pivot: ${values
            .slice(0, pivotIndex)
            .every(value => value <= values[pivotIndex])}`
    );
    console.log(
        `Right side > pivot: ${values
            .slice(pivotIndex + 1)
            .every(value => value > values[pivotIndex])}`
    );
}

function demonstratePivotStrategies() {
    console.log('\n=== Pivot Strategies ===');

    const input = [41, 8, 29, 17, 63, 4, 52, 31, 22, 70, 11];

    for (const strategy of [
        'first',
        'last',
        'middle',
        'random',
        'median_of_three'
    ]) {
        const values = [...input];
        const metrics = quickSortRecursive(values, {
            strategy,
            random: createDeterministicRandom(123)
        });

        printMetrics(strategy, metrics);
        console.log(`  sorted=${isSorted(values)}`);
    }
}

function demonstrateRecursiveLifecycle() {
    console.log('\n=== Recursive Partitioning ===');

    const values = [34, 7, 23, 32, 5, 62, 19, 44, 12];
    const metrics = quickSortRecursive(values, {
        strategy: 'median_of_three'
    });

    console.log(`Sorted array: ${JSON.stringify(values)}`);
    console.log(`Correct: ${isSorted(values)}`);
    printMetrics('recursive quick sort', metrics);

    console.log(
        'Each partition creates smaller independent ranges. The recursive '
        + 'calls terminate when a range contains zero or one element.'
    );
}

function demonstrateDuplicateOptimization() {
    console.log('\n=== Three-Way Partitioning ===');

    const input = [
        5, 3, 5, 2, 5, 8, 5, 1, 3, 5,
        4, 5, 2, 5, 7, 5, 3, 5, 6, 5
    ];

    const standard = [...input];
    const optimized = [...input];

    const standardMetrics = quickSortRecursive(standard, {
        strategy: 'median_of_three'
    });

    const threeWayMetrics = quickSortThreeWay(optimized);

    console.log(`Input:     ${JSON.stringify(input)}`);
    console.log(`Two-way:   ${JSON.stringify(standard)}`);
    console.log(`Three-way: ${JSON.stringify(optimized)}`);

    printMetrics('two-way partition', standardMetrics);
    printMetrics('three-way partition', threeWayMetrics);
}

function demonstrateWorstCase() {
    console.log('\n=== Worst-Case Behavior ===');

    const size = 200;
    const values = Array.from({ length: size }, (_, index) => index);
    const metrics = quickSortRecursive(values, {
        strategy: 'last'
    });

    const expectedQuadraticPattern = (size * (size - 1)) / 2;

    console.log(`Input: already sorted array of ${size} elements`);
    console.log(`Correct: ${isSorted(values)}`);
    console.log(`Observed comparisons: ${metrics.comparisons}`);
    console.log(
        `n(n-1)/2 comparison pattern: ${expectedQuadraticPattern}`
    );
    console.log(`Maximum recursive depth: ${metrics.maxDepth}`);
    console.log(
        'Choosing the last element on an already sorted array repeatedly '
        + 'creates partitions of sizes n-1 and 0.'
    );
}

function demonstrateIterativeProtection() {
    console.log('\n=== Explicit-Stack Quick Sort ===');

    const size = 2_000;
    const values = Array.from({ length: size }, (_, index) => size - index);
    const metrics = quickSortIterative(values);

    console.log(`Input size: ${size}`);
    console.log(`Sorted: ${isSorted(values)}`);
    printMetrics('iterative quick sort', metrics);
    console.log(
        'The algorithm uses an application-managed stack rather than '
        + 'recursively consuming the JavaScript execution stack.'
    );
}

function generateRandomArray(size, seed = 2026) {
    const random = createDeterministicRandom(seed);
    return Array.from(
        { length: size },
        () => Math.floor(random() * 200001) - 100000
    );
}

function benchmarkAlgorithms() {
    console.log('\n=== Quick Sort vs Merge Sort ===');

    const original = generateRandomArray(4_000);

    const quickValues = [...original];
    const mergeValues = [...original];

    const quickMetrics = new SortMetrics();
    const mergeMetrics = new SortMetrics();

    const quickStart = process.hrtime.bigint();
    quickSortThreeWay(quickValues, quickMetrics);
    const quickEnd = process.hrtime.bigint();

    const mergeStart = process.hrtime.bigint();
    mergeSort(mergeValues, mergeMetrics);
    const mergeEnd = process.hrtime.bigint();

    const quickMilliseconds =
        Number(quickEnd - quickStart) / 1_000_000;

    const mergeMilliseconds =
        Number(mergeEnd - mergeStart) / 1_000_000;

    console.log(`Quick sort correct: ${isSorted(quickValues)}`);
    console.log(`Merge sort correct: ${isSorted(mergeValues)}`);
    console.log(`Quick sort time: ${quickMilliseconds.toFixed(3)} ms`);
    console.log(`Merge sort time: ${mergeMilliseconds.toFixed(3)} ms`);

    printMetrics('quick sort', quickMetrics);
    printMetrics('merge sort', mergeMetrics);

    console.log('\nComplexity:');
    console.log('Quick sort expected: O(n log n)');
    console.log('Quick sort worst case: O(n^2)');
    console.log('Merge sort: O(n log n) in all input-order cases');
    console.log('Quick sort expected auxiliary stack: O(log n)');
    console.log('Merge sort auxiliary storage: O(n)');
}

function demonstrateEdgeCases() {
    console.log('\n=== Edge Cases ===');

    const cases = {
        empty: [],
        singleton: [42],
        sorted: [1, 2, 3, 4, 5],
        reversed: [5, 4, 3, 2, 1],
        equal: [7, 7, 7, 7, 7],
        negative: [-4, 9, -1, 0, -12, 6],
        duplicates: [3, 1, 3, 2, 1, 3, 2]
    };

    for (const [name, input] of Object.entries(cases)) {
        const values = [...input];
        quickSortThreeWay(values);
        console.log(
            `${name.padEnd(10)} ${JSON.stringify(values)} ` +
            `sorted=${isSorted(values)}`
        );
    }

    try {
        quickSortThreeWay([3, '2', 1]);
    } catch (error) {
        console.log(`Validation failure: ${error.message}`);
    }
}

function verifyCorrectness() {
    console.log('\n=== Randomized Correctness Verification ===');

    const random = createDeterministicRandom(777);

    for (let caseNumber = 0; caseNumber < 250; caseNumber += 1) {
        const length = Math.floor(random() * 80);
        const input = Array.from(
            { length },
            () => Math.floor(random() * 41) - 20
        );

        const expected = [...input].sort((a, b) => a - b);

        const algorithms = [
            values => quickSortRecursive(values, {
                strategy: 'median_of_three'
            }),
            values => quickSortThreeWay(values),
            values => quickSortIterative(values),
            values => mergeSort(values)
        ];

        for (const algorithm of algorithms) {
            const actual = [...input];
            algorithm(actual);

            if (JSON.stringify(actual) !== JSON.stringify(expected)) {
                throw new Error(
                    `Correctness failure in case ${caseNumber}: ` +
                    `input=${JSON.stringify(input)} ` +
                    `expected=${JSON.stringify(expected)} ` +
                    `actual=${JSON.stringify(actual)}`
                );
            }
        }
    }

    console.log('250 randomized cases passed for all implementations.');
}

async function asynchronousBenchmark() {
    console.log('\n=== Event-Loop-Friendly Workload ===');

    /*
     * JavaScript runs application code on the event loop. A large synchronous
     * sort can block timers and user interaction in a browser or server.
     * This example yields before starting a deliberately larger operation.
     */
    await new Promise(resolve => setImmediate(resolve));

    const values = generateRandomArray(12_000, 9090);
    const metrics = new SortMetrics();

    const start = process.hrtime.bigint();
    quickSortThreeWay(values, metrics);
    const elapsed = Number(process.hrtime.bigint() - start) / 1_000_000;

    console.log(`Large workload sorted: ${isSorted(values)}`);
    console.log(`Elapsed time: ${elapsed.toFixed(3)} ms`);
    printMetrics('large quick sort', metrics);
}

async function main() {
    console.log('QUICK SORT TECHNICAL DEMONSTRATION');
    console.log('='.repeat(60));

    demonstratePartition();
    demonstratePivotStrategies();
    demonstrateRecursiveLifecycle();
    demonstrateDuplicateOptimization();
    demonstrateWorstCase();
    demonstrateIterativeProtection();
    benchmarkAlgorithms();
    demonstrateEdgeCases();
    verifyCorrectness();
    await asynchronousBenchmark();

    console.log('\nAll demonstrations completed successfully.');
}

main().catch(error => {
    console.error(`Fatal error: ${error.message}`);
    process.exitCode = 1;
});
