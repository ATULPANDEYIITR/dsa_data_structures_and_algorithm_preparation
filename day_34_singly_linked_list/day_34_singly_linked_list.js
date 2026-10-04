"use strict";

/*
 * Singly Linked Lists
 *
 * This file implements a singly linked list without using a built-in
 * linked-list collection. The focus is pointer-like object references,
 * head management, traversal, insertion, deletion, validation, and
 * event-driven mutation reporting.
 *
 * Run with:
 *   node singly_linked_list.js
 */

// -----------------------------------------------------------------------------
// Node
// -----------------------------------------------------------------------------

class Node {
    constructor(data) {
        this.data = data;
        this.next = null;
    }
}

// -----------------------------------------------------------------------------
// Singly Linked List
// -----------------------------------------------------------------------------

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

    traverse() {
        const values = [];
        let current = this.head;

        while (current !== null) {
            values.push(current.data);
            current = current.next;
        }

        return values;
    }

    display() {
        if (this.head === null) {
            return "HEAD -> null";
        }

        const values = ["HEAD"];
        let current = this.head;

        while (current !== null) {
            values.push(String(current.data));
            current = current.next;
        }

        values.push("null");
        return values.join(" -> ");
    }

    nodeAt(index) {
        this.validateIndex(index);

        let current = this.head;

        for (let position = 0; position < index; position += 1) {
            current = current.next;
        }

        return current;
    }

    validateIndex(index, allowEnd = false) {
        if (!Number.isInteger(index)) {
            throw new TypeError("index must be an integer");
        }

        const maximum = allowEnd ? this.size : this.size - 1;

        if (index < 0 || index > maximum) {
            throw new RangeError(
                `index ${index} is outside the valid range 0..${maximum}`
            );
        }
    }

    insertAtHead(value) {
        const newNode = new Node(value);

        // The new node inherits the old head before the list head changes.
        newNode.next = this.head;
        this.head = newNode;
        this.size += 1;

        return newNode;
    }

    insertAtEnd(value) {
        const newNode = new Node(value);

        if (this.head === null) {
            this.head = newNode;
            this.size += 1;
            return newNode;
        }

        let current = this.head;

        while (current.next !== null) {
            current = current.next;
        }

        current.next = newNode;
        this.size += 1;

        return newNode;
    }

    insertAt(index, value) {
        this.validateIndex(index, true);

        if (index === 0) {
            return this.insertAtHead(value);
        }

        const previous = this.nodeAt(index - 1);
        const newNode = new Node(value);

        // Preserve the suffix before attaching the new node.
        newNode.next = previous.next;
        previous.next = newNode;

        this.size += 1;
        return newNode;
    }

    insertAfter(target, value) {
        let current = this.head;

        while (current !== null) {
            if (Object.is(current.data, target)) {
                const newNode = new Node(value);
                newNode.next = current.next;
                current.next = newNode;
                this.size += 1;
                return newNode;
            }

            current = current.next;
        }

        throw new Error(`target ${String(target)} was not found`);
    }

    search(value) {
        let current = this.head;

        while (current !== null) {
            if (Object.is(current.data, value)) {
                return current;
            }

            current = current.next;
        }

        return null;
    }

    deleteHead() {
        if (this.head === null) {
            throw new Error("cannot delete the head of an empty list");
        }

        const removed = this.head;

        this.head = removed.next;

        // Disconnect the removed object from the remaining structure.
        removed.next = null;

        this.size -= 1;

        return removed.data;
    }

    deleteAt(index) {
        this.validateIndex(index);

        if (index === 0) {
            return this.deleteHead();
        }

        const previous = this.nodeAt(index - 1);
        const removed = previous.next;

        previous.next = removed.next;
        removed.next = null;

        this.size -= 1;

        return removed.data;
    }

    deleteFirst(value) {
        if (this.head === null) {
            throw new Error("cannot delete from an empty list");
        }

        if (Object.is(this.head.data, value)) {
            return this.deleteHead();
        }

        let previous = this.head;
        let current = this.head.next;

        while (current !== null) {
            if (Object.is(current.data, value)) {
                previous.next = current.next;
                current.next = null;
                this.size -= 1;
                return current.data;
            }

            previous = current;
            current = current.next;
        }

        throw new Error(`value ${String(value)} was not found`);
    }

    deleteAll(value) {
        let removedCount = 0;

        while (
            this.head !== null &&
            Object.is(this.head.data, value)
        ) {
            this.deleteHead();
            removedCount += 1;
        }

        if (this.head === null) {
            return removedCount;
        }

        let previous = this.head;
        let current = this.head.next;

        while (current !== null) {
            if (Object.is(current.data, value)) {
                previous.next = current.next;
                current.next = null;
                this.size -= 1;
                removedCount += 1;
                current = previous.next;
            } else {
                previous = current;
                current = current.next;
            }
        }

        return removedCount;
    }

    reverse() {
        let previous = null;
        let current = this.head;

        while (current !== null) {
            const nextNode = current.next;
            current.next = previous;
            previous = current;
            current = nextNode;
        }

        this.head = previous;
    }

    detectCycle() {
        let slow = this.head;
        let fast = this.head;

        // The fast reference moves two links at a time. If a cycle exists,
        // fast and slow eventually reference the same Node object.
        while (fast !== null && fast.next !== null) {
            slow = slow.next;
            fast = fast.next.next;

            if (slow === fast) {
                return true;
            }
        }

        return false;
    }

    clear() {
        let current = this.head;

        while (current !== null) {
            const nextNode = current.next;
            current.next = null;
            current = nextNode;
        }

        this.head = null;
        this.size = 0;
    }

    mapInPlace(transform) {
        if (typeof transform !== "function") {
            throw new TypeError("transform must be a function");
        }

        let current = this.head;

        while (current !== null) {
            current.data = transform(current.data);
            current = current.next;
        }
    }

    validateIntegrity() {
        if (this.detectCycle()) {
            throw new Error("list integrity failure: cycle detected");
        }

        let count = 0;
        let current = this.head;

        while (current !== null) {
            count += 1;
            current = current.next;
        }

        if (count !== this.size) {
            throw new Error(
                `list integrity failure: size=${this.size}, counted=${count}`
            );
        }
    }
}

