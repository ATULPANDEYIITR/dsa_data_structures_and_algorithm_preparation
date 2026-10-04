"use strict";

/*
 * Linked-list insertion and deletion.
 *
 * This file uses a singly linked list and focuses on pointer/link
 * manipulation rather than JavaScript's built-in Array methods.
 *
 * Positions are zero-based.
 */

class Node {
    constructor(value) {
        this.value = value;
        this.next = null;
    }
}

class SinglyLinkedList {
    constructor(values = []) {
        this.head = null;
        this.size = 0;

        for (const value of values) {
            this.insertAtEnd(value);
        }
    }

    isEmpty() {
        return this.head === null;
    }

    toArray() {
        const result = [];
        let current = this.head;

        while (current !== null) {
            result.push(current.value);
            current = current.next;
        }

        return result;
    }

    toString() {
        return this.isEmpty() ? "EMPTY" : this.toArray().join(" -> ");
    }

    validateInsertPosition(position) {
        if (!Number.isInteger(position)) {
            throw new TypeError("Insertion position must be an integer.");
        }

        if (position < 0 || position > this.size) {
            throw new RangeError(
                `Insertion position ${position} must be between 0 and ${this.size}.`
            );
        }
    }

    validateDeletePosition(position) {
        if (!Number.isInteger(position)) {
            throw new TypeError("Deletion position must be an integer.");
        }

        if (position < 0 || position >= this.size) {
            throw new RangeError(
                `Deletion position ${position} must be between 0 and ${this.size - 1}.`
            );
        }
    }

    insertAtBeginning(value) {
        const node = new Node(value);

        // The new node inherits the old head before head is redirected.
        node.next = this.head;
        this.head = node;
        this.size += 1;
    }

    insertAtEnd(value) {
        const node = new Node(value);

        if (this.head === null) {
            this.head = node;
            this.size += 1;
            return;
        }

        let current = this.head;
        while (current.next !== null) {
            current = current.next;
        }

        current.next = node;
        this.size += 1;
    }

    insertAtPosition(position, value) {
        this.validateInsertPosition(position);

        if (position === 0) {
            this.insertAtBeginning(value);
            return;
        }

        if (position === this.size) {
            this.insertAtEnd(value);
            return;
        }

        let previous = this.head;

        for (let index = 1; index < position; index += 1) {
            previous = previous.next;
        }

        const node = new Node(value);

        // Save the old successor through the new node, then redirect
        // the predecessor to the inserted node.
        node.next = previous.next;
        previous.next = node;
        this.size += 1;
    }

    deleteFirst() {
        if (this.head === null) {
            throw new Error("Cannot delete the first node from an empty list.");
        }

        const removed = this.head;

        // Moving head forward removes the old head from the list.
        this.head = removed.next;
        removed.next = null;
        this.size -= 1;

        return removed.value;
    }

    deleteLast() {
        if (this.head === null) {
            throw new Error("Cannot delete the last node from an empty list.");
        }

        if (this.head.next === null) {
            return this.deleteFirst();
        }

        let previous = this.head;

        // Stop at the node immediately before the tail.
        while (previous.next !== null && previous.next.next !== null) {
            previous = previous.next;
        }

        const removed = previous.next;
        previous.next = null;
        this.size -= 1;

        return removed.value;
    }

    deleteByValue(value) {
        if (this.head === null) {
            return false;
        }

        if (Object.is(this.head.value, value)) {
            this.deleteFirst();
            return true;
        }

        let previous = this.head;

        while (previous.next !== null) {
            if (Object.is(previous.next.value, value)) {
                const removed = previous.next;

                // Bypass the matching node.
                previous.next = removed.next;
                removed.next = null;
                this.size -= 1;

                return true;
            }

            previous = previous.next;
        }

        return false;
    }

    deleteAtPosition(position) {
        this.validateDeletePosition(position);

        if (position === 0) {
            return this.deleteFirst();
        }

        let previous = this.head;

        for (let index = 1; index < position; index += 1) {
            previous = previous.next;
        }

        const removed = previous.next;
        previous.next = removed.next;
        removed.next = null;
        this.size -= 1;

        return removed.value;
    }

    findFirst(value) {
        let current = this.head;
        let position = 0;

        while (current !== null) {
            if (Object.is(current.value, value)) {
                return position;
            }

            current = current.next;
            position += 1;
        }

        return -1;
    }

