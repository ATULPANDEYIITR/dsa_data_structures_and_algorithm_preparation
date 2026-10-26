'use strict';

/*
 * Permutation practice:
 * 1. Basic recursive generation
 * 2. Used-array generation
 * 3. Swap-based generation
 * 4. Duplicate-aware generation
 *
 * The implementation uses generators so callers can consume permutations
 * lazily instead of storing n! results in memory at once.
 */

class PermutationError extends Error {
    constructor(message) {
        super(message);
        this.name = 'PermutationError';
    }
}

function validateInput(items) {
    if (!Array.isArray(items)) {
        throw new PermutationError('Input must be an array.');
    }

    if (items.length > 9) {
        throw new PermutationError(
            'Exhaustive generation is limited to arrays of length 9.'
        );
    }
}

function factorial(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new PermutationError('Factorial requires a non-negative integer.');
    }

    let result = 1;
    for (let i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}

function uniquePermutationCount(items) {
    validateInput(items);

    const counts = new Map();

    for (const value of items) {
        const key = typeof value + ':' + String(value);
        counts.set(key, (counts.get(key) ?? 0) + 1);
    }

    let result = factorial(items.length);

    for (const count of counts.values()) {
        result /= factorial(count);
    }

    return result;
}

function* permutationsUsedArray(items) {
    validateInput(items);

    const values = [...items].sort((a, b) =>
        String(a).localeCompare(String(b))
    );

    const used = new Array(values.length).fill(false);
    const current = [];

    function* backtrack() {
        if (current.length === values.length) {
            yield [...current];
            return;
        }

        const levelValues = new Set();

        for (let i = 0; i < values.length; i++) {
            if (used[i]) {
                continue;
            }

            const valueKey = typeof values[i] + ':' + String(values[i]);

            if (levelValues.has(valueKey)) {
                continue;
            }

            levelValues.add(valueKey);
            used[i] = true;
            current.push(values[i]);

            yield* backtrack();

            current.pop();
            used[i] = false;
        }
    }

    yield* backtrack();
}

function* permutationsSwap(items) {
    validateInput(items);

    const values = [...items].sort((a, b) =>
        String(a).localeCompare(String(b))
    );

    function* backtrack(start) {
        if (start === values.length) {
            yield [...values];
            return;
        }

        const usedAtLevel = new Set();

        for (let i = start; i < values.length; i++) {
            const key = typeof values[i] + ':' + String(values[i]);

            if (usedAtLevel.has(key)) {
                continue;
            }

            usedAtLevel.add(key);

            [values[start], values[i]] = [values[i], values[start]];

            yield* backtrack(start + 1);

            [values[start], values[i]] = [values[i], values[start]];
        }
    }

    yield* backtrack(0);
}

async function* permutationsAsync(items, method = 'used-array') {
    /*
     * Async iteration allows a caller to process a large result stream
     * incrementally and yield control between batches.
     */
    const generator =
        method === 'swap'
            ? permutationsSwap(items)
            : permutationsUsedArray(items);

    let count = 0;

    for (const permutation of generator) {
        yield permutation;
        count++;

        if (count % 1000 === 0) {
            await new Promise(resolve => setImmediate(resolve));
        }
    }
}

function collect(generator) {
    return [...generator];
}

async function main() {
    const examples = [
        ['ABC', ['A', 'B', 'C']],
        ['AAB', ['A', 'A', 'B']],
        ['1234', [1, 2, 3, 4]]
    ];

    for (const [name, input] of examples) {
        console.log(`\n${name}`);
        console.log(
            `Expected unique permutations: ${uniquePermutationCount(input)}`
        );

        const used = collect(permutationsUsedArray(input));
        const swapped = collect(permutationsSwap(input));

        console.log('Used-array:', used);
        console.log('Swap-based:', swapped);

        if (used.length !== uniquePermutationCount(input)) {
            throw new Error('Used-array count validation failed.');
        }

        if (swapped.length !== uniquePermutationCount(input)) {
            throw new Error('Swap-based count validation failed.');
        }
    }

    console.log('\nAsync processing:');

    let asyncCount = 0;
    for await (const permutation of permutationsAsync(['A', 'B', 'C'])) {
        console.log(permutation);
        asyncCount++;
    }

    console.log(`Async permutations generated: ${asyncCount}`);

    console.log('\nEmpty input:');
    console.log(collect(permutationsUsedArray([])));

    console.log('\nValidation:');

    try {
        uniquePermutationCount(null);
    } catch (error) {
        console.log(`Rejected correctly: ${error.message}`);
    }

    console.log('\nPerformance characteristics:');
    console.log('Output size for n distinct values is n!.');
    console.log('Generation work is O(n × n!).');
    console.log('Recursive auxiliary state is O(n).');
}

main().catch(error => {
    console.error(`Fatal error: ${error.message}`);
    process.exitCode = 1;
});
