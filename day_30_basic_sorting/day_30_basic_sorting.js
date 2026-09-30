"use strict";

/*
 * Basic Sorting in JavaScript
 *
 * Practical implementations of:
 *   - Bubble sort
 *   - Selection sort
 *   - Insertion sort
 *
 * The program focuses on the mechanics of comparisons, swaps, stability,
 * in-place mutation, adaptive behavior, and complexity.
 *
 * No Array.prototype.sort() call is used by the sorting implementations.
 */

/* -------------------------------------------------------------------------
 * Instrumentation
 * ------------------------------------------------------------------------- */

function createStats() {
    return {
        comparisons: 0,
        swaps: 0,
        writes: 0
    };
}

function swapInPlace(values, left, right, stats) {
    if (left === right) {
        return;
    }

    const temporary = values[left];
    values[left] = values[right];
    values[right] = temporary;

    stats.swaps += 1;
    stats.writes += 2;
}

function isSorted(values, before = (a, b) => a < b) {
    for (let index = 0; index < values.length - 1; index += 1) {
        if (before(values[index + 1], values[index])) {
            return false;
        }
    }

    return true;
}

/* -------------------------------------------------------------------------
 * Bubble sort
 * ------------------------------------------------------------------------- */

/*
 * Bubble sort compares adjacent elements.
 *
 * The largest element that still belongs in the unsorted region moves
 * toward the right edge during each pass. The "swapped" flag is important:
 * without it, even an already sorted array would require every possible
 * pass and bubble sort would lose its O(n) best case.
 */
function bubbleSort(values, before = (a, b) => a < b) {
    const stats = createStats();

    for (let end = values.length - 1; end > 0; end -= 1) {
        let swapped = false;

        for (let index = 0; index < end; index += 1) {
            stats.comparisons += 1;

            if (before(values[index + 1], values[index])) {
                swapInPlace(values, index, index + 1, stats);
                swapped = true;
            }
        }

        if (!swapped) {
            break;
        }
    }

    return stats;
}

/* -------------------------------------------------------------------------
 * Selection sort
 * ------------------------------------------------------------------------- */

/*
 * Selection sort identifies the smallest remaining value first and then
 * moves it into the next output position.
 *
 * Its comparison count does not depend on whether the input is already
 * sorted because every remaining region must still be searched.
 */
function selectionSort(values, before = (a, b) => a < b) {
    const stats = createStats();

    for (let position = 0; position < values.length - 1; position += 1) {
        let selected = position;

        for (
            let index = position + 1;
            index < values.length;
            index += 1
        ) {
            stats.comparisons += 1;

            if (before(values[index], values[selected])) {
                selected = index;
            }
        }

        if (selected !== position) {
            swapInPlace(values, position, selected, stats);
        }
    }

    return stats;
}

/* -------------------------------------------------------------------------
 * Insertion sort
 * ------------------------------------------------------------------------- */

/*
 * Insertion sort maintains a sorted prefix.
 *
 * JavaScript's assignment operations are used to shift larger elements.
 * Equal elements are not shifted because the comparison is strict. That
 * detail is what preserves the relative ordering of equal-key records.
 */
function insertionSort(values, before = (a, b) => a < b) {
    const stats = createStats();

    for (let position = 1; position < values.length; position += 1) {
        const current = values[position];
        stats.writes += 1;

        let index = position - 1;

        while (index >= 0) {
            stats.comparisons += 1;

            if (!before(current, values[index])) {
                break;
            }

            values[index + 1] = values[index];
            stats.writes += 1;
            index -= 1;
        }

        values[index + 1] = current;
        stats.writes += 1;
    }

    return stats;
}

/* -------------------------------------------------------------------------
 * Event-driven pull-free sorting pipeline
 *
 * The event model is useful when a sorting operation is one stage of a
 * larger data-processing application. JavaScript promises let the pipeline
 * remain asynchronous without making the algorithms themselves dependent
 * on asynchronous execution.
 * ------------------------------------------------------------------------- */

class SortJob {
    constructor(name, algorithm, input) {
        this.name = name;
        this.algorithm = algorithm;
        this.input = [...input];
        this.status = "created";
        this.stats = null;
        this.output = null;
    }

    async execute() {
        if (this.status !== "created") {
            throw new Error(`Sort job "${this.name}" cannot be executed twice.`);
        }

        this.status = "running";

        /*
         * Queueing the actual sort through a resolved Promise demonstrates
         * the event-loop boundary without pretending that the CPU-bound
         * sorting algorithm itself has become parallel.
         */
        await Promise.resolve();

        try {
            this.stats = this.algorithm(this.input);
            this.output = this.input;
            this.status = "completed";
            return this;
        } catch (error) {
            this.status = "failed";
            throw error;
        }
    }
}

