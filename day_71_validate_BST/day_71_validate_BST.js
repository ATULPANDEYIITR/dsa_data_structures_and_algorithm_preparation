"use strict";

/*
 * VALIDATE BINARY SEARCH TREE
 *
 * Node.js 18+
 * No external dependencies.
 *
 * Features:
 * - Range-based validation.
 * - Iterative inorder validation.
 * - Duplicate-key policies.
 * - BST insertion and search.
 * - Inorder successor and predecessor.
 * - Deletion.
 * - Lowest common ancestor.
 * - Event-driven validation service.
 * - Asynchronous validation of multiple trees.
 */

const { EventEmitter } = require("node:events");
const assert = require("node:assert/strict");

const DuplicatePolicy = Object.freeze({
    FORBID: "forbid",
    LEFT: "left",
    RIGHT: "right"
});

class BSTError extends Error {}

class DuplicateKeyError extends BSTError {}

class InvalidKeyError extends BSTError {}

function validateKey(key) {
    if (!Number.isSafeInteger(key)) {
        throw new InvalidKeyError(
            "BST keys must be safe JavaScript integers."
        );
    }
}

class TreeNode {
    constructor(key) {
        validateKey(key);
        this.key = key;
        this.left = null;
        this.right = null;
    }
}

class BinarySearchTree {
    constructor(policy = DuplicatePolicy.FORBID) {
        if (!Object.values(DuplicatePolicy).includes(policy)) {
            throw new TypeError("Unknown duplicate-key policy.");
        }

        this.root = null;
        this.size = 0;
        this.policy = policy;
    }

    insert(key) {
        validateKey(key);

        if (!this.root) {
            this.root = new TreeNode(key);
            this.size++;
            return;
        }

        let current = this.root;

        while (true) {
            if (key < current.key) {
                if (!current.left) {
                    current.left = new TreeNode(key);
                    this.size++;
                    return;
                }

                current = current.left;
            } else if (key > current.key) {
                if (!current.right) {
                    current.right = new TreeNode(key);
                    this.size++;
                    return;
                }

                current = current.right;
            } else {
                if (this.policy === DuplicatePolicy.FORBID) {
                    throw new DuplicateKeyError(
                        `Duplicate key: ${key}`
                    );
                }

                const side =
                    this.policy === DuplicatePolicy.LEFT
                        ? "left"
                        : "right";

                if (!current[side]) {
                    current[side] = new TreeNode(key);
                    this.size++;
                    return;
                }

                current = current[side];
            }
        }
    }

    search(key) {
        validateKey(key);

        let current = this.root;

        while (current) {
            if (key === current.key) {
                return current;
            }

            current = key < current.key
                ? current.left
                : current.right;
        }

        return null;
    }

    static validateRange(
        root,
        low = null,
        high = null,
        lowInclusive = false,
        highInclusive = false
    ) {
        const stack = [{
            node: root,
            low,
            high,
            lowInclusive,
            highInclusive
        }];

        while (stack.length) {
            const state = stack.pop();
            const {
                node,
                low: minimum,
                high: maximum,
                lowInclusive: includeMinimum,
                highInclusive: includeMaximum
            } = state;

            if (!node) {
                continue;
            }

            if (!Number.isSafeInteger(node.key)) {
                return false;
            }

            if (minimum !== null) {
                if (node.key < minimum) return false;
                if (
                    node.key === minimum &&
                    !includeMinimum
                ) return false;
            }

            if (maximum !== null) {
                if (node.key > maximum) return false;
                if (
                    node.key === maximum &&
                    !includeMaximum
                ) return false;
            }

            stack.push({
                node: node.left,
                low: minimum,
                high: node.key,
                lowInclusive: includeMinimum,
                highInclusive: false
            });

            stack.push({
                node: node.right,
                low: node.key,
                high: maximum,
                lowInclusive: false,
                highInclusive: includeMaximum
            });
        }

        return true;
    }

    static validateInorder(
        root,
        policy = DuplicatePolicy.FORBID
    ) {
        const stack = [];
        let current = root;
        let previous = null;
        let hasPrevious = false;

        while (current || stack.length) {
            while (current) {
                stack.push(current);
                current = current.left;
            }

            current = stack.pop();

            if (!Number.isSafeInteger(current.key)) {
                return false;
            }

            if (hasPrevious) {
                if (policy === DuplicatePolicy.FORBID) {
                    if (current.key <= previous) return false;
                } else if (current.key < previous) {
                    return false;
                }
            }

            previous = current.key;
            hasPrevious = true;
            current = current.right;
        }

        return true;
    }

