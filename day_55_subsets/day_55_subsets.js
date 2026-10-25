"use strict";

/**
 * Subset algorithms with duplicate handling, subset-sum search,
 * constrained enumeration, and event-driven search progress.
 */

const { EventEmitter } = require("node:events");

function validateIntegers(values) {
    if (!Array.isArray(values)) {
        throw new TypeError("Input must be an array.");
    }

    for (const value of values) {
        if (!Number.isSafeInteger(value)) {
            throw new TypeError("Every element must be a safe integer.");
        }
    }

    return [...values];
}

function generateSubsets(values) {
    const items = validateIntegers(values);
    let result = [[]];

    for (const value of items) {
        const additions = result.map((subset) => [...subset, value]);
        result = result.concat(additions);
    }

    return result;
}

function uniqueSubsets(values) {
    const items = validateIntegers(values).sort((a, b) => a - b);
    const result = [];
    const path = [];

    function visit(start) {
        result.push([...path]);

        for (let i = start; i < items.length; i++) {
            if (i > start && items[i] === items[i - 1]) {
                continue;
            }

            path.push(items[i]);
            visit(i + 1);
            path.pop();
        }
    }

    visit(0);
    return result;
}

function subsetSum(values, target) {
    if (!Number.isSafeInteger(target)) {
        throw new TypeError("Target must be a safe integer.");
    }

    const items = validateIntegers(values).sort((a, b) => a - b);
    const result = [];
    const path = [];

    function visit(start, remaining) {
        if (remaining === 0) {
            result.push([...path]);
        }

        for (let i = start; i < items.length; i++) {
            if (i > start && items[i] === items[i - 1]) {
                continue;
            }

            path.push(items[i]);
            visit(i + 1, remaining - items[i]);
            path.pop();
        }
    }

    visit(0, target);
    return result;
}

function constrainedSubsets(values, options = {}) {
    const items = validateIntegers(values);
    const {
        minSize = 0,
        maxSize = items.length,
        minSum = null,
        maxSum = null,
        predicate = () => true
    } = options;

    if (
        !Number.isInteger(minSize) ||
        !Number.isInteger(maxSize) ||
        minSize < 0 ||
        maxSize < minSize ||
        maxSize > items.length
    ) {
        throw new RangeError("Invalid subset-size limits.");
    }

    for (const limit of [minSum, maxSum]) {
        if (limit !== null && !Number.isSafeInteger(limit)) {
            throw new TypeError("Sum limits must be safe integers or null.");
        }
    }

    if (minSum !== null && maxSum !== null && minSum > maxSum) {
        throw new RangeError("minSum cannot exceed maxSum.");
    }

    if (typeof predicate !== "function") {
        throw new TypeError("predicate must be a function.");
    }

    const result = [];
    const path = [];

    function visit(index, total) {
        if (path.length > maxSize) return;

        if (index === items.length) {
            if (path.length < minSize) return;
            if (minSum !== null && total < minSum) return;
            if (maxSum !== null && total > maxSum) return;

            const candidate = [...path];
            if (predicate(candidate, total)) {
                result.push({ values: candidate, total });
            }
            return;
        }

        visit(index + 1, total);

        path.push(items[index]);
        visit(index + 1, total + items[index]);
        path.pop();
    }

    visit(0, 0);
    return result;
}

function subsetSumExists(values, target) {
    if (!Number.isSafeInteger(target)) {
        throw new TypeError("Target must be a safe integer.");
    }

    const items = validateIntegers(values);
    let reachable = new Set([0]);

    for (const value of items) {
        const next = new Set(reachable);

        for (const sum of reachable) {
            const candidate = sum + value;
            if (!Number.isSafeInteger(candidate)) {
                throw new RangeError("A reachable sum exceeds safe integer range.");
            }
            next.add(candidate);
        }

        reachable = next;
    }

    return reachable.has(target);
}

class SubsetSearch extends EventEmitter {
    constructor(values) {
        super();
        this.values = validateIntegers(values);
    }

    async findTarget(target) {
        if (!Number.isSafeInteger(target)) {
            throw new TypeError("Target must be a safe integer.");
        }

        const matches = [];
        const path = [];
        const items = [...this.values].sort((a, b) => a - b);
        let visited = 0;

        const visit = async (start, remaining) => {
            visited++;

            if (remaining === 0) {
                matches.push([...path]);
                this.emit("match", { values: [...path], visited });
            }

            for (let i = start; i < items.length; i++) {
                if (i > start && items[i] === items[i - 1]) continue;

                path.push(items[i]);
                await visit(i + 1, remaining - items[i]);
                path.pop();
            }

            // Yield periodically so a long search does not monopolize the event loop.
            if (visited % 1024 === 0) {
                await new Promise((resolve) => setImmediate(resolve));
                this.emit("progress", { visited });
            }
        };

        await visit(0, target);
        this.emit("complete", { visited, matchCount: matches.length });
        return matches;
    }
}

async function main() {
    const values = [1, 2, 2, 3];

    console.log("All subsets:", generateSubsets(values));
    console.log("Unique subsets:", uniqueSubsets(values));
    console.log("Target 4:", subsetSum(values, 4));

    console.log(
        "Constrained:",
        constrainedSubsets(values, {
            minSize: 2,
            maxSize: 3,
            minSum: 4,
            maxSum: 6
        })
    );

    const search = new SubsetSearch(values);
    search.on("match", ({ values: match }) => {
        console.log("Match event:", match);
    });
    search.on("complete", ({ visited, matchCount }) => {
        console.log(`Search completed: ${visited} states, ${matchCount} matches`);
    });

    await search.findTarget(4);

    console.assert(generateSubsets([]).length === 1);
    console.assert(uniqueSubsets([1, 1]).length === 3);
    console.assert(JSON.stringify(subsetSum([1, 2, 2, 3], 4)) ===
        JSON.stringify([[1, 3], [2, 2]]));
    console.assert(subsetSumExists([-3, 1, 2], 0));
    console.assert(!subsetSumExists([2, 4], 3));

    try {
        generateSubsets([1, NaN]);
    } catch (error) {
        console.log("Validation caught:", error.message);
    }
}

if (require.main === module) {
    main().catch((error) => {
        console.error("Subset processing failed:", error.message);
        process.exitCode = 1;
    });
}

module.exports = {
    generateSubsets,
    uniqueSubsets,
    subsetSum,
    constrainedSubsets,
    subsetSumExists,
    SubsetSearch
};
