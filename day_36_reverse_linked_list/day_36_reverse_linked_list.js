"use strict";

/*
 * Singly linked-list reversal using iterative and recursive techniques.
 *
 * The two approaches mutate the existing next pointers rather than creating
 * a second linked list. The iterative version uses constant auxiliary space.
 * The recursive version uses the JavaScript call stack and therefore has a
 * practical depth limitation.
 */

class ListNode {
    constructor(value) {
        this.value = value;
        this.next = null;
    }
}

class LinkedList {
    constructor(values = []) {
        this.head = null;
        this.tail = null;
        this.size = 0;

        for (const value of values) {
            this.append(value);
        }
    }

    append(value) {
        const node = new ListNode(value);

        if (this.head === null) {
            this.head = node;
            this.tail = node;
        } else {
            this.tail.next = node;
            this.tail = node;
        }

        this.size += 1;
    }

    toArray() {
        const result = [];
        const visited = new Set();
        let current = this.head;

        while (current !== null) {
            if (visited.has(current)) {
                throw new Error("Cycle detected while traversing linked list.");
            }

            visited.add(current);
            result.push(current.value);
            current = current.next;
        }

        return result;
    }

    toString() {
        return this.head === null ? "EMPTY" : this.toArray().join(" -> ");
    }

    /*
     * The loop preserves the unreversed suffix in nextNode before changing
     * current.next. Without saving nextNode first, the remainder of the list
     * would become unreachable.
     */
    reverseIterative() {
        let previous = null;
        let current = this.head;
        const oldHead = this.head;

        while (current !== null) {
            const nextNode = current.next;
            current.next = previous;
            previous = current;
            current = nextNode;
        }

        this.head = previous;
        this.tail = oldHead;
    }

    /*
     * Recursion reaches the final node first. While the stack unwinds,
     * current.next.next = current makes the successor point back to current.
     * Setting current.next to null prevents the old forward link from
     * producing a cycle.
     */
    reverseRecursive() {
        const oldHead = this.head;

        const reverse = (node) => {
            if (node === null || node.next === null) {
                return node;
            }

            const newHead = reverse(node.next);
            node.next.next = node;
            node.next = null;

            return newHead;
        };

        this.head = reverse(this.head);
        this.tail = oldHead;
    }

    /*
     * JavaScript does not provide a portable standard API for safely asking
     * how many recursive calls are available. A large-list guard prevents
     * accidentally treating recursive reversal as the scalable implementation.
     */
    reverseRecursiveWithGuard(maxNodes = 10000) {
        if (this.size > maxNodes) {
            throw new RangeError(
                `Recursive reversal rejected for ${this.size} nodes; ` +
                `the configured safety limit is ${maxNodes}.`
            );
        }

        this.reverseRecursive();
    }
}

function demonstrateBothAlgorithms() {
    console.log("SINGLY LINKED LIST REVERSAL");
    console.log("============================");

    const values = [10, 20, 30, 40, 50];

    const iterative = new LinkedList(values);
    console.log("Original:          ", iterative.toString());
    iterative.reverseIterative();
    console.log("Iterative result:  ", iterative.toString());

    const recursive = new LinkedList(values);
    recursive.reverseRecursive();
    console.log("Recursive result:  ", recursive.toString());

    console.log();
}

function demonstrateEdgeCases() {
    console.log("EDGE CASES");
    console.log("----------");

    for (const values of [[], [42], [1, 2]]) {
        const iterative = new LinkedList(values);
        const recursive = new LinkedList(values);

        iterative.reverseIterative();
        recursive.reverseRecursive();

        console.log(
            `Input: ${JSON.stringify(values)} | ` +
            `iterative: ${iterative.toString()} | ` +
            `recursive: ${recursive.toString()}`
        );
    }

    console.log();
}

function demonstratePointerMechanism() {
    console.log("ITERATIVE POINTER STATE");
    console.log("=======================");

    const list = new LinkedList([1, 2, 3, 4]);

    let previous = null;
    let current = list.head;

    while (current !== null) {
        const nextNode = current.next;

        console.log({
            current: current.value,
            previous: previous === null ? null : previous.value,
            nextNode: nextNode === null ? null : nextNode.value
        });

        current.next = previous;
        previous = current;
        current = nextNode;
    }

    list.head = previous;
    list.tail = list.head;

    while (list.tail !== null && list.tail.next !== null) {
        list.tail = list.tail.next;
    }

    console.log("Reversed:", list.toString());
    console.log();
}

function demonstrateRecursiveMechanism() {
    console.log("RECURSIVE UNWINDING");
    console.log("===================");

    const list = new LinkedList([10, 20, 30]);

    console.log("Before:", list.toString());
    list.reverseRecursive();
    console.log("After: ", list.toString());
    console.log(
        "During stack unwinding, each successor is linked back to its "
        + "predecessor and the predecessor's old next pointer is cleared."
    );
    console.log();
}

function verifyInvariants() {
    const original = [5, 10, 15, 20, 25];
    const list = new LinkedList(original);

    list.reverseIterative();

    const reversed = [...original].reverse();
    const iterativeResult = list.toArray();

    if (JSON.stringify(iterativeResult) !== JSON.stringify(reversed)) {
        throw new Error("Iterative reversal invariant failed.");
    }

    if (list.size !== original.length || list.tail.next !== null) {
        throw new Error("List metadata invariant failed.");
    }

    list.reverseRecursive();

    if (JSON.stringify(list.toArray()) !== JSON.stringify(original)) {
        throw new Error("Recursive reversal invariant failed.");
    }

    console.log("All reversal invariants passed.");
    console.log();
}

function demonstrateLargeListPolicy() {
    console.log("LARGE-LIST POLICY");
    console.log("==================");

    const values = Array.from({ length: 20000 }, (_, index) => index);
    const list = new LinkedList(values);

    list.reverseIterative();

    console.log(`Iteratively reversed ${list.size} nodes.`);
    console.log(`New head: ${list.head.value}`);
    console.log(`New tail: ${list.tail.value}`);

    const recursiveList = new LinkedList(values);

    try {
        recursiveList.reverseRecursiveWithGuard(10000);
    } catch (error) {
        console.log(`Recursive guard: ${error.message}`);
    }

    console.log();
}

function explainComplexity() {
    console.log("COMPLEXITY");
    console.log("----------");
    console.log("Iterative: O(n) time and O(1) auxiliary space.");
    console.log("Recursive:  O(n) time and O(n) call-stack space.");
    console.log(
        "Both algorithms mutate the original links and therefore do not "
        + "need a second linked list."
    );
}

function main() {
    demonstrateBothAlgorithms();
    demonstrateEdgeCases();
    demonstratePointerMechanism();
    demonstrateRecursiveMechanism();
    verifyInvariants();
    demonstrateLargeListPolicy();
    explainComplexity();
}

main();
