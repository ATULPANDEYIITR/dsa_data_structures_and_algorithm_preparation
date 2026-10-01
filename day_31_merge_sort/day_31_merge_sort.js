/*
 * Merge Sort: Divide and Conquer, Splitting, Merging, Recursion, Complexity
 *
 * This Node.js program demonstrates merge sort as an event-driven workflow.
 * The sorting algorithm itself is implemented without Array.prototype.sort().
 *
 * The implementation covers:
 * - Recursive top-down merge sort
 * - Explicit splitting and merging
 * - Stable ordering
 * - Custom key extraction
 * - Event-driven lifecycle reporting
 * - Async processing of independent sort jobs
 * - Bottom-up merge sort
 * - Inversion counting
 * - Validation and failure handling
 * - Complexity measurement
 *
 * Run with:
 *   node merge_sort.js
 */

"use strict";

class MergeSortError extends Error {
    constructor(message) {
        super(message);
        this.name = "MergeSortError";
    }
}

function validateArray(values) {
    if (!Array.isArray(values)) {
        throw new MergeSortError("mergeSort requires an array.");
    }

    for (const value of values) {
        if (typeof value === "number" && !Number.isFinite(value)) {
            throw new MergeSortError(
                "Numeric input cannot contain NaN or infinite values."
            );
        }
    }
}

function mergeRanges(values, buffer, left, middle, right, key, metrics) {
    let leftIndex = left;
    let rightIndex = middle + 1;
    let outputIndex = left;

    while (leftIndex <= middle && rightIndex <= right) {
        metrics.comparisons += 1;

        /*
         * <= is important for stability. If both records have the same key,
         * the left-side record is emitted first.
         */
        if (
            key(values[leftIndex]) <=
            key(values[rightIndex])
        ) {
            buffer[outputIndex] = values[leftIndex];
            leftIndex += 1;
        } else {
            buffer[outputIndex] = values[rightIndex];
            rightIndex += 1;
        }

        outputIndex += 1;
    }

    while (leftIndex <= middle) {
        buffer[outputIndex] = values[leftIndex];
        leftIndex += 1;
        outputIndex += 1;
    }

    while (rightIndex <= right) {
        buffer[outputIndex] = values[rightIndex];
        rightIndex += 1;
        outputIndex += 1;
    }

    for (let index = left; index <= right; index += 1) {
        values[index] = buffer[index];
    }

    metrics.merges += 1;
}

function mergeSort(values, options = {}) {
    validateArray(values);

    const {
        key = (value) => value,
        onSplit = null,
        onMerge = null
    } = options;

    if (typeof key !== "function") {
        throw new MergeSortError("key must be a function.");
    }

    const result = [...values];
    const buffer = new Array(result.length);

    const metrics = {
        comparisons: 0,
        merges: 0,
        splitEvents: 0,
        skippedMerges: 0
    };

    function sortRange(left, right, depth) {
        if (left >= right) {
            return;
        }

        const middle = left + Math.floor((right - left) / 2);

        metrics.splitEvents += 1;

        if (typeof onSplit === "function") {
            onSplit({
                left,
                middle,
                right,
                depth,
                values: result.slice(left, right + 1)
            });
        }

        sortRange(left, middle, depth + 1);
        sortRange(middle + 1, right, depth + 1);

        /*
         * If the final item in the left half is already <= the first item
         * in the right half, the combined range is already sorted.
         */
        metrics.comparisons += 1;

        if (key(result[middle]) <= key(result[middle + 1])) {
            metrics.skippedMerges += 1;
            return;
        }

        mergeRanges(
            result,
            buffer,
            left,
            middle,
            right,
            key,
            metrics
        );

        if (typeof onMerge === "function") {
            onMerge({
                left,
                middle,
                right,
                depth,
                values: result.slice(left, right + 1)
            });
        }
    }

    if (result.length > 1) {
        sortRange(0, result.length - 1, 0);
    }

    return {
        values: result,
        metrics
    };
}

