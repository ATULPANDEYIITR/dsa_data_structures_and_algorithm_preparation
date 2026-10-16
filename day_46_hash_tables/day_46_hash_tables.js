"use strict";

/*
 * Hash tables in JavaScript:
 * object-property semantics, Map, collision simulation, deletion,
 * frequency aggregation, and asynchronous request deduplication.
 */

const assert = require("node:assert/strict");
const { performance } = require("node:perf_hooks");

function demonstrateMapBasics() {
  console.log("\n=== Map key/value storage ===");

  const inventory = new Map([
    ["SSD-1TB", 24],
    ["RAM-16GB", 48],
    ["GPU-MID", 12],
  ]);

  inventory.set("SSD-1TB", 26);
  inventory.set("CPU-8C", 15);

  console.log("Inventory:", [...inventory.entries()]);
  console.log("GPU quantity:", inventory.get("GPU-MID"));
  console.log("Missing key:", inventory.get("UNKNOWN"));
  console.log("Missing key exists:", inventory.has("UNKNOWN"));

  inventory.delete("RAM-16GB");
  console.log("After deletion:", [...inventory.keys()]);

  // Map distinguishes a missing key from a key whose value is undefined.
  inventory.set("undefined-value", undefined);
  assert.equal(inventory.has("undefined-value"), true);
  assert.equal(inventory.get("undefined-value"), undefined);
}

function demonstrateObjectKeySemantics() {
  console.log("\n=== Object versus Map ===");

  const objectStore = {};
  const mapStore = new Map();

  const firstObjectKey = { warehouse: "north" };
  const secondObjectKey = { warehouse: "north" };

  // Plain object keys are property names, so object keys are converted
  // to strings. These two distinct objects collide as property names.
  objectStore[firstObjectKey] = "first";
  objectStore[secondObjectKey] = "second";

  // Map compares object keys by identity and keeps the entries separate.
  mapStore.set(firstObjectKey, "first");
  mapStore.set(secondObjectKey, "second");

  console.log("Object properties:", objectStore);
  console.log("Map size:", mapStore.size);

  assert.equal(Object.keys(objectStore).length, 1);
  assert.equal(mapStore.size, 2);

  const dictionary = Object.create(null);
  dictionary["__proto__"] = "ordinary data";
  console.log("Null-prototype dictionary:", dictionary["__proto__"]);
}

function demonstrateCollisionChains() {
  console.log("\n=== Conceptual hash buckets ===");

  class ChainedHashTable {
    constructor(capacity = 8) {
      if (!Number.isInteger(capacity) || capacity < 1) {
        throw new RangeError("Capacity must be a positive integer");
      }

      this.buckets = Array.from({ length: capacity }, () => []);
      this.size = 0;
    }

    // A deterministic educational hash, not a secure production hash.
    hashKey(key) {
      const text = String(key);
      let hash = 0;

      for (let index = 0; index < text.length; index += 1) {
        hash = (hash * 31 + text.charCodeAt(index)) >>> 0;
      }

      return hash;
    }

    bucketIndex(key) {
      return this.hashKey(key) % this.buckets.length;
    }

    get(key) {
      const bucket = this.buckets[this.bucketIndex(key)];
      const entry = bucket.find((candidate) => candidate.key === key);
      return entry ? entry.value : undefined;
    }

    has(key) {
      return this.buckets[this.bucketIndex(key)]
        .some((entry) => entry.key === key);
    }

    set(key, value) {
      const bucket = this.buckets[this.bucketIndex(key)];
      const existing = bucket.find((entry) => entry.key === key);

      if (existing) {
        existing.value = value;
        return;
      }

      bucket.push({ key, value });
      this.size += 1;
    }

    delete(key) {
      const bucket = this.buckets[this.bucketIndex(key)];
      const index = bucket.findIndex((entry) => entry.key === key);

      if (index === -1) {
        return false;
      }

      bucket.splice(index, 1);
      this.size -= 1;
      return true;
    }

    bucketLengths() {
      return this.buckets.map((bucket) => bucket.length);
    }
  }

  const table = new ChainedHashTable(4);

  for (const [key, value] of [
    ["ticket-1001", 1200],
    ["ticket-1002", 1800],
    ["ticket-1003", 950],
    ["ticket-1004", 2100],
  ]) {
    table.set(key, value);
  }

  table.set("ticket-1001", 1250);

  console.log("Bucket lengths:", table.bucketLengths());
  console.log("Updated ticket:", table.get("ticket-1001"));
  console.log("Deleted ticket:", table.delete("ticket-1002"));
  console.log("Delete missing ticket:", table.delete("missing"));

  assert.equal(table.size, 3);
  assert.equal(table.get("ticket-1001"), 1250);
  assert.equal(table.has("ticket-1002"), false);
}

