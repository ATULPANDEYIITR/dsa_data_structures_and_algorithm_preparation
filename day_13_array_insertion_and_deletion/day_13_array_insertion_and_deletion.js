/*
 * Day 13 — Array Insertion and Deletion
 *
 * This standalone JavaScript file demonstrates:
 * - insertion at the beginning
 * - insertion at the end
 * - insertion at an index
 * - deletion from the beginning
 * - deletion from the end
 * - deletion by index
 * - deletion by value
 * - shifting elements
 * - stable and unordered deletion
 * - JavaScript Array behavior
 * - dynamic-array concepts
 * - edge cases
 * - validation
 * - complexity
 * - practical browser/application patterns
 *
 * Run with:
 *     node day13_array_insertion_deletion.js
 *
 * The examples use standard JavaScript only.
 */

"use strict";

// ---------------------------------------------------------------------------
// 1. DISPLAY HELPERS
// ---------------------------------------------------------------------------

function printSection(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function displayArray(values, label = "Array") {
    console.log(`${label}: [${values.join(", ")}]`);

    if (values.length > 0) {
        console.log("Index:", values.map((_, index) => String(index).padStart(4)).join(""));
        console.log("Value:", values.map(value => String(value).padStart(4)).join(""));
    }
}

// ---------------------------------------------------------------------------
// 2. INSERTION AT THE BEGINNING
// ---------------------------------------------------------------------------

function insertAtBeginning(values, value) {
    /*
     * Array.unshift() performs the operation directly, but this implementation
     * explicitly demonstrates the underlying conceptual shifting process.
     *
     * Complexity: O(n)
     */
    values.push(undefined);

    for (let index = values.length - 1; index > 0; index--) {
        values[index] = values[index - 1];
    }

    values[0] = value;
}

// ---------------------------------------------------------------------------
// 3. INSERTION AT THE END
// ---------------------------------------------------------------------------

function insertAtEnd(values, value) {
    /*
     * push() appends to the array.
     *
     * Dynamic arrays normally provide amortized O(1) append performance.
     */
    values.push(value);
}

// ---------------------------------------------------------------------------
// 4. INSERTION AT AN INDEX
// ---------------------------------------------------------------------------

function insertAtPosition(values, index, value) {
    if (!Number.isInteger(index) || index < 0 || index > values.length) {
        throw new RangeError(`Invalid insertion index: ${index}`);
    }

    values.push(undefined);

    for (let current = values.length - 1; current > index; current--) {
        values[current] = values[current - 1];
    }

    values[index] = value;
}

// ---------------------------------------------------------------------------
// 5. DELETION FROM THE BEGINNING
// ---------------------------------------------------------------------------

function deleteFromBeginning(values) {
    if (values.length === 0) {
        throw new Error("Cannot delete from an empty array.");
    }

    const removed = values[0];

    for (let index = 1; index < values.length; index++) {
        values[index - 1] = values[index];
    }

    values.pop();
    return removed;
}

// ---------------------------------------------------------------------------
// 6. DELETION FROM THE END
// ---------------------------------------------------------------------------

function deleteFromEnd(values) {
    if (values.length === 0) {
        throw new Error("Cannot delete from an empty array.");
    }

    return values.pop();
}

// ---------------------------------------------------------------------------
// 7. DELETION BY INDEX
// ---------------------------------------------------------------------------

function deleteByIndex(values, index) {
    if (!Number.isInteger(index) || index < 0 || index >= values.length) {
        throw new RangeError(`Invalid deletion index: ${index}`);
    }

    const removed = values[index];

    for (let current = index + 1; current < values.length; current++) {
        values[current - 1] = values[current];
    }

    values.pop();
    return removed;
}

// ---------------------------------------------------------------------------
// 8. DELETION BY VALUE
// ---------------------------------------------------------------------------

function deleteByValue(values, value) {
    /*
     * indexOf() performs a linear search.
     * Once the position is known, deleting from that position can require
     * another linear amount of shifting.
     */
    const index = values.indexOf(value);

    if (index === -1) {
        throw new Error(`Value ${String(value)} was not found.`);
    }

    return deleteByIndex(values, index);
}

function deleteAllByValue(values, value) {
    /*
     * The write-pointer pattern removes all matching values in O(n)
     * while preserving the order of values that remain.
     */
    let writeIndex = 0;
    let removedCount = 0;

    for (let readIndex = 0; readIndex < values.length; readIndex++) {
        if (Object.is(values[readIndex], value)) {
            removedCount++;
        } else {
            values[writeIndex] = values[readIndex];
            writeIndex++;
        }
    }

    values.length = writeIndex;
    return removedCount;
}

// ---------------------------------------------------------------------------
// 9. SHIFTING
// ---------------------------------------------------------------------------

function shiftRight(values, positions = 1) {
    if (values.length === 0) {
        return;
    }

    positions = ((positions % values.length) + values.length) % values.length;

    if (positions === 0) {
        return;
    }

    const shifted = values.splice(values.length - positions, positions);
    values.unshift(...shifted);
}

function shiftLeft(values, positions = 1) {
    if (values.length === 0) {
        return;
    }

    positions = ((positions % values.length) + values.length) % values.length;

    if (positions === 0) {
        return;
    }

    const shifted = values.splice(0, positions);
    values.push(...shifted);
}

// ---------------------------------------------------------------------------
// 10. STABLE AND UNORDERED DELETION
// ---------------------------------------------------------------------------

function deleteUnordered(values, index) {
    /*
     * If ordering does not matter, replace the deleted element with the
     * final element. This avoids shifting all subsequent elements.
     *
     * Complexity: O(1).
     */
    if (!Number.isInteger(index) || index < 0 || index >= values.length) {
        throw new RangeError("Invalid index.");
    }

    const removed = values[index];
    const lastIndex = values.length - 1;

    if (index !== lastIndex) {
        values[index] = values[lastIndex];
    }

    values.pop();
    return removed;
}

// ---------------------------------------------------------------------------
// 11. MANUAL DYNAMIC ARRAY MODEL
// ---------------------------------------------------------------------------

class DynamicArray {
    /*
     * JavaScript's built-in Array already provides dynamic-array behavior.
     * This class models the underlying idea explicitly using a fixed-size
     * ordinary array plus logical size and capacity.
     */
    constructor(initialCapacity = 4) {
        if (!Number.isInteger(initialCapacity) || initialCapacity < 1) {
            throw new RangeError("Capacity must be a positive integer.");
        }

        this.data = new Array(initialCapacity);
        this.size = 0;
    }

    get capacity() {
        return this.data.length;
    }

    resize(newCapacity) {
        if (newCapacity < this.size) {
            throw new Error("New capacity cannot be smaller than size.");
        }

        const newData = new Array(newCapacity);

        for (let index = 0; index < this.size; index++) {
            newData[index] = this.data[index];
        }

        this.data = newData;
    }

    ensureCapacity() {
        if (this.size === this.capacity) {
            this.resize(Math.max(1, this.capacity * 2));
        }
    }

    append(value) {
        this.ensureCapacity();
        this.data[this.size] = value;
        this.size++;
    }

    insert(index, value) {
        if (!Number.isInteger(index) || index < 0 || index > this.size) {
            throw new RangeError("Invalid insertion index.");
        }

        this.ensureCapacity();

        for (let current = this.size; current > index; current--) {
            this.data[current] = this.data[current - 1];
        }

        this.data[index] = value;
        this.size++;
    }

    pop(index = this.size - 1) {
        if (this.size === 0) {
            throw new Error("Cannot pop from an empty dynamic array.");
        }

        if (!Number.isInteger(index)) {
            throw new RangeError("Index must be an integer.");
        }

        if (index < 0) {
            index += this.size;
        }

        if (index < 0 || index >= this.size) {
            throw new RangeError("Index out of range.");
        }

        const removed = this.data[index];

        for (let current = index + 1; current < this.size; current++) {
            this.data[current - 1] = this.data[current];
        }

        this.size--;
        this.data[this.size] = undefined;

        if (this.size > 0 && this.size <= Math.floor(this.capacity / 4)) {
            const newCapacity = Math.max(1, Math.floor(this.capacity / 2));

            if (newCapacity >= this.size) {
                this.resize(newCapacity);
            }
        }

        return removed;
    }

    get(index) {
        if (!Number.isInteger(index)) {
            throw new RangeError("Index must be an integer.");
        }

        if (index < 0) {
            index += this.size;
        }

        if (index < 0 || index >= this.size) {
            throw new RangeError("Index out of range.");
        }

        return this.data[index];
    }

    toArray() {
        return this.data.slice(0, this.size);
    }

    toString() {
        return `DynamicArray(size=${this.size}, capacity=${this.capacity}, data=[${this.toArray().join(", ")}])`;
    }
}

// ---------------------------------------------------------------------------
// 12. SHIFT COST CALCULATIONS
// ---------------------------------------------------------------------------

function insertionShiftCount(size, index) {
    if (index < 0 || index > size) {
        throw new RangeError("Invalid insertion index.");
    }

    return size - index;
}

function deletionShiftCount(size, index) {
    if (index < 0 || index >= size) {
        throw new RangeError("Invalid deletion index.");
    }

    return size - index - 1;
}

function showShiftCosts(size) {
    console.log(`Array size = ${size}`);
    console.log("Index | Insertion shifts | Deletion shifts");

    for (let index = 0; index < size; index++) {
        console.log(
            `${String(index).padStart(5)} |` +
            `${String(insertionShiftCount(size, index)).padStart(17)} |` +
            `${String(deletionShiftCount(size, index)).padStart(16)}`
        );
    }

    console.log(
        `${String(size).padStart(5)} |` +
        `${String(0).padStart(17)} |` +
        `${"N/A".padStart(16)}`
    );
}

// ---------------------------------------------------------------------------
// 13. REAL APPLICATION: TASK LIST
// ---------------------------------------------------------------------------

class TaskList {
    /*
     * This simple application models a prioritized task list.
     * Tasks are stored in an array, so inserting a task near the beginning
     * requires shifting existing tasks.
     */
    constructor() {
        this.tasks = [];
    }

    addTaskAtEnd(task) {
        if (typeof task !== "string" || task.trim() === "") {
            throw new TypeError("Task must be a non-empty string.");
        }

        this.tasks.push(task.trim());
    }

    addPriorityTask(task, priorityIndex) {
        if (typeof task !== "string" || task.trim() === "") {
            throw new TypeError("Task must be a non-empty string.");
        }

        insertAtPosition(this.tasks, priorityIndex, task.trim());
    }

    removeTaskAtIndex(index) {
        return deleteByIndex(this.tasks, index);
    }

    removeTaskByName(task) {
        return deleteByValue(this.tasks, task);
    }

    show() {
        this.tasks.forEach((task, index) => {
            console.log(`${index + 1}. ${task}`);
        });
    }
}

// ---------------------------------------------------------------------------
// 14. ERROR HANDLING
// ---------------------------------------------------------------------------

function demonstrateErrors() {
    const operations = [
        ["delete empty array", () => deleteFromEnd([])],
        ["invalid insertion index", () => insertAtPosition([1, 2], 5, 3)],
        ["invalid deletion index", () => deleteByIndex([1, 2], 5)],
        ["missing value", () => deleteByValue([1, 2], 99)]
    ];

    for (const [description, operation] of operations) {
        try {
            operation();
        } catch (error) {
            console.log(`${description}: handled -> ${error.message}`);
        }
    }
}

// ---------------------------------------------------------------------------
// 15. TESTS
// ---------------------------------------------------------------------------

function assertEqual(actual, expected, message) {
    const actualString = JSON.stringify(actual);
    const expectedString = JSON.stringify(expected);

    if (actualString !== expectedString) {
        throw new Error(
            `${message}\nExpected: ${expectedString}\nActual: ${actualString}`
        );
    }
}

function runTests() {
    const values = [10, 20, 30];

    insertAtBeginning(values, 5);
    assertEqual(values, [5, 10, 20, 30], "Beginning insertion failed.");

    insertAtEnd(values, 40);
    assertEqual(values, [5, 10, 20, 30, 40], "End insertion failed.");

    insertAtPosition(values, 2, 15);
    assertEqual(
        values,
        [5, 10, 15, 20, 30, 40],
        "Position insertion failed."
    );

    assertEqual(deleteFromBeginning(values), 5, "Beginning deletion failed.");
    assertEqual(deleteFromEnd(values), 40, "End deletion failed.");
    assertEqual(deleteByIndex(values, 1), 15, "Index deletion failed.");

    assertEqual(deleteByValue(values, 20), 20, "Value deletion failed.");
    assertEqual(values, [10, 30], "Unexpected final array.");

    const duplicates = [1, 2, 1, 3, 1];
    assertEqual(deleteAllByValue(duplicates, 1), 3, "Duplicate deletion failed.");
    assertEqual(duplicates, [2, 3], "Delete-all operation failed.");

    const shifted = [1, 2, 3, 4];
    shiftRight(shifted);
    assertEqual(shifted, [4, 1, 2, 3], "Right shift failed.");

    shiftLeft(shifted);
    assertEqual(shifted, [1, 2, 3, 4], "Left shift failed.");

    const unordered = [10, 20, 30, 40];
    deleteUnordered(unordered, 1);
    assertEqual(unordered, [10, 40, 30], "Unordered deletion failed.");

    const dynamic = new DynamicArray(2);

    for (let value = 0; value < 10; value++) {
        dynamic.append(value);
    }

    if (dynamic.size !== 10 || dynamic.get(0) !== 0 || dynamic.get(-1) !== 9) {
        throw new Error("Dynamic array append/get test failed.");
    }

    dynamic.insert(5, 100);

    if (dynamic.get(5) !== 100) {
        throw new Error("Dynamic array insertion failed.");
    }

    if (dynamic.pop(5) !== 100) {
        throw new Error("Dynamic array deletion failed.");
    }

    console.log("All tests passed.");
}

// ---------------------------------------------------------------------------
// 16. PERFORMANCE MEASUREMENT
// ---------------------------------------------------------------------------

function measureOperation(operation, repeat = 1000) {
    const start = performance.now();

    for (let iteration = 0; iteration < repeat; iteration++) {
        operation();
    }

    return performance.now() - start;
}

function benchmark() {
    const size = 10000;

    const beginningTime = measureOperation(
        () => insertAtBeginning(Array.from({ length: size }, (_, i) => i), -1),
        20
    );

    const endingTime = measureOperation(
        () => insertAtEnd(Array.from({ length: size }, (_, i) => i), -1),
        20
    );

    console.log(`Beginning insertion: ${beginningTime.toFixed(4)} ms`);
    console.log(`End insertion:       ${endingTime.toFixed(4)} ms`);
    console.log(
        "Timing is machine-dependent; the complexity difference is the important observation."
    );
}

// ---------------------------------------------------------------------------
// 17. MAIN DEMONSTRATION
// ---------------------------------------------------------------------------

function main() {
    printSection("DAY 13 — ARRAY INSERTION AND DELETION");

    printSection("Basic insertion");
    const values = [10, 20, 30];

    displayArray(values);

    insertAtBeginning(values, 5);
    displayArray(values, "After beginning insertion");

    insertAtEnd(values, 40);
    displayArray(values, "After end insertion");

    insertAtPosition(values, 2, 15);
    displayArray(values, "After index insertion");

    printSection("Basic deletion");

    console.log("Removed from beginning:", deleteFromBeginning(values));
    displayArray(values);

    console.log("Removed from end:", deleteFromEnd(values));
    displayArray(values);

    console.log("Removed by index:", deleteByIndex(values, 1));
    displayArray(values);

    const duplicates = [10, 20, 30, 20, 40];
    console.log("Removed by value:", deleteByValue(duplicates, 20));
    displayArray(duplicates);

    printSection("Shifting");
    const shifted = [1, 2, 3, 4, 5];

    shiftRight(shifted, 2);
    displayArray(shifted, "Right shift by 2");

    shiftLeft(shifted, 3);
    displayArray(shifted, "Left shift by 3");

    printSection("Shift cost");
    showShiftCosts(8);

    printSection("Stable versus unordered deletion");
    const stable = [10, 20, 30, 40, 50];
    const unordered = stable.slice();

    deleteByIndex(stable, 1);
    deleteUnordered(unordered, 1);

    displayArray(stable, "Stable deletion");
    displayArray(unordered, "Unordered deletion");

    printSection("Dynamic array model");
    const dynamic = new DynamicArray(2);

    [10, 20, 30, 40].forEach(value => {
        dynamic.append(value);
        console.log(dynamic.toString());
    });

    dynamic.insert(2, 25);
    console.log("After insertion:", dynamic.toString());

    console.log("Removed:", dynamic.pop(1));
    console.log(dynamic.toString());

    printSection("Real application");
    const tasks = new TaskList();

    tasks.addTaskAtEnd("Write documentation");
    tasks.addTaskAtEnd("Run automated tests");
    tasks.addPriorityTask("Fix production bug", 0);

    tasks.show();

    console.log("Removing:", tasks.removeTaskByName("Run automated tests"));
    tasks.show();

    printSection("Error handling");
    demonstrateErrors();

    printSection("Tests");
    runTests();

    printSection("Performance");
    benchmark();

    printSection("Complexity reference");
    console.log(`
Operation                         Typical complexity
----------------------------------------------------
Array access by index             O(1)
Insert at beginning              O(n)
Insert at middle                 O(n)
Insert at end                    O(1) amortized
Delete from beginning            O(n)
Delete from middle               O(n)
Delete from end                  O(1)
Delete by index                  O(n) worst case
Delete by value                  O(n)
Delete all matching values       O(n)
Unordered deletion by index      O(1)
Linear search                    O(n)

The reason is element movement. An array stores elements in indexed
positions, so preserving order after an insertion or deletion can require
moving many elements.
`);
}

main();
