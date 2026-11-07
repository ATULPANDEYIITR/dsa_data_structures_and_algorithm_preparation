"use strict";

/*
 * BST fundamentals using a product catalog index.
 * Keys are unique numeric product identifiers.
 * Duplicate identifiers are rejected.
 */

const assert = require("node:assert/strict");
const { EventEmitter } = require("node:events");

class BSTNode {
    constructor(key, value) {
        this.key = key;
        this.value = value;
        this.left = null;
        this.right = null;
    }
}

class ProductBST extends EventEmitter {
    #root = null;
    #size = 0;

    get size() {
        return this.#size;
    }

    get isEmpty() {
        return this.#root === null;
    }

    #validateKey(key) {
        if (!Number.isSafeInteger(key)) {
            throw new TypeError(
                "Product identifier must be a safe integer."
            );
        }
    }

    insert(key, value) {
        this.#validateKey(key);

        if (value === null || value === undefined) {
            throw new TypeError("Product value is required.");
        }

        if (this.#root === null) {
            this.#root = new BSTNode(key, value);
            this.#size++;
            this.emit("inserted", { key, value });
            return true;
        }

        let current = this.#root;

        while (current !== null) {
            if (key === current.key) {
                return false;
            }

            if (key < current.key) {
                if (current.left === null) {
                    current.left = new BSTNode(key, value);
                    break;
                }
                current = current.left;
            } else {
                if (current.right === null) {
                    current.right = new BSTNode(key, value);
                    break;
                }
                current = current.right;
            }
        }

        this.#size++;
        this.emit("inserted", { key, value });

        return true;
    }

    search(key) {
        this.#validateKey(key);

        let current = this.#root;

        while (current !== null) {
            if (key === current.key) {
                return {
                    key: current.key,
                    value: current.value
                };
            }

            current = key < current.key
                ? current.left
                : current.right;
        }

        return null;
    }

    #minimumNode(node) {
        if (node === null) return null;

        while (node.left !== null) {
            node = node.left;
        }

        return node;
    }

    minimum() {
        const node = this.#minimumNode(this.#root);
        return node ? node.key : null;
    }

    maximum() {
        let node = this.#root;

        if (node === null) return null;

        while (node.right !== null) {
            node = node.right;
        }

        return node.key;
    }

    delete(key) {
        this.#validateKey(key);

        let deletedValue;

        const remove = (node) => {
            if (node === null) return null;

            if (key < node.key) {
                node.left = remove(node.left);
                return node;
            }

            if (key > node.key) {
                node.right = remove(node.right);
                return node;
            }

            deletedValue = node.value;

            if (node.left === null) return node.right;
            if (node.right === null) return node.left;

            // Two-child deletion: replace with inorder successor.
            const successor = this.#minimumNode(node.right);

            node.key = successor.key;
            node.value = successor.value;

            node.right = this.#removeMinimum(node.right);

            return node;
        };

        this.#root = remove(this.#root);

        if (deletedValue === undefined) return false;

        this.#size--;
        this.emit("deleted", { key, value: deletedValue });

        return true;
    }

    #removeMinimum(node) {
        if (node.left === null) return node.right;

        node.left = this.#removeMinimum(node.left);
        return node;
    }

    inorder() {
        const result = [];
        const stack = [];
        let current = this.#root;

        while (stack.length > 0 || current !== null) {
            while (current !== null) {
                stack.push(current);
                current = current.left;
            }

            current = stack.pop();
            result.push({
                key: current.key,
                value: current.value
            });

            current = current.right;
        }

        return result;
    }

    preorder() {
        if (this.#root === null) return [];

        const stack = [this.#root];
        const result = [];

        while (stack.length > 0) {
            const node = stack.pop();

            result.push(node.key);

            if (node.right) stack.push(node.right);
            if (node.left) stack.push(node.left);
        }

        return result;
    }

    postorder() {
        if (this.#root === null) return [];

        const first = [this.#root];
        const second = [];

        while (first.length > 0) {
            const node = first.pop();
            second.push(node.key);

            if (node.left) first.push(node.left);
            if (node.right) first.push(node.right);
        }

        return second.reverse();
    }

    levelOrder() {
        if (this.#root === null) return [];

        const queue = [this.#root];
        const result = [];

        // The index avoids repeated Array.shift() operations.
        let head = 0;

        while (head < queue.length) {
            const levelEnd = queue.length;
            const level = [];

            while (head < levelEnd) {
                const node = queue[head++];
                level.push(node.key);

                if (node.left) queue.push(node.left);
                if (node.right) queue.push(node.right);
            }

            result.push(level);
        }

        return result;
    }

    height() {
        if (this.#root === null) return -1;

        const stack = [[this.#root, 0]];
        let maximumDepth = 0;

        while (stack.length > 0) {
            const [node, depth] = stack.pop();

            maximumDepth = Math.max(maximumDepth, depth);

            if (node.left) stack.push([node.left, depth + 1]);
            if (node.right) stack.push([node.right, depth + 1]);
        }

        return maximumDepth;
    }

    kthSmallest(k) {
        if (!Number.isSafeInteger(k) || k < 1 || k > this.#size) {
            throw new RangeError("Invalid kth-smallest position.");
        }

        const stack = [];
        let current = this.#root;
        let count = 0;

        while (stack.length > 0 || current !== null) {
            while (current !== null) {
                stack.push(current);
                current = current.left;
            }

            current = stack.pop();
            count++;

            if (count === k) return current.key;

            current = current.right;
        }

        throw new Error("BST integrity violation.");
    }

    isValid() {
        if (this.#root === null) return this.#size === 0;

        const stack = [{
            node: this.#root,
            lower: -Infinity,
            upper: Infinity
        }];

        let count = 0;

        while (stack.length > 0) {
            const { node, lower, upper } = stack.pop();

            if (node.key <= lower || node.key >= upper) {
                return false;
            }

            count++;

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

        return count === this.#size;
    }

    toBalanced() {
        const entries = this.inorder();
        const balanced = new ProductBST();

        const build = (start, end) => {
            if (start > end) return null;

            const middle = Math.floor((start + end) / 2);
            const entry = entries[middle];
            const node = new BSTNode(entry.key, entry.value);

            node.left = build(start, middle - 1);
            node.right = build(middle + 1, end);

            return node;
        };

        balanced.#root = build(0, entries.length - 1);
        balanced.#size = entries.length;

        return balanced;
    }
}

// Event-driven product catalog example.
async function main() {
    const catalog = new ProductBST();

    catalog.on("inserted", ({ key }) => {
        console.log(`Catalog entry added: ${key}`);
    });

    catalog.on("deleted", ({ key }) => {
        console.log(`Catalog entry removed: ${key}`);
    });

    console.log("\nPRODUCT CATALOG BST");
    console.log("===================");

    const products = [
        [500, { name: "Laptop", stock: 12 }],
        [300, { name: "Keyboard", stock: 30 }],
        [700, { name: "Monitor", stock: 8 }],
        [200, { name: "Mouse", stock: 45 }],
        [400, { name: "Headphones", stock: 20 }],
        [600, { name: "Webcam", stock: 15 }],
        [800, { name: "Printer", stock: 5 }]
    ];

    for (const [id, product] of products) {
        catalog.insert(id, product);
    }

    console.log("\nDuplicate rejected:", catalog.insert(500, {
        name: "Duplicate Laptop",
        stock: 1
    }));

    console.log("\nSearch:", catalog.search(400));
    console.log("Missing product:", catalog.search(999));

    console.log("\nInorder:", catalog.inorder());
    console.log("Preorder:", catalog.preorder());
    console.log("Postorder:", catalog.postorder());
    console.log("Level order:", catalog.levelOrder());

    console.log("\nMinimum ID:", catalog.minimum());
    console.log("Maximum ID:", catalog.maximum());
    console.log("Height:", catalog.height());
    console.log("Third smallest:", catalog.kthSmallest(3));

    console.log("\nDelete leaf:", catalog.delete(200));
    console.log("Delete two-child node:", catalog.delete(300));
    console.log("Delete missing node:", catalog.delete(999));

    console.log("\nValid BST:", catalog.isValid());
    console.log("Remaining size:", catalog.size);

    const balanced = catalog.toBalanced();

    console.log("\nBalanced preorder:", balanced.preorder());
    console.log("Balanced height:", balanced.height());

    // Asynchronous API-style access.
    const lookupProduct = async (id) => {
        await Promise.resolve();
        return catalog.search(id);
    };

    const product = await lookupProduct(700);
    console.log("\nAsync product lookup:", product);

    // Edge-case verification.
    const empty = new ProductBST();

    assert.equal(empty.minimum(), null);
    assert.equal(empty.height(), -1);
    assert.deepEqual(empty.inorder(), []);

    const single = new ProductBST();
    single.insert(10, { name: "Single", stock: 1 });

    assert.equal(single.delete(10), true);
    assert.equal(single.isEmpty, true);

    assert.equal(catalog.isValid(), true);
    assert.equal(balanced.isValid(), true);
    assert.equal(catalog.kthSmallest(1), 400);

    assert.throws(() => catalog.insert(NaN, {}), TypeError);
    assert.throws(() => catalog.kthSmallest(100), RangeError);

    console.log("\nAll JavaScript assertions passed.");
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