    validate() {
        if (this.policy === DuplicatePolicy.FORBID) {
            return BinarySearchTree.validateRange(this.root);
        }

        return (
            BinarySearchTree.validateInorder(
                this.root,
                this.policy
            ) &&
            this.validateDuplicatePlacement()
        );
    }

    validateDuplicatePlacement() {
        const stack = [{
            node: this.root,
            ancestors: []
        }];

        while (stack.length) {
            const { node, ancestors } = stack.pop();

            if (!node) continue;

            for (const [key, side] of ancestors) {
                if (node.key === key) {
                    const expected =
                        this.policy === DuplicatePolicy.LEFT
                            ? "left"
                            : "right";

                    if (side !== expected) return false;
                }
            }

            const next = [...ancestors];

            stack.push({
                node: node.left,
                ancestors: [...next, [node.key, "left"]]
            });

            stack.push({
                node: node.right,
                ancestors: [...next, [node.key, "right"]]
            });
        }

        return true;
    }

    inorder() {
        const result = [];
        const stack = [];
        let current = this.root;

        while (current || stack.length) {
            while (current) {
                stack.push(current);
                current = current.left;
            }

            current = stack.pop();
            result.push(current.key);
            current = current.right;
        }

        return result;
    }

    minimum(node = this.root) {
        if (!node) return null;

        while (node.left) {
            node = node.left;
        }

        return node;
    }

    maximum(node = this.root) {
        if (!node) return null;

        while (node.right) {
            node = node.right;
        }

        return node;
    }

    successor(key) {
        validateKey(key);

        let current = this.root;
        let candidate = null;

        while (current) {
            if (key < current.key) {
                candidate = current;
                current = current.left;
            } else {
                current = current.right;
            }
        }

        return candidate ? candidate.key : null;
    }

    predecessor(key) {
        validateKey(key);

        let current = this.root;
        let candidate = null;

        while (current) {
            if (key > current.key) {
                candidate = current;
                current = current.right;
            } else {
                current = current.left;
            }
        }

        return candidate ? candidate.key : null;
    }

    successorOfNode(key) {
        let current = this.root;
        let candidate = null;

        while (current) {
            if (key < current.key) {
                candidate = current;
                current = current.left;
            } else if (key > current.key) {
                current = current.right;
            } else {
                if (current.right) {
                    return this.minimum(current.right).key;
                }

                return candidate ? candidate.key : null;
            }
        }

        return null;
    }

    predecessorOfNode(key) {
        let current = this.root;
        let candidate = null;

        while (current) {
            if (key > current.key) {
                candidate = current;
                current = current.right;
            } else if (key < current.key) {
                current = current.left;
            } else {
                if (current.left) {
                    return this.maximum(current.left).key;
                }

                return candidate ? candidate.key : null;
            }
        }

        return null;
    }

    lowestCommonAncestor(first, second) {
        if (!this.search(first) || !this.search(second)) {
            return null;
        }

        let current = this.root;

        while (current) {
            if (first < current.key && second < current.key) {
                current = current.left;
            } else if (
                first > current.key &&
                second > current.key
            ) {
                current = current.right;
            } else {
                return current.key;
            }
        }

        return null;
    }

    delete(key) {
        validateKey(key);

        let parent = null;
        let current = this.root;

        while (current && current.key !== key) {
            parent = current;
            current = key < current.key
                ? current.left
                : current.right;
        }

        if (!current) return false;

        if (current.left && current.right) {
            let successorParent = current;
            let successor = current.right;

            while (successor.left) {
                successorParent = successor;
                successor = successor.left;
            }

            current.key = successor.key;

            if (successorParent === current) {
                successorParent.right = successor.right;
            } else {
                successorParent.left = successor.right;
            }
        } else {
            const child = current.left || current.right;

            if (!parent) {
                this.root = child;
            } else if (parent.left === current) {
                parent.left = child;
            } else {
                parent.right = child;
            }
        }

        this.size--;
        return true;
    }
}

/*
 * Event-driven validation service.
 * Validation events allow monitoring and audit integration.
 */
