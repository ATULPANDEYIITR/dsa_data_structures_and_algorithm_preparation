"use strict";

/**
 * Binary Search Tree Assessment Engine
 * Node.js 18+
 *
 * Features:
 * - Iterative insertion and searching
 * - Deletion with successor replacement
 * - BST invariant validation
 * - LCA, minimum, maximum
 * - Successor and predecessor
 * - Traversal and range queries
 * - Event-driven operation monitoring
 * - Asynchronous assessment and batch execution
 * - Deterministic tests
 *
 * Duplicate policy: reject duplicate keys.
 */

const { EventEmitter } = require("node:events");
const fs = require("node:fs/promises");
const path = require("node:path");
const assert = require("node:assert/strict");

class BSTError extends Error {}

class InvalidBSTError extends BSTError {}

class BSTNode {
    constructor(key) {
        this.key = key;
        this.left = null;
        this.right = null;
    }
}

class BinarySearchTree extends EventEmitter {
    constructor(values = []) {
        super();

        this.root = null;
        this.size = 0;

        for (const value of values) {
            this.insert(value);
        }
    }

    static validateKey(key) {
        if (!Number.isSafeInteger(key)) {
            throw new TypeError(
                "BST keys must be safe integers."
            );
        }
    }

    emitResult(operation, key, success) {
        this.emit("operation", {
            operation,
            key,
            success,
            size: this.size,
            timestamp: new Date().toISOString()
        });
    }

    insert(key) {
        BinarySearchTree.validateKey(key);

        if (this.root === null) {
            this.root = new BSTNode(key);
            this.size = 1;
            this.emitResult("insert", key, true);
            return true;
        }

        let current = this.root;

        while (true) {
            if (key === current.key) {
                this.emitResult("insert", key, false);
                return false;
            }

            const direction = key < current.key
                ? "left"
                : "right";

            if (current[direction] === null) {
                current[direction] = new BSTNode(key);
                this.size++;
                this.emitResult("insert", key, true);
                return true;
            }

            current = current[direction];
        }
    }

    search(key) {
        BinarySearchTree.validateKey(key);

        let current = this.root;

        while (current !== null) {
            if (key === current.key) {
                this.emitResult("search", key, true);
                return current;
            }

            current = key < current.key
                ? current.left
                : current.right;
        }

        this.emitResult("search", key, false);
        return null;
    }

    contains(key) {
        return this.search(key) !== null;
    }

    minimum(node = this.root) {
        if (node === null) return null;

        while (node.left !== null) {
            node = node.left;
        }

        return node.key;
    }

    maximum(node = this.root) {
        if (node === null) return null;

        while (node.right !== null) {
            node = node.right;
        }

        return node.key;
    }

    delete(key) {
        BinarySearchTree.validateKey(key);

        let parent = null;
        let current = this.root;

        while (current !== null && current.key !== key) {
            parent = current;
            current = key < current.key
                ? current.left
                : current.right;
        }

        if (current === null) {
            this.emitResult("delete", key, false);
            return false;
        }

        // Two-child deletion: replace with inorder successor.
        if (current.left !== null && current.right !== null) {
            let successorParent = current;
            let successor = current.right;

            while (successor.left !== null) {
                successorParent = successor;
                successor = successor.left;
            }

            current.key = successor.key;
            parent = successorParent;
            current = successor;
        }

        const child = current.left !== null
            ? current.left
            : current.right;

        if (parent === null) {
            this.root = child;
        } else if (parent.left === current) {
            parent.left = child;
        } else {
            parent.right = child;
        }

        this.size--;
        this.emitResult("delete", key, true);
        return true;
    }

    inorder() {
        const result = [];
        const stack = [];
        let current = this.root;

        while (current !== null || stack.length > 0) {
            while (current !== null) {
                stack.push(current);
                current = current.left;
            }

            current = stack.pop();
            result.push(current.key);
            current = current.right;
        }

        return result;
    }

    preorder() {
        if (this.root === null) return [];

        const result = [];
        const stack = [this.root];

        while (stack.length > 0) {
            const node = stack.pop();
            result.push(node.key);

            if (node.right) stack.push(node.right);
            if (node.left) stack.push(node.left);
        }

        return result;
    }

    postorder() {
        if (this.root === null) return [];

        const result = [];
        const stack = [[this.root, false]];

        while (stack.length > 0) {
            const [node, visited] = stack.pop();

            if (visited) {
                result.push(node.key);
                continue;
            }

            stack.push([node, true]);

            if (node.right) stack.push([node.right, false]);
            if (node.left) stack.push([node.left, false]);
        }

        return result;
    }

