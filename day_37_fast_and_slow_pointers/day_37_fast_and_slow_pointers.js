"use strict";

/*
 * Fast and Slow Pointers
 *
 * This file demonstrates:
 * - one-step/two-step pointer movement
 * - middle-node detection
 * - Floyd cycle detection
 * - cycle-entry detection
 * - cycle length
 * - identity versus equal values
 * - an event-driven trace of Floyd's algorithm
 * - practical linked-list applications
 *
 * No external packages are required.
 */

class ListNode {
    constructor(value) {
        this.value = value;
        this.next = null;
    }
}

function buildLinkedList(values) {
    const items = Array.from(values);

    if (items.length === 0) {
        return null;
    }

    const head = new ListNode(items[0]);
    let tail = head;

    for (let index = 1; index < items.length; index += 1) {
        tail.next = new ListNode(items[index]);
        tail = tail.next;
    }

    return head;
}

function listPreview(head, limit = 20) {
    const values = [];
    let current = head;

    for (let count = 0; count < limit; count += 1) {
        if (current === null) {
            return values.length === 0 ? "empty" : values.join(" -> ");
        }

        values.push(String(current.value));
        current = current.next;
    }

    values.push("...");
    return values.join(" -> ");
}

function findMiddleNode(head) {
    /*
     * When fast reaches the end, slow has advanced approximately half as far.
     * With an even number of nodes, this version returns the second middle.
     */
    let slow = head;
    let fast = head;

    while (fast !== null && fast.next !== null) {
        slow = slow.next;
        fast = fast.next.next;
    }

    return slow;
}

function findFirstMiddleNode(head) {
    if (head === null) {
        return null;
    }

    let slow = head;
    let fast = head;

    /*
     * Looking two nodes ahead lets us stop on the first middle for
     * even-length lists.
     */
    while (fast.next !== null && fast.next.next !== null) {
        slow = slow.next;
        fast = fast.next.next;
    }

    return slow;
}

function hasCycle(head) {
    let slow = head;
    let fast = head;

    while (fast !== null && fast.next !== null) {
        slow = slow.next;
        fast = fast.next.next;

        if (slow === fast) {
            return true;
        }
    }

    return false;
}

function findCycleEntry(head) {
    let slow = head;
    let fast = head;

    /*
     * Phase one: find any meeting point inside the cycle.
     */
    while (fast !== null && fast.next !== null) {
        slow = slow.next;
        fast = fast.next.next;

        if (slow === fast) {
            /*
             * Phase two: one pointer returns to the head. Moving both
             * pointers at one node per step makes them meet at the cycle
             * entry.
             */
            slow = head;

            while (slow !== fast) {
                slow = slow.next;
                fast = fast.next;
            }

            return slow;
        }
    }

    return null;
}

function getCycleLength(head) {
    const entry = findCycleEntry(head);

    if (entry === null) {
        return 0;
    }

    let current = entry.next;
    let length = 1;

    while (current !== entry) {
        current = current.next;
        length += 1;
    }

    return length;
}

function getDistanceToCycleEntry(head) {
    const entry = findCycleEntry(head);

    if (entry === null) {
        return null;
    }

    let current = head;
    let distance = 0;

    while (current !== entry) {
        current = current.next;
        distance += 1;
    }

    return distance;
}

function makeCycle(head, entryIndex) {
    if (head === null || entryIndex < 0) {
        throw new Error("A non-empty list and a non-negative entry index are required.");
    }

    let entry = head;
    let tail = head;

    for (let index = 0; index < entryIndex; index += 1) {
        if (entry.next === null) {
            throw new Error("Cycle entry index is outside the list.");
        }

        entry = entry.next;
    }

    while (tail.next !== null) {
        tail = tail.next;
    }

    tail.next = entry;
    return entry;
}

function traceFloyd(head, onStep) {
    let slow = head;
    let fast = head;
    let step = 0;

    while (fast !== null && fast.next !== null) {
        step += 1;
        slow = slow.next;
        fast = fast.next.next;

        onStep({
            step,
            slowValue: slow.value,
            fastValue: fast === null ? null : fast.value,
            meeting: slow === fast
        });

        if (slow === fast) {
            return {
                detected: true,
                meetingNode: slow,
                steps: step
            };
        }
    }

    return {
        detected: false,
        meetingNode: null,
        steps: step
    };
}

function demonstrateMiddleDetection() {
    console.log("\n=== Middle-Node Detection ===");

    const examples = [
        [],
        [10],
        [10, 20],
        [10, 20, 30],
        [10, 20, 30, 40],
        [10, 20, 30, 40, 50],
        [10, 20, 30, 40, 50, 60]
    ];

    for (const values of examples) {
        const head = buildLinkedList(values);
        const first = findFirstMiddleNode(head);
        const second = findMiddleNode(head);

        console.log(
            JSON.stringify(values),
            `first=${first ? first.value : null}`,
            `second=${second ? second.value : null}`
        );
    }
}

function demonstrateCycleDetection() {
    console.log("\n=== Floyd Cycle Detection ===");

    const acyclic = buildLinkedList([1, 2, 3, 4, 5]);

    console.log(
        "Acyclic list:",
        listPreview(acyclic),
        "cycle=",
        hasCycle(acyclic)
    );

    const cyclic = buildLinkedList([10, 20, 30, 40, 50, 60]);
    const entry = makeCycle(cyclic, 2);

    console.log("Cyclic preview:", listPreview(cyclic, 10));
    console.log("Cycle detected:", hasCycle(cyclic));
    console.log("Cycle entry:", findCycleEntry(cyclic).value);
    console.log("Cycle length:", getCycleLength(cyclic));
    console.log("Distance to entry:", getDistanceToCycleEntry(cyclic));
    console.log("Expected entry:", entry.value);
}