class BSTValidationService extends EventEmitter {
    constructor() {
        super();
        this.results = new Map();
    }

    validateTree(id, tree) {
        if (typeof id !== "string" || !id.trim()) {
            throw new TypeError("Tree identifier is required.");
        }

        if (!(tree instanceof BinarySearchTree)) {
            throw new TypeError("Expected BinarySearchTree instance.");
        }

        const result = tree.validate();

        const record = Object.freeze({
            id,
            valid: result,
            size: tree.size,
            timestamp: new Date().toISOString()
        });

        this.results.set(id, record);

        this.emit(
            result ? "validation:passed" : "validation:failed",
            record
        );

        return record;
    }

    async validateMany(entries) {
        if (!Array.isArray(entries)) {
            throw new TypeError("Expected an array of tree entries.");
        }

        return Promise.all(
            entries.map(async ({ id, tree }) => {
                await Promise.resolve();

                return this.validateTree(id, tree);
            })
        );
    }

    getResult(id) {
        return this.results.get(id) || null;
    }
}

async function main() {
    console.log("1. BUILDING A BST");

    const tree = new BinarySearchTree();

    [50, 30, 70, 20, 40, 60, 80].forEach(
        value => tree.insert(value)
    );

    console.log("Inorder:", tree.inorder());
    console.log("Valid:", tree.validate());

    console.log("\n2. RANGE-BASED VALIDATION");

    const invalid = new TreeNode(10);
    invalid.left = new TreeNode(5);
    invalid.left.right = new TreeNode(12);
    invalid.right = new TreeNode(15);

    console.log(
        "Invalid tree:",
        BinarySearchTree.validateRange(invalid)
    );

    console.log("\n3. SUCCESSOR AND PREDECESSOR");

    for (const key of [20, 30, 40, 50, 60, 70, 80, 55]) {
        console.log(key, {
            successor: tree.successor(key),
            predecessor: tree.predecessor(key)
        });
    }

    console.log("\n4. EXISTING NODE OPERATIONS");

    console.log("Successor of 50:", tree.successorOfNode(50));
    console.log("Predecessor of 50:", tree.predecessorOfNode(50));
    console.log("LCA of 20 and 40:", tree.lowestCommonAncestor(20, 40));

    console.log("\n5. EVENT-DRIVEN VALIDATION");

    const service = new BSTValidationService();

    service.on("validation:passed", result => {
        console.log("PASSED:", result.id);
    });

    service.on("validation:failed", result => {
        console.log("FAILED:", result.id);
    });

    const results = await service.validateMany([
        { id: "production-tree", tree },
        {
            id: "invalid-tree",
            tree: (() => {
                const t = new BinarySearchTree();
                t.root = invalid;
                return t;
            })()
        }
    ]);

    console.log("Validation records:", results);

    console.log("\n6. DELETION");

    tree.delete(20);
    tree.delete(30);
    tree.delete(50);

    console.log("After deletion:", tree.inorder());
    console.log("Valid after deletion:", tree.validate());

    console.log("\n7. TESTS");

    const testTree = new BinarySearchTree();

    [10, 5, 15, 2, 7, 12, 20].forEach(
        value => testTree.insert(value)
    );

    assert.equal(testTree.validate(), true);
    assert.deepEqual(testTree.inorder(), [2, 5, 7, 10, 12, 15, 20]);

    assert.equal(testTree.successor(7), 10);
    assert.equal(testTree.predecessor(7), 5);

    assert.equal(testTree.successor(20), null);
    assert.equal(testTree.predecessor(2), null);

    assert.equal(testTree.successorOfNode(10), 12);
    assert.equal(testTree.predecessorOfNode(10), 7);

    assert.equal(testTree.lowestCommonAncestor(2, 7), 5);

    assert.equal(testTree.delete(10), true);
    assert.equal(testTree.delete(999), false);
    assert.equal(testTree.validate(), true);

    assert.throws(
        () => testTree.insert(5),
        DuplicateKeyError
    );

    assert.throws(
        () => testTree.insert(Number.MAX_SAFE_INTEGER + 1),
        InvalidKeyError
    );

    const emptyTree = new BinarySearchTree();

    assert.equal(emptyTree.validate(), true);
    assert.deepEqual(emptyTree.inorder(), []);

    console.log("All tests passed.");
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