function demonstrateAggregation() {
  console.log("\n=== Event aggregation ===");

  const events = [
    { service: "payments", status: 200 },
    { service: "identity", status: 401 },
    { service: "payments", status: 503 },
    { service: "payments", status: 200 },
    { service: "identity", status: 200 },
  ];

  const countsByService = new Map();

  for (const event of events) {
    if (!Number.isInteger(event.status) || event.status < 100) {
      throw new TypeError("Invalid HTTP status");
    }

    const current = countsByService.get(event.service) ?? {
      total: 0,
      failures: 0,
    };

    current.total += 1;
    if (event.status >= 400) {
      current.failures += 1;
    }

    countsByService.set(event.service, current);
  }

  console.log("Service metrics:", [...countsByService.entries()]);
  assert.equal(countsByService.get("payments").total, 3);
  assert.equal(countsByService.get("payments").failures, 1);
}

async function demonstrateRequestDeduplication() {
  console.log("\n=== Asynchronous request deduplication ===");

  const inFlight = new Map();
  let underlyingRequests = 0;

  async function fetchAccount(accountId) {
    if (typeof accountId !== "string" || accountId.trim() === "") {
      throw new TypeError("Account ID must be a non-empty string");
    }

    if (inFlight.has(accountId)) {
      return inFlight.get(accountId);
    }

    const request = (async () => {
      underlyingRequests += 1;

      // Represents asynchronous I/O without requiring an external service.
      await Promise.resolve();
      return { accountId, balance: 2500 };
    })();

    inFlight.set(accountId, request);

    try {
      return await request;
    } finally {
      // Remove only the same promise so a newer request is not deleted.
      if (inFlight.get(accountId) === request) {
        inFlight.delete(accountId);
      }
    }
  }

  const [first, second] = await Promise.all([
    fetchAccount("AC-100"),
    fetchAccount("AC-100"),
  ]);

  assert.deepEqual(first, second);
  console.log("Concurrent requests completed:", first);
  console.log("Underlying requests:", underlyingRequests);
}

function benchmarkLookup() {
  console.log("\n=== Lookup benchmark ===");

  const count = 100_000;
  const map = new Map();

  for (let key = 0; key < count; key += 1) {
    map.set(key, key * 3);
  }

  const start = performance.now();
  let checksum = 0;

  for (let query = 0; query < count; query += 1) {
    checksum += map.get(query);
  }

  console.log("Entries:", map.size);
  console.log("Elapsed milliseconds:", (performance.now() - start).toFixed(3));
  console.log("Checksum:", checksum);
}

async function main() {
  demonstrateMapBasics();
  demonstrateObjectKeySemantics();
  demonstrateCollisionChains();
  demonstrateAggregation();
  await demonstrateRequestDeduplication();
  benchmarkLookup();

  console.log("\nAll JavaScript demonstrations passed.");
}

main().catch((error) => {
  console.error("Demonstration failed:", error.message);
  process.exitCode = 1;
});