function bottomUpMergeSort(values) {
    validateArray(values);

    const result = [...values];

    if (result.length < 2) {
        return result;
    }

    const buffer = new Array(result.length);

    for (
        let width = 1;
        width < result.length;
        width *= 2
    ) {
        for (
            let left = 0;
            left < result.length;
            left += width * 2
        ) {
            const middle = Math.min(
                left + width - 1,
                result.length - 1
            );

            const right = Math.min(
                left + width * 2 - 1,
                result.length - 1
            );

            if (middle < right) {
                mergeRanges(
                    result,
                    buffer,
                    left,
                    middle,
                    right,
                    (value) => value,
                    {
                        comparisons: 0,
                        merges: 0
                    }
                );
            }
        }
    }

    return result;
}

function countInversions(values) {
    validateArray(values);

    const working = [...values];
    const buffer = new Array(working.length);

    function countRange(left, right) {
        if (left >= right) {
            return 0;
        }

        const middle = left + Math.floor((right - left) / 2);

        let count =
            countRange(left, middle) +
            countRange(middle + 1, right);

        let leftIndex = left;
        let rightIndex = middle + 1;
        let outputIndex = left;

        while (leftIndex <= middle && rightIndex <= right) {
            if (working[leftIndex] <= working[rightIndex]) {
                buffer[outputIndex] = working[leftIndex];
                leftIndex += 1;
            } else {
                buffer[outputIndex] = working[rightIndex];

                /*
                 * Every remaining value in the left half is greater than
                 * this right-half value, so all of them form inversions.
                 */
                count += middle - leftIndex + 1;

                rightIndex += 1;
            }

            outputIndex += 1;
        }

        while (leftIndex <= middle) {
            buffer[outputIndex] = working[leftIndex];
            leftIndex += 1;
            outputIndex += 1;
        }

        while (rightIndex <= right) {
            buffer[outputIndex] = working[rightIndex];
            rightIndex += 1;
            outputIndex += 1;
        }

        for (let index = left; index <= right; index += 1) {
            working[index] = buffer[index];
        }

        return count;
    }

    return working.length === 0
        ? 0
        : countRange(0, working.length - 1);
}

function demonstrateTrace() {
    const input = [38, 27, 43, 3, 9, 82, 10];

    console.log("\nRecursive lifecycle:");

    const result = mergeSort(input, {
        onSplit: ({ values, depth }) => {
            console.log(
                `${"  ".repeat(depth)}split ${JSON.stringify(values)}`
            );
        },
        onMerge: ({ values, depth }) => {
            console.log(
                `${"  ".repeat(depth)}merge ${JSON.stringify(values)}`
            );
        }
    });

    console.log(`sorted = ${JSON.stringify(result.values)}`);
    console.log(`metrics = ${JSON.stringify(result.metrics)}`);
}

function demonstrateStableRecords() {
    const records = [
        { name: "Aarav", score: 82, position: 0 },
        { name: "Meera", score: 95, position: 1 },
        { name: "Kabir", score: 82, position: 2 },
        { name: "Ishita", score: 95, position: 3 },
        { name: "Rohan", score: 70, position: 4 }
    ];

    const result = mergeSort(records, {
        key: (record) => record.score
    });

    console.log("\nStable record ordering:");

    for (const record of result.values) {
        console.log(
            `${record.name.padEnd(8)} score=${record.score} ` +
            `original=${record.position}`
        );
    }

    const score82 = result.values
        .filter((record) => record.score === 82)
        .map((record) => record.name);

    if (JSON.stringify(score82) !== JSON.stringify(["Aarav", "Kabir"])) {
        throw new Error("Stability check failed.");
    }
}

async function processSortJob(job) {
    if (!job || typeof job !== "object") {
        throw new MergeSortError("A sort job must be an object.");
    }

    /*
     * Promise.resolve().then() makes the API asynchronous without pretending
     * that the CPU-bound merge sort itself becomes parallel automatically.
     * JavaScript's event loop still executes the sort synchronously.
     */
    return Promise.resolve().then(() => {
        const result = mergeSort(job.values);
        return {
            id: job.id,
            values: result.values,
            metrics: result.metrics
        };
    });
}

