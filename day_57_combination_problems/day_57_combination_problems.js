"use strict";

/*
 * Combination problems implemented as a small event-driven search engine.
 * The implementation uses JavaScript-specific Maps, Sets, generators,
 * Promises, and EventEmitter rather than translating the Python design.
 */

const { EventEmitter } = require("node:events");
const crypto = require("node:crypto");

class CombinationError extends Error {
  constructor(message) {
    super(message);
    this.name = "CombinationError";
  }
}

function validatePositiveIntegers(values) {
  if (!Array.isArray(values)) {
    throw new CombinationError("values must be an array");
  }

  if (!values.every(Number.isInteger)) {
    throw new CombinationError("values must contain integers");
  }

  if (values.some((value) => value <= 0)) {
    throw new CombinationError("values must contain positive integers");
  }
}

function* chooseOrSkip(items) {
  if (!Array.isArray(items)) {
    throw new CombinationError("items must be an array");
  }

  const path = [];

  function* search(index) {
    if (index === items.length) {
      yield [...path];
      return;
    }

    path.push(items[index]);
    yield* search(index + 1);
    path.pop();

    yield* search(index + 1);
  }

  yield* search(0);
}

function* combinations(values, size) {
  validatePositiveIntegers(values);

  if (!Number.isInteger(size) || size < 0) {
    throw new CombinationError("size must be a non-negative integer");
  }

  const sorted = [...new Set(values)].sort((a, b) => a - b);
  const path = [];

  function* search(start) {
    if (path.length === size) {
      yield [...path];
      return;
    }

    const required = size - path.length;
    if (sorted.length - start < required) {
      return;
    }

    for (let index = start; index < sorted.length; index += 1) {
      path.push(sorted[index]);
      yield* search(index + 1);
      path.pop();
    }
  }

  if (size === 0) {
    yield [];
    return;
  }

  yield* search(0);
}

function combinationSum(values, target, { reuse = false } = {}) {
  validatePositiveIntegers(values);

  if (!Number.isInteger(target) || target < 0) {
    throw new CombinationError("target must be a non-negative integer");
  }

  const sorted = [...new Set(values)].sort((a, b) => a - b);
  const output = [];
  const path = [];

  function search(start, remaining) {
    if (remaining === 0) {
      output.push([...path]);
      return;
    }

    for (let index = start; index < sorted.length; index += 1) {
      const value = sorted[index];

      if (value > remaining) {
        break;
      }

      path.push(value);
      search(reuse ? index : index + 1, remaining - value);
      path.pop();
    }
  }

  search(0, target);
  return output;
}

function constrainedCombinationSum(
  values,
  {
    size,
    minimumSum = null,
    maximumSum = null,
  },
) {
  validatePositiveIntegers(values);

  if (!Number.isInteger(size) || size < 0) {
    throw new CombinationError("size must be a non-negative integer");
  }

  if (
    minimumSum !== null &&
    maximumSum !== null &&
    minimumSum > maximumSum
  ) {
    throw new CombinationError("minimumSum cannot exceed maximumSum");
  }

  const sorted = [...new Set(values)].sort((a, b) => a - b);
  const output = [];
  const path = [];

  function smallestPossible(start, count) {
    if (sorted.length - start < count) {
      return null;
    }

    let total = 0;
    for (let index = start; index < start + count; index += 1) {
      total += sorted[index];
    }
    return total;
  }

  function search(start, sum) {
    const remainingSlots = size - path.length;

    if (remainingSlots === 0) {
      if (
        (minimumSum === null || sum >= minimumSum) &&
        (maximumSum === null || sum <= maximumSum)
      ) {
        output.push([...path]);
      }
      return;
    }

    const lowerBound = smallestPossible(start, remainingSlots);
    if (lowerBound === null) {
      return;
    }

    if (
      maximumSum !== null &&
      sum + lowerBound > maximumSum
    ) {
      return;
    }

    for (let index = start; index < sorted.length; index += 1) {
      const value = sorted[index];
      const nextSum = sum + value;

      if (maximumSum !== null && nextSum > maximumSum) {
        break;
      }

      path.push(value);
      search(index + 1, nextSum);
      path.pop();
    }
  }

  search(0, 0);
  return output;
}

class SearchSession extends EventEmitter {
  constructor(values) {
    super();
    validatePositiveIntegers(values);

    this.values = [...new Set(values)].sort((a, b) => a - b);
    this.sessionId = crypto.randomUUID();
    this.cache = new Map();
  }

  async find(target, reuse = false) {
    const key = `${target}:${reuse}`;

    if (this.cache.has(key)) {
      this.emit("cacheHit", { sessionId: this.sessionId, key });
      return this.cache.get(key);
    }

    this.emit("started", {
      sessionId: this.sessionId,
      target,
      reuse,
    });

    // Yield to the event loop so a larger search does not monopolize
    // synchronous application work.
    await new Promise((resolve) => setImmediate(resolve));

    const result = combinationSum(this.values, target, { reuse });
    this.cache.set(key, result);

    this.emit("completed", {
      sessionId: this.sessionId,
      target,
      count: result.length,
    });

    return result;
  }
}

async function main() {
  console.log("Choose/not choose:");
  for (const subset of chooseOrSkip(["repository", "review", "merge"])) {
    console.log(subset);
  }

  console.log("\nFixed-size combinations:");
  for (const combination of combinations([1, 2, 3, 4], 2)) {
    console.log(combination);
  }

  console.log("\nCombination sum without reuse:");
  console.log(combinationSum([2, 3, 5, 7], 10));

  console.log("\nCombination sum with reuse:");
  console.log(combinationSum([2, 3, 5], 8, { reuse: true }));

  console.log("\nConstraint-based recursion:");
  console.log(
    constrainedCombinationSum([2, 3, 5, 7, 11], {
      size: 3,
      minimumSum: 12,
      maximumSum: 18,
    }),
  );

  const session = new SearchSession([2, 3, 5, 7]);

  session.on("started", (event) => {
    console.log(`Search started: ${event.sessionId}`);
  });

  session.on("completed", (event) => {
    console.log(
      `Search completed: ${event.count} combinations found`,
    );
  });

  session.on("cacheHit", (event) => {
    console.log(`Cache hit: ${event.key}`);
  });

  const first = await session.find(10);
  const second = await session.find(10);

  console.log("\nEvent-driven result:");
  console.log(first);
  console.log(`Cached result equal: ${JSON.stringify(first) === JSON.stringify(second)}`);

  // Security and reliability checks.
  try {
    combinationSum([1, 2], -1);
  } catch (error) {
    console.log(`Validation rejected invalid target: ${error.message}`);
  }

  try {
    combinations([1, 2, 3], -2);
  } catch (error) {
    console.log(`Validation rejected invalid size: ${error.message}`);
  }

  // Large unconstrained search spaces can grow exponentially.
  // Production callers should impose input-size and target limits.
  console.log("\nCombination processing completed.");
}

main().catch((error) => {
  console.error("Fatal error:", error.message);
  process.exitCode = 1;
});
