/*
 * Day 10 — Best, Average and Worst Case
 *
 * Topics:
 *   - Linear search
 *   - Binary search
 *   - Sorting algorithms
 *   - Hash-table operations
 *   - Array operations
 *   - Linked-list operations
 *   - Complexity reference sheet
 *
 * Runtime:
 *   Node.js or a modern browser console.
 *
 * The examples are deliberately self-contained and require no packages.
 */

"use strict";

// ============================================================
// 1. COMPLEXITY BASICS
// ============================================================

function explainComplexityBasics() {
    console.log("\n" + "=".repeat(80));
    console.log("1. COMPLEXITY BASICS");
    console.log("=".repeat(80));

    const concepts = [
        ["Best case", "Most favorable valid input arrangement."],
        ["Average case", "Expected cost under a defined input distribution."],
        ["Worst case", "Maximum cost among valid inputs of size n."],
        ["Big O", "Asymptotic upper-bound notation."],
        ["Big Omega", "Asymptotic lower-bound notation."],
        ["Big Theta", "Tight asymptotic bound when growth matches."],
    ];

    for (const [name, definition] of concepts) {
        console.log(`${name}: ${definition}`);
    }

    console.log("\nCommon growth rates:");
    console.log("O(1)       constant");
    console.log("O(log n)   logarithmic");
    console.log("O(n)       linear");
    console.log("O(n log n) linearithmic");
    console.log("O(n²)      quadratic");
    console.log("O(2ⁿ)      exponential");
    console.log("O(n!)      factorial");
}


// ============================================================
// 2. LINEAR SEARCH
// ============================================================

function linearSearch(array, target) {
    for (let index = 0; index < array.length; index++) {
        if (array[index] === target) {
            return index;
        }
    }

    return -1;
}

function linearSearchWithComparisons(array, target) {
    let comparisons = 0;

    for (let index = 0; index < array.length; index++) {
        comparisons++;

        if (array[index] === target) {
            return {
                index,
                comparisons
            };
        }
    }

    return {
        index: -1,
        comparisons
    };
}

function demonstrateLinearSearch() {
    console.log("\n" + "=".repeat(80));
    console.log("2. LINEAR SEARCH");
    console.log("=".repeat(80));

    const data = [10, 20, 30, 40, 50];

    for (const target of [10, 30, 50, 999]) {
        const result = linearSearchWithComparisons(data, target);

        console.log(
            `Target ${target}: index=${result.index}, ` +
            `comparisons=${result.comparisons}`
        );
    }

    console.log("Best case   : O(1)");
    console.log("Average case: O(n)");
    console.log("Worst case  : O(n)");
    console.log("Space       : O(1)");
}


// ============================================================
// 3. BINARY SEARCH
// ============================================================