async function demonstrateEventDrivenJobs() {
    const jobs = [
        { id: "orders-by-amount", values: [900, 120, 450, 300, 80] },
        { id: "latencies-ms", values: [82, 14, 39, 7, 125, 21] },
        { id: "inventory-deltas", values: [3, -2, 7, 0, -8, 4] }
    ];

    const results = await Promise.all(
        jobs.map((job) => processSortJob(job))
    );

    console.log("\nEvent-driven sort jobs:");

    for (const result of results) {
        console.log(
            `${result.id}: ${JSON.stringify(result.values)}`
        );
    }
}

function verifyImplementation() {
    const cases = [
        [],
        [1],
        [2, 1],
        [1, 2, 3],
        [5, 5, 5],
        [4, -1, 7, 2, 0, -5],
        Array.from({ length: 100 }, (_, index) => 100 - index)
    ];

    for (const input of cases) {
        const expected = [...input].sort((a, b) => a - b);

        const actual = mergeSort(input).values;
        const iterative = bottomUpMergeSort(input);

        if (
            JSON.stringify(actual) !== JSON.stringify(expected) ||
            JSON.stringify(iterative) !== JSON.stringify(expected)
        ) {
            throw new Error(
                `Verification failed for ${JSON.stringify(input)}`
            );
        }
    }

    const random = [];
    let state = 0x12345678;

    for (let index = 0; index < 200; index += 1) {
        /*
         * A deterministic integer generator avoids external dependencies.
         */
        state = (
            Math.imul(state, 1664525) + 1013904223
        ) >>> 0;

        random.push((state % 2001) - 1000);
    }

    const expected = [...random].sort((a, b) => a - b);
    const actual = mergeSort(random).values;

    if (JSON.stringify(actual) !== JSON.stringify(expected)) {
        throw new Error("Randomized verification failed.");
    }

    console.log("\nVerification: all JavaScript tests passed.");
}

function demonstrateComplexity() {
    console.log("\nComparison measurements:");

    for (const size of [8, 16, 32, 64, 128]) {
        const descending = Array.from(
            { length: size },
            (_, index) => size - index
        );

        const result = mergeSort(descending);

        console.log(
            `n=${String(size).padStart(3)} ` +
            `comparisons=${String(result.metrics.comparisons).padStart(5)} ` +
            `merges=${String(result.metrics.merges).padStart(4)}`
        );
    }

    console.log(
        "\nThe recursion tree has logarithmic depth, while each level " +
        "collectively processes linear data during merging."
    );
}

async function main() {
    console.log("MERGE SORT CASE STUDY");
    console.log("=".repeat(60));

    demonstrateTrace();
    demonstrateStableRecords();

    const iterativeInput = [12, 5, 19, 1, 7, 3, 15];
    console.log("\nBottom-up implementation:");
    console.log(`before = ${JSON.stringify(iterativeInput)}`);
    console.log(
        `after  = ${JSON.stringify(bottomUpMergeSort(iterativeInput))}`
    );

    const inversionInput = [2, 4, 1, 3, 5];
    console.log("\nInversion counting:");
    console.log(
        `${JSON.stringify(inversionInput)} -> ` +
        `${countInversions(inversionInput)} inversions`
    );

    await demonstrateEventDrivenJobs();
    verifyImplementation();
    demonstrateComplexity();

    console.log("\nAlgorithm properties:");
    console.log("Time: O(n log n) in best, average, and worst cases.");
    console.log("Auxiliary storage: O(n) for the merge buffer.");
    console.log("Stable: yes, when equal keys select the left item first.");
    console.log(
        "Recursive implementation: O(log n) recursion depth for balanced splits."
    );
    console.log(
        "Bottom-up implementation: avoids recursive call-stack usage."
    );
}

main().catch((error) => {
    console.error(`Execution failed: ${error.message}`);
    process.exitCode = 1;
});