// -----------------------------------------------------------------------------
// Event-driven wrapper
// -----------------------------------------------------------------------------

class ObservableLinkedList extends SinglyLinkedList {
    constructor(values = []) {
        super();
        this.listeners = new Set();

        for (const value of values) {
            this.insertAtEnd(value);
        }
    }

    onMutation(listener) {
        if (typeof listener !== "function") {
            throw new TypeError("mutation listener must be a function");
        }

        this.listeners.add(listener);

        return () => this.listeners.delete(listener);
    }

    emitMutation(operation, details) {
        const event = {
            operation,
            details,
            size: this.size,
            snapshot: this.traverse()
        };

        for (const listener of this.listeners) {
            listener(event);
        }
    }

    insertAtHead(value) {
        const result = super.insertAtHead(value);
        this.emitMutation("insertAtHead", { value });
        return result;
    }

    insertAtEnd(value) {
        const result = super.insertAtEnd(value);
        this.emitMutation("insertAtEnd", { value });
        return result;
    }

    deleteHead() {
        const value = super.deleteHead();
        this.emitMutation("deleteHead", { value });
        return value;
    }

    deleteAt(index) {
        const value = super.deleteAt(index);
        this.emitMutation("deleteAt", { index, value });
        return value;
    }
}

// -----------------------------------------------------------------------------
// Demonstrations
// -----------------------------------------------------------------------------

function demonstrateNodeAndHead() {
    console.log("\n=== Node and Head ===");

    const first = new Node("first");
    const second = new Node("second");
    const third = new Node("third");

    first.next = second;
    second.next = third;

    let head = first;

    while (head !== null) {
        console.log({
            data: head.data,
            next: head.next ? head.next.data : null
        });

        head = head.next;
    }
}

function demonstrateTraversal() {
    console.log("\n=== Traversal ===");

    const list = new SinglyLinkedList([
        "feature/search",
        "feature/auth",
        "release"
    ]);

    console.log(list.display());
    console.log("Values:", list.traverse());
    console.log("Contains release:", list.search("release") !== null);
    console.log("Contains hotfix:", list.search("hotfix") !== null);
}

