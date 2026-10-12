"use strict";

/*
 * Monotonic stacks in JavaScript.
 *
 * Run with: node monotonic-stack.js
 *
 * This implementation emphasizes event-style processing, streaming input,
 * circular-array queries, stable index tracking, and histogram analysis.
 */

function assertNumericArray(values, name = "values") {
  if (!Array.isArray(values)) {
    throw new TypeError(`${name} must be an array`);
  }

  for (const value of values) {
    if (typeof value !== "number" || !Number.isFinite(value)) {
      throw new TypeError(`${name} must contain finite numbers`);
    }
  }
}

function nextGreaterRight(values) {
  assertNumericArray(values);
  const answer = Array(values.length).fill(null);
  const unresolved = [];

  values.forEach((value, index) => {
    // Each popped index receives its first strictly greater value.
    while (
      unresolved.length > 0 &&
      values[unresolved[unresolved.length - 1]] < value
    ) {
      const previousIndex = unresolved.pop();
      answer[previousIndex] = value;
    }

    unresolved.push(index);
  });

  return answer;
}

function nextSmallerRight(values) {
  assertNumericArray(values);
  const answer = Array(values.length).fill(null);
  const unresolved = [];

  for (let index = 0; index < values.length; index += 1) {
    while (
      unresolved.length > 0 &&
      values[unresolved[unresolved.length - 1]] > values[index]
    ) {
      answer[unresolved.pop()] = values[index];
    }
    unresolved.push(index);
  }

  return answer;
}

function nextGreaterLeft(values) {
  assertNumericArray(values);
  const answer = Array(values.length).fill(null);
  const candidates = [];

  for (let index = 0; index < values.length; index += 1) {
    // Equal values cannot answer a strictly-greater query.
    while (
      candidates.length > 0 &&
      values[candidates[candidates.length - 1]] <= values[index]
    ) {
      candidates.pop();
    }

    if (candidates.length > 0) {
      answer[index] = values[candidates[candidates.length - 1]];
    }
    candidates.push(index);
  }

  return answer;
}

function nextSmallerLeft(values) {
  assertNumericArray(values);
  const answer = Array(values.length).fill(null);
  const candidates = [];

  for (let index = 0; index < values.length; index += 1) {
    while (
      candidates.length > 0 &&
      values[candidates[candidates.length - 1]] >= values[index]
    ) {
      candidates.pop();
    }

    if (candidates.length > 0) {
      answer[index] = values[candidates[candidates.length - 1]];
    }
    candidates.push(index);
  }

  return answer;
}

function nextGreaterCircular(values) {
  assertNumericArray(values);
  const answer = Array(values.length).fill(null);
  const stack = [];
  const n = values.length;

  // Iterate twice to let late elements answer queries near the array's end.
  for (let step = 0; step < 2 * n; step += 1) {
    const index = step % n;

    while (
      stack.length > 0 &&
      values[stack[stack.length - 1]] < values[index]
    ) {
      answer[stack.pop()] = values[index];
    }

    if (step < n) {
      stack.push(index);
    }
  }

  return answer;
}

function dailyTemperatures(temperatures) {
  assertNumericArray(temperatures, "temperatures");
  const answer = Array(temperatures.length).fill(0);
  const unresolvedDays = [];

  temperatures.forEach((temperature, day) => {
    while (
      unresolvedDays.length > 0 &&
      temperatures[unresolvedDays[unresolvedDays.length - 1]] < temperature
    ) {
      const previousDay = unresolvedDays.pop();
      answer[previousDay] = day - previousDay;
    }
    unresolvedDays.push(day);
  });

  return answer;
}

function largestHistogramRectangle(heights) {
  assertNumericArray(heights, "heights");

  if (heights.some((height) => height < 0)) {
    throw new RangeError("Histogram heights must be non-negative");
  }

  const stack = [];
  let largestArea = 0;

  // The virtual zero-height bar flushes all remaining positive bars.
  for (let index = 0; index <= heights.length; index += 1) {
    const currentHeight = index === heights.length ? 0 : heights[index];

    while (
      stack.length > 0 &&
      heights[stack[stack.length - 1]] > currentHeight
    ) {
      const height = heights[stack.pop()];
      const previousSmallerIndex =
        stack.length > 0 ? stack[stack.length - 1] : -1;
      const width = index - previousSmallerIndex - 1;
      largestArea = Math.max(largestArea, height * width);
    }

    // The sentinel index is never dereferenced because the loop ends here.
    stack.push(index);
  }

  return largestArea;
}

/*
 * Process an iterable of readings without retaining every input value.
 * Outstanding indices are resolved when a later reading is greater.
 *
 * This generator yields results as soon as the next-greater answer becomes
 * known. Final unresolved readings receive null when the stream ends.
 */