function binarySearch(array, target) {
    let left = 0;
    let right = array.length - 1;

    while (left <= right) {
        const middle = left + Math.floor((right - left) / 2);

        if (array[middle] === target) {
            return middle;
        }

        if (array[middle] < target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return -1;
}

function binarySearchWithComparisons(array, target) {
    let left = 0;
    let right = array.length - 1;
    let comparisons = 0;

    while (left <= right) {
        const middle = left + Math.floor((right - left) / 2);
        comparisons++;

        if (array[middle] === target) {
            return {
                index: middle,
                comparisons
            };
        }

        if (array[middle] < target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return {
        index: -1,
        comparisons
    };
}

function demonstrateBinarySearch() {
    console.log("\n" + "=".repeat(80));
    console.log("3. BINARY SEARCH");
    console.log("=".repeat(80));

    const data = [10, 20, 30, 40, 50, 60, 70];

    for (const target of [40, 10, 70, 999]) {
        const result = binarySearchWithComparisons(data, target);

        console.log(
            `Target ${target}: index=${result.index}, ` +
            `comparisons=${result.comparisons}`
        );
    }

    console.log("Best case   : O(1)");
    console.log("Average case: O(log n)");
    console.log("Worst case  : O(log n)");
    console.log("Requirement : sorted data");
}


// ============================================================
// 4. BUBBLE SORT
// ============================================================

function bubbleSort(input) {
    const array = [...input];

    for (let end = array.length - 1; end > 0; end--) {
        let swapped = false;

        for (let index = 0; index < end; index++) {
            if (array[index] > array[index + 1]) {
                [array[index], array[index + 1]] =
                    [array[index + 1], array[index]];

                swapped = true;
            }
        }

        if (!swapped) {
            break;
        }
    }

    return array;
}


// ============================================================
// 5. SELECTION SORT
// ============================================================

function selectionSort(input) {
    const array = [...input];

    for (let position = 0; position < array.length; position++) {
        let minimumIndex = position;

        for (
            let index = position + 1;
            index < array.length;
            index++
        ) {
            if (array[index] < array[minimumIndex]) {
                minimumIndex = index;
            }
        }

        [array[position], array[minimumIndex]] =
            [array[minimumIndex], array[position]];
    }

    return array;
}


// ============================================================
// 6. INSERTION SORT
// ============================================================

function insertionSort(input) {
    const array = [...input];

    for (let position = 1; position < array.length; position++) {
        const currentValue = array[position];
        let previous = position - 1;

        while (
            previous >= 0 &&
            array[previous] > currentValue
        ) {
            array[previous + 1] = array[previous];
            previous--;
        }

        array[previous + 1] = currentValue;
    }

    return array;
}


// ============================================================
// 7. MERGE SORT
// ============================================================

function merge(left, right) {
    const result = [];
    let leftIndex = 0;
    let rightIndex = 0;

    while (
        leftIndex < left.length &&
        rightIndex < right.length
    ) {
        if (left[leftIndex] <= right[rightIndex]) {
            result.push(left[leftIndex]);
            leftIndex++;
        } else {
            result.push(right[rightIndex]);
            rightIndex++;
        }
    }

    result.push(...left.slice(leftIndex));
    result.push(...right.slice(rightIndex));

    return result;
}

function mergeSort(input) {
    if (input.length <= 1) {
        return [...input];
    }

    const middle = Math.floor(input.length / 2);

    const left = mergeSort(input.slice(0, middle));
    const right = mergeSort(input.slice(middle));

    return merge(left, right);
}


// ============================================================
// 8. QUICKSORT
// ============================================================

function quickSort(input) {
    if (input.length <= 1) {
        return [...input];
    }

    const pivot = input[Math.floor(input.length / 2)];
    const smaller = [];
    const equal = [];
    const greater = [];

    for (const value of input) {
        if (value < pivot) {
            smaller.push(value);
        } else if (value > pivot) {
            greater.push(value);
        } else {
            equal.push(value);
        }
    }

    return [
        ...quickSort(smaller),
        ...equal,
        ...quickSort(greater)
    ];
}


// ============================================================
// 9. SORTING DEMONSTRATION
// ============================================================

function demonstrateSorting() {
    console.log("\n" + "=".repeat(80));
    console.log("4. SORTING ALGORITHMS");
    console.log("=".repeat(80));

    const data = [7, 2, 9, 1, 5, 2, 8];

    const algorithms = {
        "Bubble sort": bubbleSort,
        "Selection sort": selectionSort,
        "Insertion sort": insertionSort,
        "Merge sort": mergeSort,
        "Quicksort": quickSort,
        "JavaScript sort": array => [...array].sort((a, b) => a - b)
    };

    console.log("Original:", data);

    for (const [name, algorithm] of Object.entries(algorithms)) {
        console.log(`${name}:`, algorithm(data));
    }

    console.log("\nComplexity:");
    console.log("Bubble sort   : best O(n), average O(n²), worst O(n²)");
    console.log("Selection sort: best O(n²), average O(n²), worst O(n²)");
    console.log("Insertion sort: best O(n), average O(n²), worst O(n²)");
    console.log("Merge sort    : best/average/worst O(n log n)");
    console.log("Quicksort     : average O(n log n), worst O(n²)");
}


// ============================================================
// 10. JAVASCRIPT ARRAY OPERATIONS
// ============================================================

function demonstrateArrayOperations() {
    console.log("\n" + "=".repeat(80));
    console.log("5. JAVASCRIPT ARRAY OPERATIONS");
    console.log("=".repeat(80));

    const array = [10, 20, 30, 40, 50];

    console.log("Index access:", array[2]);
    console.log("Index access complexity: O(1)");

    array[2] = 35;
    console.log("After update:", array);

    array.push(60);
    console.log("After push:", array);
    console.log("Push is typically O(1) amortized.");

    array.pop();
    console.log("After pop:", array);
    console.log("Pop from the end is O(1).");

    array.unshift(5);
    console.log("After unshift:", array);
    console.log("Unshift is O(n) because existing elements shift.");

    array.shift();
    console.log("After shift:", array);
    console.log("Shift is O(n) because existing elements shift.");

    console.log("Includes:", array.includes(30));
    console.log("Linear search with includes: O(n)");
}


// ============================================================
// 11. HASH TABLES WITH MAP
// ============================================================

function demonstrateHashTable() {
    console.log("\n" + "=".repeat(80));
    console.log("6. HASH-TABLE OPERATIONS");
    console.log("=".repeat(80));

    const users = new Map();

    users.set("name", "Atul");
    users.set("role", "Developer");
    users.set("topic", "Algorithms");

    console.log("name:", users.get("name"));
    console.log("Has role:", users.has("role"));

    users.set("role", "Engineer");
    console.log("Updated role:", users.get("role"));

    users.delete("topic");
    console.log("Has topic after delete:", users.has("topic"));

    console.log("\nTypical Map complexity:");
    console.log("Insert: expected O(1)");
    console.log("Lookup: expected O(1)");
    console.log("Delete: expected O(1)");

    console.log(
        "These are expected performance characteristics, not universal " +
        "worst-case guarantees."
    );
}


// ============================================================
// 12. LINKED LIST
// ============================================================

class LinkedNode {
    constructor(value) {
        this.value = value;
        this.next = null;
    }
}

class SinglyLinkedList {
    constructor() {
        this.head = null;
        this.tail = null;
        this.size = 0;
    }

    prepend(value) {
        const node = new LinkedNode(value);
        node.next = this.head;
        this.head = node;

        if (this.tail === null) {
            this.tail = node;
        }

        this.size++;
    }

    append(value) {
        const node = new LinkedNode(value);

        if (this.head === null) {
            this.head = node;
            this.tail = node;
        } else {
            this.tail.next = node;
            this.tail = node;
        }

        this.size++;
    }

    find(value) {
        let current = this.head;

        while (current !== null) {
            if (current.value === value) {
                return current;
            }

            current = current.next;
        }

        return null;
    }

    getAt(index) {
        if (index < 0 || index >= this.size) {
            throw new RangeError("Linked-list index out of range");
        }

        let current = this.head;

        for (let position = 0; position < index; position++) {
            current = current.next;
        }

        return current.value;
    }

    deleteValue(value) {
        let previous = null;
        let current = this.head;

        while (current !== null) {
            if (current.value === value) {
                if (previous === null) {
                    this.head = current.next;
                } else {
                    previous.next = current.next;
                }

                if (current === this.tail) {
                    this.tail = previous;
                }

                this.size--;

                if (this.size === 0) {
                    this.head = null;
                    this.tail = null;
                }

                return true;
            }

            previous = current;
            current = current.next;
        }

        return false;
    }

    toArray() {
        const values = [];
        let current = this.head;

        while (current !== null) {
            values.push(current.value);
            current = current.next;
        }

        return values;
    }
}

function demonstrateLinkedList() {
    console.log("\n" + "=".repeat(80));
    console.log("7. LINKED-LIST OPERATIONS");
    console.log("=".repeat(80));

    const list = new SinglyLinkedList();

    list.append(20);
    list.append(30);
    list.prepend(10);
    list.append(40);

    console.log("List:", list.toArray());
    console.log("Size:", list.size);

    console.log("Index 2:", list.getAt(2));
    console.log("Index access: O(n)");

    console.log("Find 30:", list.find(30)?.value ?? null);
    console.log("Search: O(n)");

    console.log("Delete 30:", list.deleteValue(30));
    console.log("After deletion:", list.toArray());

    console.log("\nComplexity:");
    console.log("Prepend: O(1)");
    console.log("Append with tail: O(1)");
    console.log("Search: O(n)");
    console.log("Access by index: O(n)");
    console.log("Delete by value: O(n)");
}


// ============================================================
// 13. ASYNCHRONOUS COMPLEXITY EXAMPLE
// ============================================================

function simulateAsynchronousWork() {
    console.log("\n" + "=".repeat(80));
    console.log("8. JAVASCRIPT RUNTIME AND ASYNCHRONOUS WORK");
    console.log("=".repeat(80));

    console.log(
        "Asynchronous scheduling changes when a callback executes, " +
        "but it does not automatically improve the algorithmic complexity " +
        "of the work performed by that callback."
    );

    return new Promise(resolve => {
        setTimeout(() => {
            console.log("Asynchronous callback executed.");
            resolve();
        }, 0);
    });
}


// ============================================================
// 14. PERFORMANCE BENCHMARK
// ============================================================

function benchmark(functionToMeasure, data, repetitions = 3) {
    const start = performance.now();

    for (let repetition = 0; repetition < repetitions; repetition++) {
        functionToMeasure(data);
    }

    const elapsed = performance.now() - start;

    return elapsed / repetitions;
}

function demonstrateBenchmark() {
    console.log("\n" + "=".repeat(80));
    console.log("9. EMPIRICAL PERFORMANCE");
    console.log("=".repeat(80));

    const sizes = [100, 500, 1000];

    const algorithms = {
        "Insertion sort": insertionSort,
        "Merge sort": mergeSort,
        "Quicksort": quickSort,
        "Built-in sort": array => [...array].sort((a, b) => a - b)
    };

    for (const size of sizes) {
        const data = Array.from(
            { length: size },
            () => Math.floor(Math.random() * 20000) - 10000
        );

        console.log(`\nInput size: ${size}`);

        for (const [name, algorithm] of Object.entries(algorithms)) {
            const milliseconds = benchmark(
                algorithm,
                data,
                size >= 1000 ? 1 : 3
            );

            console.log(
                `${name.padEnd(18)} ${milliseconds.toFixed(4)} ms`
            );
        }
    }

    console.log(
        "\nBenchmarks depend on hardware, runtime implementation, " +
        "garbage collection, and system load."
    );
}


// ============================================================
// 15. EDGE CASES
// ============================================================

function demonstrateEdgeCases() {
    console.log("\n" + "=".repeat(80));
    console.log("10. EDGE CASES");
    console.log("=".repeat(80));

    const cases = [
        [],
        [42],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [3, 3, 3, 3],
        [-5, 0, 5, -10, 10]
    ];

    for (const data of cases) {
        console.log("\nInput:", data);
        console.log("Insertion:", insertionSort(data));
        console.log("Merge:", mergeSort(data));
        console.log("Quick:", quickSort(data));
    }

    console.log("\nEmpty binary search:", binarySearch([], 1));
    console.log(
        "Single-element binary search:",
        binarySearch([42], 42)
    );
}


// ============================================================
// 16. COMPLEXITY REFERENCE SHEET
// ============================================================

function printComplexityReferenceSheet() {
    console.log("\n" + "=".repeat(80));
    console.log("11. COMPLEXITY REFERENCE SHEET");
    console.log("=".repeat(80));

    console.log(`
SEARCH
----------------------------------------------------------------------
Linear search
  Best       O(1)
  Average    O(n)
  Worst      O(n)
  Space      O(1)

Binary search
  Best       O(1)
  Average    O(log n)
  Worst      O(log n)
  Space      O(1) iterative
  Requirement: sorted data


SORTING
----------------------------------------------------------------------
Bubble sort
  Best       O(n)
  Average    O(n²)
  Worst      O(n²)

Selection sort
  Best       O(n²)
  Average    O(n²)
  Worst      O(n²)

Insertion sort
  Best       O(n)
  Average    O(n²)
  Worst      O(n²)

Merge sort
  Best       O(n log n)
  Average    O(n log n)
  Worst      O(n log n)

Quicksort
  Best       O(n log n)
  Average    O(n log n)
  Worst      O(n²)


HASH TABLE
----------------------------------------------------------------------
Insert       Expected O(1), pathological worst O(n)
Lookup       Expected O(1), pathological worst O(n)
Delete       Expected O(1), pathological worst O(n)
Space        O(n)


ARRAY
----------------------------------------------------------------------
Index access       O(1)
Index update       O(1)
Append             O(1) amortized
Pop from end       O(1)
Insert at front    O(n)
Delete at front    O(n)
Search             O(n)


LINKED LIST
----------------------------------------------------------------------
Access by index    O(n)
Search             O(n)
Prepend            O(1)
Append with tail   O(1)
Delete by value    O(n)
Space              O(n)


GROWTH ORDER
----------------------------------------------------------------------
O(1)
O(log n)
O(n)
O(n log n)
O(n²)
O(2ⁿ)
O(n!)
`);
}


// ============================================================
// 17. CORRECTNESS TESTS
// ============================================================

function runTests() {
    console.log("\n" + "=".repeat(80));
    console.log("12. CORRECTNESS TESTS");
    console.log("=".repeat(80));

    const data = [7, 2, 9, 1, 5, 2, 8, -1];
    const expected = [...data].sort((a, b) => a - b);

    const algorithms = [
        bubbleSort,
        selectionSort,
        insertionSort,
        mergeSort,
        quickSort
    ];

    for (const algorithm of algorithms) {
        const result = algorithm(data);

        if (JSON.stringify(result) !== JSON.stringify(expected)) {
            throw new Error(`${algorithm.name} failed`);
        }
    }

    console.assert(linearSearch([1, 2, 3], 1) === 0);
    console.assert(linearSearch([1, 2, 3], 3) === 2);
    console.assert(linearSearch([1, 2, 3], 9) === -1);

    console.assert(binarySearch([1, 2, 3, 4, 5], 1) === 0);
    console.assert(binarySearch([1, 2, 3, 4, 5], 3) === 2);
    console.assert(binarySearch([1, 2, 3, 4, 5], 5) === 4);
    console.assert(binarySearch([1, 2, 3, 4, 5], 9) === -1);

    const list = new SinglyLinkedList();
    list.append(10);
    list.append(20);
    list.prepend(5);

    console.assert(
        JSON.stringify(list.toArray()) === JSON.stringify([5, 10, 20])
    );

    console.assert(list.getAt(1) === 10);
    console.assert(list.deleteValue(10) === true);
    console.assert(
        JSON.stringify(list.toArray()) === JSON.stringify([5, 20])
    );

    const map = new Map();
    map.set("language", "JavaScript");
    console.assert(map.get("language") === "JavaScript");
    console.assert(map.has("language"));

    console.log("All tests passed.");
}


// ============================================================
// 18. MAIN
// ============================================================

async function main() {
    console.log("=".repeat(80));
    console.log("DAY 10 — BEST, AVERAGE AND WORST CASE");
    console.log("=".repeat(80));

    explainComplexityBasics();
    demonstrateLinearSearch();
    demonstrateBinarySearch();
    demonstrateSorting();
    demonstrateArrayOperations();
    demonstrateHashTable();
    demonstrateLinkedList();
    await simulateAsynchronousWork();
    demonstrateBenchmark();
    demonstrateEdgeCases();
    printComplexityReferenceSheet();
    runTests();

    console.log("\n" + "=".repeat(80));
    console.log("END OF DAY 10");
    console.log("=".repeat(80));
}

if (typeof module !== "undefined" && require.main === module) {
    main().catch(error => {
        console.error("Program failed:", error);
        process.exitCode = 1;
    });
}