    levelOrder() {
        if (this.root === null) return [];

        const queue = [this.root];
        const result = [];

        for (let index = 0; index < queue.length; index++) {
            const node = queue[index];
            result.push(node.key);

            if (node.left) queue.push(node.left);
            if (node.right) queue.push(node.right);
        }

        return result;
    }

    validate() {
        if (this.root === null) {
            return this.size === 0;
        }

        const stack = [{
            node: this.root,
            lower: null,
            upper: null
        }];

        const seen = new Set();

        while (stack.length > 0) {
            const { node, lower, upper } = stack.pop();

            if (seen.has(node)) return false;
            seen.add(node);

            if (!Number.isSafeInteger(node.key)) return false;

            if (lower !== null && node.key <= lower) return false;
            if (upper !== null && node.key >= upper) return false;

            if (node.left) {
                stack.push({
                    node: node.left,
                    lower,
                    upper: node.key
                });
            }

            if (node.right) {
                stack.push({
                    node: node.right,
                    lower: node.key,
                    upper
                });
            }
        }

        return seen.size === this.size;
    }

    lowestCommonAncestor(first, second) {
        BinarySearchTree.validateKey(first);
        BinarySearchTree.validateKey(second);

        if (!this.contains(first) || !this.contains(second)) {
            return null;
        }

        let current = this.root;

        while (current !== null) {
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

    successor(key) {
        BinarySearchTree.validateKey(key);

        let current = this.root;
        let candidate = null;

        while (current !== null) {
            if (key < current.key) {
                candidate = current.key;
                current = current.left;
            } else {
                current = current.right;
            }
        }

        return candidate;
    }

    predecessor(key) {
        BinarySearchTree.validateKey(key);

        let current = this.root;
        let candidate = null;

        while (current !== null) {
            if (key > current.key) {
                candidate = current.key;
                current = current.right;
            } else {
                current = current.left;
            }
        }

        return candidate;
    }

    rangeQuery(low, high) {
        BinarySearchTree.validateKey(low);
        BinarySearchTree.validateKey(high);

        if (low > high) {
            throw new RangeError("Invalid range.");
        }

        const result = [];
        const stack = [];
        let current = this.root;

        while (current !== null || stack.length > 0) {
            while (current !== null) {
                if (current.key >= low) {
                    stack.push(current);
                    current = current.left;
                } else {
                    current = current.right;
                }
            }

            if (stack.length === 0) break;

            current = stack.pop();

            if (current.key > high) break;

            result.push(current.key);
            current = current.right;
        }

        return result;
    }

    height() {
        if (this.root === null) return -1;

        const queue = [[this.root, 0]];
        let maximumDepth = 0;

        for (let i = 0; i < queue.length; i++) {
            const [node, depth] = queue[i];
            maximumDepth = Math.max(maximumDepth, depth);

            if (node.left) queue.push([node.left, depth + 1]);
            if (node.right) queue.push([node.right, depth + 1]);
        }

        return maximumDepth;
    }

    toJSON() {
        const serialize = node => {
            if (node === null) return null;

            return {
                key: node.key,
                left: serialize(node.left),
                right: serialize(node.right)
            };
        };

        return {
            version: 1,
            size: this.size,
            root: serialize(this.root)
        };
    }

    static fromJSON(data) {
        if (
            data === null ||
            typeof data !== "object" ||
            data.version !== 1 ||
            !Number.isSafeInteger(data.size) ||
            data.size < 0
        ) {
            throw new InvalidBSTError("Invalid serialized tree.");
        }

        const tree = new BinarySearchTree();

        const restore = (item, lower, upper) => {
            if (item === null) return null;

            if (
                typeof item !== "object" ||
                Array.isArray(item) ||
                !Object.hasOwn(item, "key") ||
                !Object.hasOwn(item, "left") ||
                !Object.hasOwn(item, "right")
            ) {
                throw new InvalidBSTError("Invalid node.");
            }

            const key = item.key;
            BinarySearchTree.validateKey(key);

            if (lower !== null && key <= lower) {
                throw new InvalidBSTError("Lower-bound violation.");
            }

            if (upper !== null && key >= upper) {
                throw new InvalidBSTError("Upper-bound violation.");
            }

            tree.size++;

            const node = new BSTNode(key);
            node.left = restore(item.left, lower, key);
            node.right = restore(item.right, key, upper);

            return node;
        };

        tree.root = restore(data.root, null, null);

        if (tree.size !== data.size || !tree.validate()) {
            throw new InvalidBSTError("Tree integrity check failed.");
        }

        return tree;
    }
}

class BSTAssessmentService {
    constructor(tree) {
        this.tree = tree;
    }

    async evaluate(requests) {
        if (!Array.isArray(requests)) {
            throw new TypeError("Requests must be an array.");
        }

        // Preserve request order while isolating individual failures.
        return Promise.all(
            requests.map(async request => {
                try {
                    if (
                        request === null ||
                        typeof request !== "object"
                    ) {
                        throw new TypeError("Invalid request.");
                    }

                    switch (request.operation) {
                        case "search":
                            return {
                                operation: "search",
                                key: request.key,
                                found: this.tree.contains(request.key)
                            };

                        case "successor":
                            return {
                                operation: "successor",
                                key: request.key,
                                result: this.tree.successor(request.key)
                            };

                        case "predecessor":
                            return {
                                operation: "predecessor",
                                key: request.key,
                                result: this.tree.predecessor(request.key)
                            };

                        case "insert":
                            return {
                                operation: "insert",
                                key: request.key,
                                inserted: this.tree.insert(request.key)
                            };

                        case "delete":
                            return {
                                operation: "delete",
                                key: request.key,
                                deleted: this.tree.delete(request.key)
                            };

                        default:
                            throw new BSTError(
                                "Unsupported assessment operation."
                            );
                    }
                } catch (error) {
                    return {
                        operation: request.operation,
                        error: error.message
                    };
                }
            })
        );
    }

    report() {
        return {
            size: this.tree.size,
            valid: this.tree.validate(),
            inorder: this.tree.inorder(),
            minimum: this.tree.minimum(),
            maximum: this.tree.maximum(),
            height: this.tree.height()
        };
    }
}

async function runTests() {
    const tree = new BinarySearchTree([
        50, 30, 70, 20, 40, 60, 80
    ]);

    const events = [];

    tree.on("operation", event => events.push(event));

    assert.equal(tree.search(40).key, 40);
    assert.equal(tree.search(999), null);

    assert.equal(tree.insert(65), true);
    assert.equal(tree.insert(65), false);

    assert.equal(tree.minimum(), 20);
    assert.equal(tree.maximum(), 80);

    assert.deepEqual(
        tree.inorder(),
        [20, 30, 40, 50, 60, 65, 70, 80]
    );

    assert.equal(tree.lowestCommonAncestor(20, 40), 30);
    assert.equal(tree.lowestCommonAncestor(20, 80), 50);

    assert.equal(tree.successor(40), 50);
    assert.equal(tree.predecessor(60), 50);
    assert.equal(tree.successor(80), null);
    assert.equal(tree.predecessor(20), null);

    assert.deepEqual(
        tree.rangeQuery(30, 70),
        [30, 40, 50, 60, 65, 70]
    );

    assert.equal(tree.delete(50), true);
    assert.equal(tree.delete(999), false);
    assert.equal(tree.validate(), true);

    assert.throws(
        () => tree.insert(Number.MAX_SAFE_INTEGER + 1),
        TypeError
    );

    const restored = BinarySearchTree.fromJSON(tree.toJSON());

    assert.deepEqual(restored.inorder(), tree.inorder());

    const service = new BSTAssessmentService(restored);

    const results = await service.evaluate([
        { operation: "search", key: 40 },
        { operation: "successor", key: 40 },
        { operation: "predecessor", key: 40 },
        { operation: "search", key: 999 },
        { operation: "unknown", key: 40 }
    ]);

    assert.equal(results.length, 5);
    assert.equal(results[0].found, true);
    assert.ok(results[4].error);

    assert.ok(events.length > 0);

    const temporaryFile = path.join(
        require("node:os").tmpdir(),
        `bst-assessment-${process.pid}.json`
    );

    try {
        await fs.writeFile(
            temporaryFile,
            JSON.stringify(tree.toJSON()),
            { encoding: "utf8", flag: "wx" }
        );

        const document = JSON.parse(
            await fs.readFile(temporaryFile, "utf8")
        );

        assert.deepEqual(
            BinarySearchTree.fromJSON(document).inorder(),
            tree.inorder()
        );
    } finally {
        await fs.unlink(temporaryFile).catch(error => {
            if (error.code !== "ENOENT") throw error;
        });
    }

    console.log("All BST tests passed.");
    console.log("Assessment report:", service.report());
    console.log("Batch results:", results);
}

runTests().catch(error => {
    console.error("Assessment failed:", error);
    process.exitCode = 1;
});