async function runSortJobs() {
    const source = [12, 4, 9, 1, 7, 3, 10, 2];

    const jobs = [
        new SortJob("bubble", bubbleSort, source),
        new SortJob("selection", selectionSort, source),
        new SortJob("insertion", insertionSort, source)
    ];

    /*
     * Promise.all is safe here because each job owns a copy of the source
     * array. If the same mutable array were shared, in-place algorithms
     * could interfere with one another.
     */
    const completed = await Promise.all(
        jobs.map((job) => job.execute())
    );

    console.log("\nASYNCHRONOUS SORT JOB PIPELINE");
    console.log("-".repeat(72));

    for (const job of completed) {
        console.log({
            algorithm: job.name,
            status: job.status,
            output: job.output,
            comparisons: job.stats.comparisons,
            swaps: job.stats.swaps,
            writes: job.stats.writes
        });
    }
}

/* -------------------------------------------------------------------------
 * Stability demonstration
 * ------------------------------------------------------------------------- */

class Record {
    constructor(name, score, originalPosition) {
        this.name = name;
        this.score = score;
        this.originalPosition = originalPosition;
    }
}

function recordBefore(left, right) {
    return left.score < right.score;
}

function equalKeyOrder(records) {
    const groups = new Map();

    for (const record of records) {
        if (!groups.has(record.score)) {
            groups.set(record.score, []);
        }

        groups.get(record.score).push(record.name);
    }

    return Object.fromEntries(groups);
}

function demonstrateStability() {
    const original = [
        new Record("Asha", 80, 0),
        new Record("Bharat", 70, 1),
        new Record("Chen", 80, 2),
        new Record("Divya", 60, 3),
        new Record("Esha", 80, 4)
    ];

    console.log("\nSTABILITY");
    console.log("-".repeat(72));
    console.log("Original:", equalKeyOrder(original));

    const algorithms = [
        ["Bubble sort", bubbleSort],
        ["Selection sort", selectionSort],
        ["Insertion sort", insertionSort]
    ];

    for (const [name, algorithm] of algorithms) {
        const records = original.map(
            (record) =>
                new Record(
                    record.name,
                    record.score,
                    record.originalPosition
                )
        );

        const stats = algorithm(records, recordBefore);

        console.log(`\n${name}`);
        console.log(
            "Sorted:",
            records.map((record) => `${record.name}:${record.score}`)
        );
        console.log("Equal-key order:", equalKeyOrder(records));
        console.log("Swaps:", stats.swaps);
    }
}

/* -------------------------------------------------------------------------
 * Basic demonstrations
 * ------------------------------------------------------------------------- */

function demonstrateBasics() {
    const cases = {
        empty: [],
        single: [42],
        duplicates: [5, 2, 5, 1, 2, 5, 3],
        sorted: [1, 2, 3, 4, 5, 6],
        reverse: [6, 5, 4, 3, 2, 1],
        mixed: [9, 1, 7, 3, 2, 8, 4, 6, 5]
    };

    const algorithms = [
        ["Bubble sort", bubbleSort],
        ["Selection sort", selectionSort],
        ["Insertion sort", insertionSort]
    ];

    console.log("BASIC SORTING");
    console.log("=".repeat(72));

    for (const [caseName, original] of Object.entries(cases)) {
        console.log(`\n${caseName}:`, original);

        for (const [name, algorithm] of algorithms) {
            const data = [...original];
            const stats = algorithm(data);

            if (!isSorted(data)) {
                throw new Error(`${name} failed for ${caseName}`);
            }

            console.log(
                `${name.padEnd(16)} -> ${JSON.stringify(data).padEnd(35)} ` +
                `comparisons=${String(stats.comparisons).padStart(3)} ` +
                `swaps=${String(stats.swaps).padStart(2)} ` +
                `writes=${String(stats.writes).padStart(3)}`
            );
        }
    }
}

/* -------------------------------------------------------------------------
 * Descending-order comparison
 * ------------------------------------------------------------------------- */

