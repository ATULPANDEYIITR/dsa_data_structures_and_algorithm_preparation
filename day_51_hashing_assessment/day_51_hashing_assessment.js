"use strict";

/**
 * Hashing assessment implemented as a Node.js-compatible module.
 * Run with: node hashing_assessment.js
 */

const assert = require("node:assert/strict");

function frequencyCounts(values) {
  const frequencies = new Map();

  for (const value of values) {
    frequencies.set(value, (frequencies.get(value) ?? 0) + 1);
  }

  return frequencies;
}

function findDuplicates(values) {
  const seen = new Set();
  const reported = new Set();
  const duplicates = [];

  for (const value of values) {
    if (seen.has(value) && !reported.has(value)) {
      duplicates.push(value);
      reported.add(value);
    }
    seen.add(value);
  }

  return duplicates;
}

function twoSum(values, target) {
  const earliestIndex = new Map();

  for (let index = 0; index < values.length; index++) {
    const value = values[index];
    const complement = target - value;

    if (earliestIndex.has(complement)) {
      return [earliestIndex.get(complement), index];
    }

    if (!earliestIndex.has(value)) {
      earliestIndex.set(value, index);
    }
  }

  return null;
}

function countSubarraysWithSum(values, target) {
  const prefixFrequency = new Map([[0, 1]]);
  let prefixSum = 0;
  let total = 0;

  for (const value of values) {
    prefixSum += value;
    total += prefixFrequency.get(prefixSum - target) ?? 0;
    prefixFrequency.set(prefixSum, (prefixFrequency.get(prefixSum) ?? 0) + 1);
  }

  return total;
}

function longestConsecutiveSequence(values) {
  const uniqueValues = new Set(values);
  let longest = 0;

  for (const value of uniqueValues) {
    if (!uniqueValues.has(value - 1)) {
      let length = 1;
      while (uniqueValues.has(value + length)) {
        length++;
      }
      longest = Math.max(longest, length);
    }
  }

  return longest;
}

function groupAnagrams(words) {
  const groups = new Map();

  for (const word of words) {
    if (typeof word !== "string" || !/^[a-z]+$/i.test(word)) {
      throw new TypeError("Anagram input must contain ASCII alphabetic words");
    }

    const signature = new Array(26).fill(0);
    for (const character of word.toLowerCase()) {
      signature[character.charCodeAt(0) - 97]++;
    }

    const key = signature.join(",");
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(word);
  }

  return [...groups.values()];
}

function longestUniqueSubstring(text) {
  const lastSeen = new Map();
  let left = 0;
  let longest = 0;
  let position = 0;

  // Iterate Unicode code points rather than UTF-16 code units.
  for (const character of text) {
    if (lastSeen.has(character)) {
      left = Math.max(left, lastSeen.get(character) + 1);
    }
    lastSeen.set(character, position);
    longest = Math.max(longest, position - left + 1);
    position++;
  }

  return longest;
}

function polynomialStringHash(text, base = 257, modulus = 1000000007) {
  if (!Number.isSafeInteger(base) || base < 1 ||
      !Number.isSafeInteger(modulus) || modulus < 2) {
    throw new RangeError("Invalid rolling-hash parameters");
  }

  let hash = 0;
  for (const character of text) {
    hash = (hash * base + character.codePointAt(0)) % modulus;
  }
  return hash;
}

function groupStringsByVerifiedHash(strings) {
  const buckets = new Map();

  for (const text of strings) {
    const hash = polynomialStringHash(text);
    if (!buckets.has(hash)) buckets.set(hash, []);

    const groups = buckets.get(hash);
    const matching = groups.find(group => group[0] === text);

    if (matching) {
      matching.push(text);
    } else {
      groups.push([text]);
    }
  }

  return [...buckets.values()].flat();
}

async function evaluateAssessment(cases) {
  const results = [];

  // Each test runs independently so one failure cannot suppress later tests.
  for (const testCase of cases) {
    try {
      await testCase.run();
      results.push({ name: testCase.name, passed: true });
    } catch (error) {
      results.push({
        name: testCase.name,
        passed: false,
        error: error.message
      });
    }
  }

  return results;
}

async function main() {
  const cases = [
    {
      name: "frequency",
      run: () => assert.deepEqual(
        [...frequencyCounts([1, 2, 2, 3, 1, 2])],
        [[1, 2], [2, 3], [3, 1]]
      )
    },
    {
      name: "duplicates",
      run: () => assert.deepEqual(findDuplicates([4, 2, 4, 2, 4]), [4, 2])
    },
    {
      name: "two sum",
      run: () => assert.deepEqual(twoSum([3, -2, 7, 5], 3), [1, 2])
    },
    {
      name: "no pair",
      run: () => assert.equal(twoSum([1, 2], 8), null)
    },
    {
      name: "prefix sums with negatives",
      run: () => assert.equal(countSubarraysWithSum([1, -1, 0], 0), 3)
    },
    {
      name: "consecutive sequence",
      run: () => assert.equal(longestConsecutiveSequence([100, 4, 200, 1, 3, 2]), 4)
    },
    {
      name: "anagrams",
      run: () => assert.equal(groupAnagrams(["eat", "tea", "ate"]).length, 1)
    },
    {
      name: "invalid anagram input",
      run: () => assert.throws(() => groupAnagrams(["valid", "bad word"]), TypeError)
    },
    {
      name: "Unicode unique substring",
      run: () => assert.equal(longestUniqueSubstring("😀a😀"), 2)
    },
    {
      name: "rolling hash determinism",
      run: () => assert.equal(polynomialStringHash("branch"), polynomialStringHash("branch"))
    },
    {
      name: "hash collisions do not imply equality",
      run: () => assert.deepEqual(
        groupStringsByVerifiedHash(["same", "other", "same"]),
        [["same", "same"], ["other"]]
      )
    }
  ];

  const results = await evaluateAssessment(cases);

  for (const result of results) {
    console.log(`${result.passed ? "PASS" : "FAIL"} | ${result.name}` +
      (result.error ? `: ${result.error}` : ""));
  }

  const passed = results.filter(result => result.passed).length;
  console.log(`\nScore: ${passed}/${results.length}`);

  if (passed !== results.length) process.exitCode = 1;
}

if (require.main === module) {
  main().catch(error => {
    console.error("Assessment execution failed:", error.message);
    process.exitCode = 1;
  });
}

module.exports = {
  frequencyCounts,
  findDuplicates,
  twoSum,
  countSubarraysWithSum,
  longestConsecutiveSequence,
  groupAnagrams,
  longestUniqueSubstring,
  polynomialStringHash,
  groupStringsByVerifiedHash
};
