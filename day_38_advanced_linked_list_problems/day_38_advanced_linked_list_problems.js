'use strict';

/*
 * Advanced linked-list problems implemented with JavaScript-specific
 * features such as classes, Sets, generators, iterators, and event-driven
 * workflow reporting.
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

        return node;
    }

    *values(limit = 100) {
        let current = this.head;
        const seen = new Set();
        let count = 0;

        while (current !== null && count < limit) {
            if (seen.has(current)) {
                yield `${current.value} (cycle)`;
                return;
            }

            seen.add(current);
            yield current.value;
            current = current.next;
            count++;
        }
    }

    toArray(limit = 100) {
        return [...this.values(limit)];
    }

    toString(limit = 100) {
        return this.toArray(limit).join(' -> ');
    }
}

function mergeSorted(first, second) {
    const dummy = new ListNode(0);
    let tail = dummy;
    let left = first;
    let right = second;

    while (left && right) {
        if (left.value <= right.value) {
            tail.next = left;
            left = left.next;
        } else {
            tail.next = right;
            right = right.next;
        }
        tail = tail.next;
    }

    tail.next = left || right;
    return dummy.next;
}

function removeSortedDuplicates(head) {
    let current = head;

    while (current && current.next) {
        if (current.value === current.next.value) {
            current.next = current.next.next;
        } else {
            current = current.next;
        }
    }

    return head;
}

function removeNthFromEnd(head, n) {
    if (!Number.isInteger(n) || n <= 0) {
        throw new RangeError('n must be a positive integer');
    }

    const dummy = new ListNode(0);
    dummy.next = head;

    let fast = dummy;

    for (let i = 0; i < n; i++) {
        fast = fast.next;
        if (!fast) {
            throw new RangeError('n exceeds the list length');
        }
    }

    let slow = dummy;

    while (fast.next) {
        fast = fast.next;
        slow = slow.next;
    }

    slow.next = slow.next.next;
    return dummy.next;
}

function findIntersection(first, second) {
    /*
     * The comparison is object identity. Equal values do not imply
     * intersection because intersection means sharing the same node.
     */
    let a = first;
    let b = second;

    while (a !== b) {
        a = a ? a.next : second;
        b = b ? b.next : first;
    }

    return a;
}

function detectCycle(head) {
    let slow = head;
    let fast = head;

    while (fast && fast.next) {
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

    while (fast && fast.next) {
        slow = slow.next;
        fast = fast.next.next;

        if (slow === fast) {
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

function reverse(head) {
    let previous = null;
    let current = head;

    while (current) {
        const following = current.next;
        current.next = previous;
        previous = current;
        current = following;
    }

    return previous;
}

function isPalindrome(head) {
    if (!head || !head.next) {
        return true;
    }

    let slow = head;
    let fast = head;

    while (fast.next && fast.next.next) {
        slow = slow.next;
        fast = fast.next.next;
    }

    const secondHalf = reverse(slow.next);
    slow.next = secondHalf;

    let left = head;
    let right = secondHalf;
    let result = true;

    while (right) {
        if (left.value !== right.value) {
            result = false;
            break;
        }
        left = left.next;
        right = right.next;
    }

    slow.next = reverse(secondHalf);
    return result;
}

function josephusCircular(size, step) {
    if (!Number.isInteger(size) || size <= 0 || !Number.isInteger(step) || step <= 0) {
        throw new RangeError('size and step must be positive integers');
    }

    let survivor = 0;

    for (let currentSize = 2; currentSize <= size; currentSize++) {
        survivor = (survivor + step) % currentSize;
    }

    return survivor;
}

class WorkflowEmitter {
    constructor() {
        this.listeners = new Map();
    }

    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, new Set());
        }

        this.listeners.get(event).add(callback);

        return () => this.listeners.get(event)?.delete(callback);
    }

    emit(event, payload) {
        for (const callback of this.listeners.get(event) ?? []) {
            callback(payload);
        }
    }
}

/*
 * This event-driven demonstration uses linked-list operations as a
 * processing pipeline. Each successful operation emits a domain event.
 */
function demonstrateEventDrivenProcessing() {
    const emitter = new WorkflowEmitter();

    emitter.on('merged', ({ values }) => {
        console.log(`Merged event: ${values.join(', ')}`);
    });

    emitter.on('palindromeChecked', ({ result }) => {
        console.log(`Palindrome event: ${result}`);
    });

    const left = new LinkedList([1, 4, 7]);
    const right = new LinkedList([2, 3, 8]);

    const merged = mergeSorted(left.head, right.head);
    emitter.emit('merged', { values: [...new LinkedListFromHead(merged).values()] });

    const palindrome = new LinkedList([1, 2, 3, 2, 1]);
    emitter.emit('palindromeChecked', {
        result: isPalindrome(palindrome.head)
    });
}

class LinkedListFromHead extends LinkedList {
    constructor(head) {
        super();
        this.head = head;

        let current = head;
        while (current && current.next) {
            current = current.next;
        }
        this.tail = current;
    }
}

function buildIntersectionExample() {
    const shared = new ListNode(90);
    shared.next = new ListNode(100);

    const first = new LinkedList([10, 20]);
    first.tail.next = shared;
    first.tail = shared.next;

    const second = new LinkedList([30, 40, 50]);
    second.tail.next = shared;
    second.tail = shared.next;

    return { first, second, shared };
}

function buildCycleExample() {
    const list = new LinkedList([1, 2, 3, 4, 5]);
    list.tail.next = list.head.next.next;
    return list;
}

function main() {
    console.log('ADVANCED LINKED-LIST PROBLEMS');

    const first = new LinkedList([1, 3, 5, 7]);
    const second = new LinkedList([2, 3, 6, 8]);
    const merged = mergeSorted(first.head, second.head);
    console.log('Merged:', new LinkedListFromHead(merged).toString());

    const duplicateList = new LinkedList([1, 1, 2, 2, 3, 3, 3]);
    removeSortedDuplicates(duplicateList.head);
    console.log('Duplicates removed:', duplicateList.toString());

    const nthList = new LinkedList([10, 20, 30, 40, 50]);
    nthList.head = removeNthFromEnd(nthList.head, 2);
    console.log('Nth node removed:', nthList.toString());

    const intersection = buildIntersectionExample();
    const intersectionNode = findIntersection(
        intersection.first.head,
        intersection.second.head
    );
    console.log(
        'Intersection:',
        intersectionNode ? intersectionNode.value : null,
        'same object:',
        intersectionNode === intersection.shared
    );

    const cyclic = buildCycleExample();
    const cycleEntry = findCycleEntry(cyclic.head);
    console.log('Cycle detected:', detectCycle(cyclic.head));
    console.log('Cycle entry:', cycleEntry?.value ?? null);

    const palindrome = new LinkedList([1, 2, 3, 2, 1]);
    console.log('Palindrome:', isPalindrome(palindrome.head));
    console.log('Restored palindrome list:', palindrome.toString());

    console.log('Josephus survivor:', josephusCircular(8, 3));

    demonstrateEventDrivenProcessing();

    try {
        removeNthFromEnd(new LinkedList([1, 2]).head, 3);
    } catch (error) {
        console.log('Validation failure:', error.message);
    }

    /*
     * A Set provides expected O(1) membership checks, but using a Set for
     * every duplicate-removal task is unnecessary when the input is sorted.
     * The sorted version therefore exploits ordering and uses O(1) space.
     */
    console.log('Empty palindrome:', isPalindrome(null));
}

main();