function demonstrateEventDrivenTrace() {
    console.log("\n=== Event-Driven Floyd Trace ===");

    const head = buildLinkedList(["A", "B", "C", "D", "E", "F"]);
    makeCycle(head, 2);

    const result = traceFloyd(head, event => {
        console.log(
            `step=${event.step}`,
            `slow=${event.slowValue}`,
            `fast=${event.fastValue}`,
            `meeting=${event.meeting}`
        );
    });

    console.log(
        `Detection result: detected=${result.detected}, ` +
        `steps=${result.steps}, ` +
        `meeting=${result.meetingNode.value}`
    );
}

function demonstrateIdentity() {
    console.log("\n=== Node Identity ===");

    const first = new ListNode(42);
    const second = new ListNode(42);

    first.next = second;

    console.log("Same value:", first.value === second.value);
    console.log("Same object:", first === second);

    /*
     * Floyd compares object identity. Comparing only values would be wrong
     * when separate nodes happen to contain the same value.
     */
    second.next = first;

    console.log("Self-contained two-node cycle:", hasCycle(first));
    console.log("Cycle entry value:", findCycleEntry(first).value);
}

function reverseList(head) {
    let previous = null;
    let current = head;

    while (current !== null) {
        const next = current.next;
        current.next = previous;
        previous = current;
        current = next;
    }

    return previous;
}

function isPalindrome(head) {
    if (head === null || head.next === null) {
        return true;
    }

    let slow = head;
    let fast = head;

    while (fast.next !== null && fast.next.next !== null) {
        slow = slow.next;
        fast = fast.next.next;
    }

    const secondHalf = reverseList(slow.next);
    slow.next = secondHalf;

    let left = head;
    let right = secondHalf;
    let result = true;

    while (right !== null) {
        if (left.value !== right.value) {
            result = false;
            break;
        }

        left = left.next;
        right = right.next;
    }

    // Restore the original structure after inspection.
    slow.next = reverseList(secondHalf);

    return result;
}

function demonstratePalindromeApplication() {
    console.log("\n=== Palindrome Application ===");

    for (const values of [
        [1, 2, 3, 2, 1],
        [1, 2, 2, 1],
        [1, 2, 3],
        [7],
        []
    ]) {
        const head = buildLinkedList(values);

        console.log(
            JSON.stringify(values),
            "palindrome=",
            isPalindrome(head)
        );
    }
}

function demonstrateErrorHandling() {
    console.log("\n=== Validation and Failure Handling ===");

    try {
        makeCycle(null, 0);
    } catch (error) {
        console.log("Rejected invalid cycle creation:", error.message);
    }

    try {
        makeCycle(buildLinkedList([1, 2]), 5);
    } catch (error) {
        console.log("Rejected invalid entry index:", error.message);
    }

    const selfCycle = new ListNode(99);
    selfCycle.next = selfCycle;

    console.log("Self-cycle detected:", hasCycle(selfCycle));
    console.log("Self-cycle entry:", findCycleEntry(selfCycle).value);
    console.log("Self-cycle length:", getCycleLength(selfCycle));
}

function demonstrateComplexity() {
    console.log("\n=== Complexity ===");
    console.log("Middle-node detection: O(n) time, O(1) auxiliary space.");
    console.log("Cycle detection: O(n) time, O(1) auxiliary space.");
    console.log("Cycle-entry detection: O(n) time, O(1) auxiliary space.");
    console.log(
        "A Set-based detector can be easier to write, but it requires O(n) " +
        "additional memory because every visited node is stored."
    );
}

function runAssertions() {
    console.log("\n=== Self Checks ===");

    console.assert(findMiddleNode(null) === null);
    console.assert(findMiddleNode(buildLinkedList([1])).value === 1);
    console.assert(findMiddleNode(buildLinkedList([1, 2])).value === 2);
    console.assert(findMiddleNode(buildLinkedList([1, 2, 3])).value === 2);
    console.assert(findMiddleNode(buildLinkedList([1, 2, 3, 4])).value === 3);

    const normal = buildLinkedList([1, 2, 3]);
    console.assert(hasCycle(normal) === false);

    const cycle = buildLinkedList([1, 2, 3, 4, 5]);
    const entry = makeCycle(cycle, 2);

    console.assert(hasCycle(cycle) === true);
    console.assert(findCycleEntry(cycle) === entry);
    console.assert(getCycleLength(cycle) === 3);
    console.assert(getDistanceToCycleEntry(cycle) === 2);

    console.log("All assertions passed.");
}

function main() {
    console.log("FAST AND SLOW POINTERS");
    console.log("======================");
    console.log(
        "JavaScript demonstrations use object identity for pointer comparisons."
    );

    demonstrateMiddleDetection();
    demonstrateCycleDetection();
    demonstrateEventDrivenTrace();
    demonstrateIdentity();
    demonstratePalindromeApplication();
    demonstrateErrorHandling();
    demonstrateComplexity();
    runAssertions();
}

main();
