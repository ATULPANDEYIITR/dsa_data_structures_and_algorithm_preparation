"use strict";

/*
 * Linked-list assessment using Node.js-compatible JavaScript.
 *
 * Easy: reverse list, cycle detection, merge two sorted lists.
 * Medium: remove Nth from end, intersection, palindrome, reorder.
 * Difficult: merge K sorted lists with a binary min-heap.
 */

class ListNode {
    constructor(value, next = null) {
        if (!Number.isSafeInteger(value)) {
            throw new TypeError("Node values must be safe integers.");
        }
        this.value = value;
        this.next = next;
    }
}

function fromArray(values) {
    const dummy = new ListNode(0);
    let tail = dummy;
    for (const value of values) {
        tail.next = new ListNode(value);
        tail = tail.next;
    }
    return dummy.next;
}

function toArray(head) {
    const result = [];
    const visited = new Set();
    let current = head;

    while (current !== null) {
        if (visited.has(current)) {
            throw new Error("Cannot convert a cyclic list to an array.");
        }
        visited.add(current);
        result.push(current.value);
        current = current.next;
    }
    return result;
}

function hasCycle(head) {
    let slow = head;
    let fast = head;

    while (fast !== null && fast.next !== null) {
        slow = slow.next;
        fast = fast.next.next;
        if (slow === fast) return true;
    }
    return false;
}

function assertAcyclic(head) {
    if (hasCycle(head)) {
        throw new Error("The operation requires an acyclic list.");
    }
}

function assertDisjoint(headA, headB) {
    const nodes = new Set();
    for (let node = headA; node !== null; node = node.next) {
        nodes.add(node);
    }
    for (let node = headB; node !== null; node = node.next) {
        if (nodes.has(node)) {
            throw new Error("Input lists must not share nodes.");
        }
    }
}

function reverseList(head) {
    assertAcyclic(head);
    let previous = null;
    let current = head;

    while (current !== null) {
        const following = current.next;
        current.next = previous;
        previous = current;
        current = following;
    }
    return previous;
}

function mergeTwoSorted(first, second) {
    assertAcyclic(first);
    assertAcyclic(second);
    assertDisjoint(first, second);

    const dummy = new ListNode(0);
    let tail = dummy;

    while (first !== null && second !== null) {
        if (first.value <= second.value) {
            tail.next = first;
            first = first.next;
        } else {
            tail.next = second;
            second = second.next;
        }
        tail = tail.next;
    }

    tail.next = first ?? second;
    return dummy.next;
}

function removeNthFromEnd(head, n) {
    if (!Number.isSafeInteger(n) || n <= 0) {
        throw new RangeError("n must be a positive integer.");
    }
    assertAcyclic(head);

    const dummy = new ListNode(0, head);
    let fast = dummy;
    let slow = dummy;

    for (let index = 0; index < n; index++) {
        fast = fast.next;
        if (fast === null) {
            throw new RangeError("n exceeds the list length.");
        }
    }

    while (fast.next !== null) {
        fast = fast.next;
        slow = slow.next;
    }

    const removed = slow.next;
    slow.next = removed.next;
    removed.next = null;
    return dummy.next;
}

function intersectionNode(headA, headB) {
    assertAcyclic(headA);
    assertAcyclic(headB);

    let a = headA;
    let b = headB;

    // Switching heads equalizes the total distance traveled by both pointers.
    while (a !== b) {
        a = a === null ? headB : a.next;
        b = b === null ? headA : b.next;
    }
    return a;
}

function isPalindrome(head) {
    assertAcyclic(head);
    if (head === null || head.next === null) return true;

    let slow = head;
    let fast = head;

    while (fast.next !== null && fast.next.next !== null) {
        slow = slow.next;
        fast = fast.next.next;
    }

    const reversed = reverseList(slow.next);
    slow.next = reversed;

    let left = head;
    let right = reversed;
    let matches = true;

    try {
        while (right !== null) {
            if (left.value !== right.value) {
                matches = false;
                break;
            }
            left = left.next;
            right = right.next;
        }
    } finally {
        // Restore the input structure even if comparison logic later changes.
        slow.next = reverseList(reversed);
    }

    return matches;
}

function reorderList(head) {
    assertAcyclic(head);
    if (head === null || head.next === null) return head;

    let slow = head;
    let fast = head;
    while (fast.next !== null && fast.next.next !== null) {
        slow = slow.next;
        fast = fast.next.next;
    }

    let second = slow.next;
    slow.next = null;
    second = reverseList(second);

    let first = head;
    while (second !== null) {
        const firstNext = first.next;
        const secondNext = second.next;
        first.next = second;
        second.next = firstNext;
        first = firstNext;
        second = secondNext;
    }
    return head;
}