    verifyIntegrity() {
        // Floyd's algorithm catches accidental cycles caused by incorrect
        // next-pointer updates.
        let slow = this.head;
        let fast = this.head;

        while (fast !== null && fast.next !== null) {
            slow = slow.next;
            fast = fast.next.next;

            if (slow === fast) {
                throw new Error("Integrity failure: cycle detected.");
            }
        }

        let counted = 0;
        let current = this.head;

        while (current !== null) {
            counted += 1;
            current = current.next;
        }

        if (counted !== this.size) {
            throw new Error(
                `Integrity failure: size says ${this.size}, traversal found ${counted}.`
            );
        }

        return true;
    }
}

function printState(label, list) {
    list.verifyIntegrity();
    console.log(`${label.padEnd(34)} ${list.toString()}  size=${list.size}`);
}

function basicDemo() {
    console.log("\n=== Basic insertion and deletion ===");

    const list = new SinglyLinkedList();
    printState("empty", list);

    list.insertAtBeginning("B");
    printState("insertAtBeginning('B')", list);

    list.insertAtBeginning("A");
    printState("insertAtBeginning('A')", list);

    list.insertAtEnd("D");
    printState("insertAtEnd('D')", list);

    list.insertAtPosition(2, "C");
    printState("insertAtPosition(2, 'C')", list);

    console.log("deleteFirst() ->", list.deleteFirst());
    printState("after deleteFirst", list);

    console.log("deleteLast() ->", list.deleteLast());
    printState("after deleteLast", list);

    console.log("deleteByValue('C') ->", list.deleteByValue("C"));
    printState("after deleteByValue('C')", list);

    list.insertAtEnd("E");
    list.insertAtEnd("F");
    console.log("deleteAtPosition(1) ->", list.deleteAtPosition(1));
    printState("after deleteAtPosition(1)", list);
}

function duplicateDemo() {
    console.log("\n=== Duplicate values ===");

    const list = new SinglyLinkedList(["review", "merge", "review", "deploy"]);
    printState("before duplicate deletion", list);

    console.log("First review position:", list.findFirst("review"));
    console.log("Removed:", list.deleteByValue("review"));

    printState("only first matching value removed", list);
}

function edgeCaseDemo() {
    console.log("\n=== Edge cases ===");

    const list = new SinglyLinkedList();

    try {
        list.deleteFirst();
    } catch (error) {
        console.log("Empty deleteFirst:", error.message);
    }

    try {
        list.deleteLast();
    } catch (error) {
        console.log("Empty deleteLast:", error.message);
    }

    try {
        list.insertAtPosition(-1, "invalid");
    } catch (error) {
        console.log("Negative insertion:", error.message);
    }

    try {
        list.insertAtPosition(1, "invalid");
    } catch (error) {
        console.log("Position beyond size:", error.message);
    }

    const populated = new SinglyLinkedList(["A"]);

    try {
        populated.deleteAtPosition(1);
    } catch (error) {
        console.log("Deletion at size:", error.message);
    }

    console.log(
        "Deleting a missing value:",
        populated.deleteByValue("Z")
    );
}

function eventDrivenDemo() {
    console.log("\n=== Event-driven workflow model ===");

    const queue = new SinglyLinkedList();

    // These events represent operations arriving from an application
    // layer.  The switch separates the event type from list mechanics.
    const events = [
        { type: "append", value: "PR-201" },
        { type: "append", value: "PR-202" },
        { type: "prepend", value: "HOTFIX-200" },
        { type: "insert", position: 2, value: "PR-201A" },
        { type: "deleteValue", value: "PR-202" },
        { type: "deletePosition", position: 1 }
    ];

    for (const event of events) {
        switch (event.type) {
            case "append":
                queue.insertAtEnd(event.value);
                break;
            case "prepend":
                queue.insertAtBeginning(event.value);
                break;
            case "insert":
                queue.insertAtPosition(event.position, event.value);
                break;
            case "deleteValue":
                queue.deleteByValue(event.value);
                break;
            case "deletePosition":
                queue.deleteAtPosition(event.position);
                break;
            default:
                throw new Error(`Unsupported event type: ${event.type}`);
        }

        printState(`processed ${event.type}`, queue);
    }
}

function complexityDemo() {
    console.log("\n=== Complexity ===");
    console.log("Beginning insertion: O(1)");
    console.log("End insertion:       O(n) without a tail pointer");
    console.log("Position insertion:  O(n) worst case");
    console.log("First deletion:      O(1)");
    console.log("Last deletion:       O(n)");
    console.log("Value deletion:      O(n)");
    console.log("Position deletion:   O(n)");
}

function main() {
    basicDemo();
    duplicateDemo();
    edgeCaseDemo();
    eventDrivenDemo();
    complexityDemo();
}

main();