function demonstrateDescendingOrder() {
    const original = [8, 3, 7, 4, 9, 2, 6, 1, 5];
    const descending = (a, b) => a > b;

    console.log("\nDESCENDING ORDER");
    console.log("-".repeat(72));

    for (const [name, algorithm] of [
        ["Bubble sort", bubbleSort],
        ["Selection sort", selectionSort],
        ["Insertion sort", insertionSort]
    ]) {
        const data = [...original];
        algorithm(data, descending);

        if (!isSorted(data, descending)) {
            throw new Error(`${name} failed descending-order validation.`);
        }

        console.log(`${name.padEnd(16)} -> ${data.join(", ")}`);
    }
}

/* -------------------------------------------------------------------------
 * Randomized correctness testing
 * ------------------------------------------------------------------------- */

/*
 * The reference implementation below is deliberately used only for testing.
 * The three educational algorithms never call Array.prototype.sort().
 *
 * JavaScript's built-in sort is useful here because a correctness test should
 * compare the result of an independently implemented algorithm with a known
 * reference operation.
 */
function referenceNumericSort(values) {
    return [...values].sort((a, b) => a - b);
}

function arraysEqual(left, right) {
    if (left.length !== right.length) {
        return false;
    }

    return left.every((value, index) => value === right[index]);
}

function randomizedCorrectnessTest() {
    let tests = 0;

    for (let run = 0; run < 100; run += 1) {
        const size = Math.floor(Math.random() * 31);
        const original = Array.from(
            { length: size },
            () => Math.floor(Math.random() * 41) - 20
        );

        const expected = referenceNumericSort(original);

        for (const [name, algorithm] of [
            ["Bubble sort", bubbleSort],
            ["Selection sort", selectionSort],
            ["Insertion sort", insertionSort]
        ]) {
            const candidate = [...original];
            algorithm(candidate);

            if (!arraysEqual(candidate, expected)) {
                throw new Error(
                    `${name} failed.\n` +
                    `Input: ${JSON.stringify(original)}\n` +
                    `Expected: ${JSON.stringify(expected)}\n` +
                    `Actual: ${JSON.stringify(candidate)}`
                );
            }

            tests += 1;
        }
    }

    console.log("\nRANDOMIZED CORRECTNESS");
    console.log("-".repeat(72));
    console.log(`Passed ${tests} algorithm/input combinations.`);
}

/* -------------------------------------------------------------------------
 * Operation-pattern analysis
 * ------------------------------------------------------------------------- */

function analyzeOperationPatterns() {
    const sizes = [5, 10, 20, 40];
    const algorithms = [
        ["Bubble sort", bubbleSort],
        ["Selection sort", selectionSort],
        ["Insertion sort", insertionSort]
    ];

    console.log("\nOPERATION PATTERNS");
    console.log("-".repeat(96));
    console.log(
        "Algorithm".padEnd(18) +
        "N".padStart(5) +
        "Best comparisons".padStart(20) +
        "Best swaps".padStart(15) +
        "Reverse comparisons".padStart(22) +
        "Reverse swaps".padStart(17)
    );

    for (const size of sizes) {
        const sorted = Array.from({ length: size }, (_, index) => index);
        const reverse = [...sorted].reverse();

        for (const [name, algorithm] of algorithms) {
            const bestData = [...sorted];
            const best = algorithm(bestData);

            const worstData = [...reverse];
            const worst = algorithm(worstData);

            console.log(
                name.padEnd(18) +
                String(size).padStart(5) +
                String(best.comparisons).padStart(20) +
                String(best.swaps).padStart(15) +
                String(worst.comparisons).padStart(22) +
                String(worst.swaps).padStart(17)
            );
        }
    }
}

/* -------------------------------------------------------------------------
 * Main
 * ------------------------------------------------------------------------- */

async function main() {
    demonstrateBasics();
    demonstrateDescendingOrder();
    demonstrateStability();
    analyzeOperationPatterns();
    randomizedCorrectnessTest();
    await runSortJobs();

    console.log("\nCOMPLEXITY REFERENCE");
    console.log("-".repeat(72));
    console.log(
        "Bubble sort:    best O(n), average O(n²), worst O(n²), stable, in-place."
    );
    console.log(
        "Selection sort: best O(n²), average O(n²), worst O(n²), unstable, in-place."
    );
    console.log(
        "Insertion sort: best O(n), average O(n²), worst O(n²), stable, in-place."
    );
}

main().catch((error) => {
    /*
     * A top-level catch prevents an asynchronous failure from becoming an
     * unhandled rejection and provides a deterministic process failure code
     * for command-line execution.
     */
    console.error("Sorting demonstration failed:", error.message);
    process.exitCode = 1;
});
