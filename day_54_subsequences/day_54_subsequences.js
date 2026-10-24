"use strict";

/*
 * Event-driven subsequence practice engine.
 * Run with Node.js 18 or later.
 */

const { EventEmitter } = require("node:events");

class SubsequenceError extends Error {}

function validateSequence(values) {
  if (!Array.isArray(values) ||
      values.some(value => !Number.isSafeInteger(value))) {
    throw new SubsequenceError(
      "Expected an array of safe integers."
    );
  }
}

function* subsequences(values) {
  validateSequence(values);
  const current = [];

  function* visit(index) {
    if (index === values.length) {
      yield current.slice();
      return;
    }

    // Exclude first, then include the current element.
    yield* visit(index + 1);
    current.push(values[index]);
    yield* visit(index + 1);
    current.pop();
  }

  yield* visit(0);
}

function countBySum(values, target) {
  validateSequence(values);
  if (!Number.isSafeInteger(target)) {
    throw new SubsequenceError("Target must be a safe integer.");
  }

  const counts = new Map([[0, 1n]]);

  for (const value of values) {
    const updated = new Map(counts);
    for (const [sum, count] of counts) {
      const nextSum = sum + value;
      if (!Number.isSafeInteger(nextSum)) {
        throw new SubsequenceError("A calculated sum exceeds safe integer range.");
      }
      updated.set(nextSum, (updated.get(nextSum) || 0n) + count);
    }
    counts.clear();
    for (const [sum, count] of updated) counts.set(sum, count);
  }

  return counts.get(target) || 0n;
}

function hasSubsequenceSum(values, target) {
  validateSequence(values);
  let reachable = new Set([0]);

  for (const value of values) {
    const next = new Set(reachable);
    for (const sum of reachable) {
      const nextSum = sum + value;
      if (!Number.isSafeInteger(nextSum)) {
        throw new SubsequenceError("A calculated sum exceeds safe integer range.");
      }
      next.add(nextSum);
    }
    reachable = next;
  }

  return reachable.has(target);
}

function countAtMost(values, limit) {
  validateSequence(values);
  if (!Number.isSafeInteger(limit)) {
    throw new SubsequenceError("Limit must be a safe integer.");
  }

  const sorted = [...values].sort((a, b) => a - b);
  const powers = [1n];
  for (let i = 1; i <= sorted.length; i++) {
    powers.push(powers[i - 1] * 2n);
  }

  let left = 0;
  let right = sorted.length - 1;
  let answer = 0n;

  while (left <= right) {
    if (sorted[left] + sorted[right] <= limit) {
      answer += powers[right - left];
      left++;
    } else {
      right--;
    }
  }

  return answer;
}

class PracticeSession extends EventEmitter {
  #values;
  #closed = false;

  constructor(values) {
    super();
    validateSequence(values);
    this.#values = Object.freeze([...values]);
  }

  get values() {
    return [...this.#values];
  }

  run(target) {
    if (this.#closed) {
      throw new SubsequenceError("The practice session is closed.");
    }

    const result = Object.freeze({
      target,
      exists: hasSubsequenceSum(this.#values, target),
      count: countBySum(this.#values, target),
      total: 1n << BigInt(this.#values.length)
    });

    this.emit("analysis", result);
    return result;
  }

  close() {
    this.#closed = true;
    this.emit("closed");
  }
}

function main() {
  const session = new PracticeSession([1, 2, 3]);

  session.on("analysis", result => {
    console.log("Analysis event:", {
      target: result.target,
      exists: result.exists,
      count: result.count.toString(),
      total: result.total.toString()
    });
  });

  console.log("Generated subsequences:");
  for (const item of subsequences(session.values)) {
    console.log(item);
  }

  session.run(3);
  console.log("Nonempty subsequences with min + max <= 4:",
    countAtMost([1, 2, 3], 4).toString());

  if (countBySum([0, 0], 0) !== 4n) {
    throw new Error("Duplicate-index counting test failed.");
  }
  if (countBySum([], 0) !== 1n) {
    throw new Error("Empty-subsequence test failed.");
  }
  if (!hasSubsequenceSum([-2, 5], 3)) {
    throw new Error("Negative-number test failed.");
  }

  session.close();
}

if (require.main === module) {
  try {
    main();
  } catch (error) {
    console.error(`${error.name}: ${error.message}`);
    process.exitCode = 1;
  }
}

module.exports = {
  subsequences,
  countBySum,
  hasSubsequenceSum,
  countAtMost,
  PracticeSession
};