class MinHeap {
    constructor() {
        this.items = [];
    }

    push(item) {
        this.items.push(item);
        let index = this.items.length - 1;

        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);
            if (this.items[parent].node.value <= item.node.value) break;
            this.items[index] = this.items[parent];
            index = parent;
        }
        this.items[index] = item;
    }

    pop() {
        if (this.items.length === 0) return null;

        const minimum = this.items[0];
        const last = this.items.pop();

        if (this.items.length > 0) {
            let index = 0;

            while (true) {
                const left = index * 2 + 1;
                const right = left + 1;
                if (left >= this.items.length) break;

                let child = left;
                if (
                    right < this.items.length &&
                    this.items[right].node.value < this.items[left].node.value
                ) {
                    child = right;
                }

                if (this.items[child].node.value >= last.node.value) break;
                this.items[index] = this.items[child];
                index = child;
            }
            this.items[index] = last;
        }

        return minimum;
    }

    get size() {
        return this.items.length;
    }
}

function mergeKSorted(heads) {
    for (const head of heads) assertAcyclic(head);

    const seen = new Set();
    for (const head of heads) {
        for (let node = head; node !== null; node = node.next) {
            if (seen.has(node)) {
                throw new Error("Input lists must not share nodes.");
            }
            seen.add(node);
        }
    }

    const heap = new MinHeap();
    for (const head of heads) {
        if (head !== null) heap.push({ node: head });
    }

    const dummy = new ListNode(0);
    let tail = dummy;

    while (heap.size > 0) {
        const node = heap.pop().node;
        const following = node.next;
        tail.next = node;
        tail = node;

        if (following !== null) heap.push({ node: following });
    }

    tail.next = null;
    return dummy.next;
}

function runTests() {
    const assert = require("node:assert/strict");

    assert.deepEqual(toArray(reverseList(fromArray([1, 2, 3]))), [3, 2, 1]);
    assert.equal(hasCycle(fromArray([1, 2, 3])), false);

    const cyclic = fromArray([1, 2, 3]);
    cyclic.next.next.next = cyclic.next;
    assert.equal(hasCycle(cyclic), true);
    assert.throws(() => reverseList(cyclic), /acyclic/);

    assert.deepEqual(
        toArray(mergeTwoSorted(fromArray([1, 3, 5]), fromArray([2, 4, 6]))),
        [1, 2, 3, 4, 5, 6]
    );

    assert.deepEqual(
        toArray(removeNthFromEnd(fromArray([1, 2, 3, 4, 5]), 2)),
        [1, 2, 3, 5]
    );
    assert.throws(() => removeNthFromEnd(fromArray([1]), 2), RangeError);

    const shared = fromArray([8, 9]);
    assert.equal(
        intersectionNode(new ListNode(1, shared), new ListNode(2, shared)),
        shared
    );
    assert.equal(intersectionNode(fromArray([1]), fromArray([1])), null);

    const palindrome = fromArray([1, 2, 3, 2, 1]);
    assert.equal(isPalindrome(palindrome), true);
    assert.deepEqual(toArray(palindrome), [1, 2, 3, 2, 1]);
    assert.equal(isPalindrome(fromArray([1, 2, 3])), false);

    assert.deepEqual(toArray(reorderList(fromArray([1, 2, 3, 4, 5]))),
        [1, 5, 2, 4, 3]);

    assert.deepEqual(
        toArray(mergeKSorted([
            fromArray([1, 4, 7]),
            fromArray([2, 5, 8]),
            fromArray([3, 6, 9]),
            null
        ])),
        [1, 2, 3, 4, 5, 6, 7, 8, 9]
    );

    assert.deepEqual(toArray(mergeKSorted([])), []);
    assert.throws(
        () => mergeTwoSorted(shared, new ListNode(7, shared)),
        /share nodes/
    );

    console.log("All linked-list assessment tests passed.");
}

function main() {
    console.log("Reversed:", toArray(reverseList(fromArray([1, 2, 3, 4]))));
    console.log(
        "Merged K:",
        toArray(mergeKSorted([
            fromArray([1, 4, 7]),
            fromArray([2, 5, 8]),
            fromArray([3, 6, 9])
        ]))
    );
    runTests();
}

if (require.main === module) main();

module.exports = {
    ListNode,
    fromArray,
    toArray,
    hasCycle,
    reverseList,
    mergeTwoSorted,
    removeNthFromEnd,
    intersectionNode,
    isPalindrome,
    reorderList,
    mergeKSorted
};