function demonstrateInsertion() {
    console.log("\n=== Insertion ===");

    const list = new SinglyLinkedList();

    list.insertAtHead("review");
    list.insertAtHead("changes");
    list.insertAtEnd("merge");
    list.insertAt(1, "approval");
    list.insertAfter("approval", "status-check");

    console.log(list.display());
    console.log("Size:", list.size);

    list.validateIntegrity();
}

function demonstrateDeletion() {
    console.log("\n=== Deletion ===");

    const list = new SinglyLinkedList([
        "pull-request",
        "review",
        "approval",
        "approval",
        "merge"
    ]);

    console.log("Before:", list.display());

    console.log("Deleted head:", list.deleteHead());
    console.log("Deleted index 1:", list.deleteAt(1));
    console.log("Deleted first approval:", list.deleteFirst("approval"));
    console.log("Deleted remaining approvals:", list.deleteAll("approval"));

    console.log("After:", list.display());
    list.validateIntegrity();
}

function demonstrateReverseAndCycleDetection() {
    console.log("\n=== Reverse and Cycle Detection ===");

    const list = new SinglyLinkedList(["A", "B", "C", "D"]);

    console.log("Before:", list.display());

    list.reverse();

    console.log("After:", list.display());
    console.log("Cycle:", list.detectCycle());

    const tail = list.nodeAt(list.size - 1);
    tail.next = list.head;

    console.log("Cycle after deliberate corruption:", list.detectCycle());

    tail.next = null;
    list.validateIntegrity();
}

function demonstrateObservableBehavior() {
    console.log("\n=== Event-driven Mutation ===");

    const list = new ObservableLinkedList();

    const unsubscribe = list.onMutation((event) => {
        console.log(
            `[event=${event.operation}] size=${event.size}`,
            event.snapshot
        );
    });

    list.insertAtHead("node-a");
    list.insertAtEnd("node-b");
    list.deleteHead();

    unsubscribe();

    list.insertAtEnd("node-c");

    console.log("Final:", list.display());
}

function demonstrateFailures() {
    console.log("\n=== Failure Conditions ===");

    const list = new SinglyLinkedList(["alpha", "beta"]);

    const failures = [
        () => list.nodeAt(5),
        () => list.insertAt(7, "gamma"),
        () => list.deleteAt(-1),
        () => list.deleteFirst("missing"),
        () => list.insertAfter("missing", "x"),
    ];

    for (const operation of failures) {
        try {
            operation();
        } catch (error) {
            console.log(`Rejected safely: ${error.message}`);
        }
    }

    const empty = new SinglyLinkedList();

    try {
        empty.deleteHead();
    } catch (error) {
        console.log(`Empty-list deletion rejected: ${error.message}`);
    }
}

function demonstrateRealisticPipeline() {
    console.log("\n=== Ordered Processing Pipeline ===");

    const pipeline = new SinglyLinkedList([
        "validate-request",
        "run-tests",
        "collect-review",
        "merge"
    ]);

    console.log("Pipeline:", pipeline.display());

    while (!pipeline.isEmpty()) {
        const completed = pipeline.deleteHead();
        console.log(`Completed: ${completed}`);
    }

    console.log("Pipeline after processing:", pipeline.display());
}

function demonstrateEdgeCases() {
    console.log("\n=== Edge Cases ===");

    const examples = [
        [],
        [42],
        [42, 42, 42],
        [null, false, 0, ""]
    ];

    for (const values of examples) {
        const list = new SinglyLinkedList(values);
        list.validateIntegrity();

        console.log({
            input: values,
            output: list.traverse(),
            size: list.size,
            empty: list.isEmpty()
        });
    }
}

function main() {
    demonstrateNodeAndHead();
    demonstrateTraversal();
    demonstrateInsertion();
    demonstrateDeletion();
    demonstrateReverseAndCycleDetection();
    demonstrateObservableBehavior();
    demonstrateFailures();
    demonstrateRealisticPipeline();
    demonstrateEdgeCases();

    console.log("\nAll JavaScript demonstrations completed successfully.");
}

main();