function* streamNextGreater(readings) {
  const pending = [];
  let index = 0;

  for (const value of readings) {
    if (typeof value !== "number" || !Number.isFinite(value)) {
      throw new TypeError("Every streamed reading must be a finite number");
    }

    while (pending.length > 0 && pending[pending.length - 1].value < value) {
      const resolved = pending.pop();
      yield Object.freeze({
        index: resolved.index,
        value: resolved.value,
        nextGreater: value,
      });
    }

    pending.push({ index, value });
    index += 1;
  }

  while (pending.length > 0) {
    const unresolved = pending.pop();
    yield Object.freeze({
      index: unresolved.index,
      value: unresolved.value,
      nextGreater: null,
    });
  }
}

/*
 * An event-driven service for temperature monitoring.
 * The stack stores unresolved measurements, and each new measurement can
 * trigger multiple notification events for previously recorded readings.
 */
class TemperatureMonitor {
  #pending = [];
  #nextId = 0;

  record(celsius) {
    if (typeof celsius !== "number" || !Number.isFinite(celsius)) {
      throw new TypeError("Temperature must be a finite number");
    }

    const events = [];
    const current = Object.freeze({
      id: this.#nextId,
      celsius,
    });

    while (
      this.#pending.length > 0 &&
      this.#pending[this.#pending.length - 1].celsius < celsius
    ) {
      const previous = this.#pending.pop();
      events.push(
        Object.freeze({
          measurementId: previous.id,
          warmerMeasurementId: current.id,
          increase: celsius - previous.celsius,
        }),
      );
    }

    this.#pending.push(current);
    this.#nextId += 1;

    return events;
  }

  pendingMeasurements() {
    return this.#pending.map((entry) => ({ ...entry }));
  }
}

function runTests() {
  const equal = (actual, expected, message) => {
    if (JSON.stringify(actual) !== JSON.stringify(expected)) {
      throw new Error(
        `${message}\nExpected: ${JSON.stringify(expected)}\n` +
          `Actual:   ${JSON.stringify(actual)}`,
      );
    }
  };

  equal(nextGreaterRight([2, 1, 3]), [3, 3, null], "Next greater");
  equal(nextSmallerRight([2, 3, 1]), [1, 1, null], "Next smaller");
  equal(nextGreaterLeft([2, 1, 3]), [null, 2, null], "Greater on left");
  equal(nextSmallerLeft([2, 3, 1]), [null, 2, null], "Smaller on left");
  equal(nextGreaterRight([4, 4, 4]), [null, null, null], "Strict duplicates");
  equal(nextGreaterCircular([1, 2, 1]), [2, null, 2], "Circular query");
  equal(dailyTemperatures([73, 74, 75, 71, 69, 72, 76, 73]),
    [1, 1, 4, 2, 1, 1, 0, 0], "Daily temperatures");
  equal(largestHistogramRectangle([2, 1, 5, 6, 2, 3]),
    10, "Histogram rectangle");
  equal([...streamNextGreater([2, 1, 3])], [
    { index: 1, value: 1, nextGreater: 3 },
    { index: 0, value: 2, nextGreater: 3 },
    { index: 2, value: 3, nextGreater: null },
  ], "Stream results");

  let rejected = false;
  try {
    largestHistogramRectangle([2, -1]);
  } catch (error) {
    rejected = error instanceof RangeError;
  }
  if (!rejected) {
    throw new Error("Negative heights must be rejected");
  }

  console.log("All JavaScript tests passed.");
}

function main() {
  const readings = [4, 2, 2, 7, 3, 6, 1, 8];

  console.log("Input readings:", readings);
  console.log("Next greater to the right:", nextGreaterRight(readings));
  console.log("Next smaller to the right:", nextSmallerRight(readings));
  console.log("Nearest greater on the left:", nextGreaterLeft(readings));
  console.log("Nearest smaller on the left:", nextSmallerLeft(readings));

  console.log(
    "Largest histogram rectangle:",
    largestHistogramRectangle([2, 1, 5, 6, 2, 3]),
  );

  console.log("\nStreaming next-greater events:");
  for (const event of streamNextGreater([20, 17, 21, 15, 25])) {
    console.log(event);
  }

  console.log("\nTemperature monitoring:");
  const monitor = new TemperatureMonitor();
  for (const temperature of [18, 20, 19, 24]) {
    console.log(
      `Recorded ${temperature}°C:`,
      monitor.record(temperature),
    );
  }

  runTests();
}

if (require.main === module) {
  main();
}

module.exports = {
  dailyTemperatures,
  largestHistogramRectangle,
  nextGreaterCircular,
  nextGreaterLeft,
  nextGreaterRight,
  nextSmallerLeft,
  nextSmallerRight,
  streamNextGreater,
  TemperatureMonitor,
};
