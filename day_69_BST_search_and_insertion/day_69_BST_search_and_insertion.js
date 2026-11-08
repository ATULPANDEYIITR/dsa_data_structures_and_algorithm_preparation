"use strict";

/*
 * Binary Search Tree: Search, Insert, Minimum, Maximum.
 *
 * Node.js implementation with:
 * - Unique integer keys
 * - Event-driven operation logging
 * - Iterative tree operations
 * - Search comparison tracking
 * - Structural validation
 * - Performance evaluation
 * - Asynchronous JSON export
 */

const fs = require("node:fs/promises");
const { performance } = require("node:perf_hooks");
const EventEmitter = require("node:events");

class BSTNode {
    constructor(key) {
        this.key = key;
        this.left = null;
        this.right = null;
    }
}

class BinarySearchTree extends EventEmitter {
    constructor(name = "BST") {
        super();

        this.name = name;
        this.root = null;
        this.size = 0;
        this.lastComparisons = 0;
    }

    static validateKey(key) {
        if (!Number.isSafeInteger(key)) {
            throw new TypeError(
                "Key must be a safe JavaScript integer."
            );
        }
    }

    insert(key) {
        BinarySearchTree.validateKey(key);

        const node = new BSTNode(key);

        if (this.root === null) {
            this.root = node;
            this.size++;

            this.emit("inserted", {
                tree: this.name,
                key
            });

            return true;
        }

        let current = this.root;

        while (true) {
            if (key === current.key) {
                this.emit("duplicate", { key });
                return false;
            }

            const direction =
                key < current.key ? "left" : "right";

            if (current[direction] === null) {
                current[direction] = node;
                this.size++;

                this.emit("inserted", {
                    tree: this.name,
                    key
                });

                return true;
            }

            current = current[direction];
        }
    }

    search(key) {
        BinarySearchTree.validateKey(key);

        this.lastComparisons = 0;
        let current = this.root;

        while (current !== null) {
            this.lastComparisons++;

            if (current.key === key) {
                this.emit("search", {
                    key,
                    found: true,
                    comparisons: this.lastComparisons
                });

                return true;
            }

            current = key < current.key
                ? current.left
                : current.right;
        }

        this.emit("search", {
            key,
            found: false,
            comparisons: this.lastComparisons
        });

        return false;
    }

    minimum() {
        if (this.root === null) {
            return null;
        }

        let current = this.root;

        while (current.left !== null) {
            current = current.left;
        }

        return current.key;
    }

    maximum() {
        if (this.root === null) {
            return null;
        }

        let current = this.root;

        while (current.right !== null) {
            current = current.right;
        }

        return current.key;
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

    height() {
        if (this.root === null) {
            return -1;
        }

        const queue = [{ node: this.root, depth: 0 }];
        let maxDepth = 0;

        for (let index = 0; index < queue.length; index++) {
            const { node, depth } = queue[index];

            maxDepth = Math.max(maxDepth, depth);

            if (node.left !== null) {
                queue.push({
                    node: node.left,
                    depth: depth + 1
                });
            }

            if (node.right !== null) {
                queue.push({
                    node: node.right,
                    depth: depth + 1
                });
            }
        }

        return maxDepth;
    }

    validate() {
        const stack = [{
            node: this.root,
            lower: null,
            upper: null
        }];

        let count = 0;

        while (stack.length > 0) {
            const { node, lower, upper } = stack.pop();

            if (node === null) {
                continue;
            }

            if (
                (lower !== null && node.key <= lower) ||
                (upper !== null && node.key >= upper)
            ) {
                return false;
            }

            count++;

            stack.push({
                node: node.left,
                lower,
                upper: node.key
            });

            stack.push({
                node: node.right,
                lower: node.key,
                upper
            });
        }

        return count === this.size;
    }

    snapshot() {
        return {
            name: this.name,
            size: this.size,
            height: this.height(),
            minimum: this.minimum(),
            maximum: this.maximum(),
            keys: this.inorder(),
            valid: this.validate()
        };
    }

    async exportJSON(filename) {
        if (!filename.endsWith(".json")) {
            throw new Error("Expected a JSON filename.");
        }

        const data = JSON.stringify(this.snapshot(), null, 2);

        await fs.writeFile(filename, data, {
            encoding: "utf8",
            flag: "w"
        });
    }
}

function buildMedianFirst(values) {
    const sorted = [...values].sort((a, b) => a - b);
    const result = [];
    const stack = [[0, sorted.length - 1]];

    while (stack.length > 0) {
        const [low, high] = stack.pop();

        if (low > high) {
            continue;
        }

        const middle = Math.floor((low + high) / 2);
        result.push(sorted[middle]);

        stack.push([middle + 1, high]);
        stack.push([low, middle - 1]);
    }

    return result;
}

function benchmark() {
    console.log("\n=== Performance Benchmark ===");

    const values = Array.from(
        { length: 2000 },
        (_, index) => index + 1
    );

    const balanced = new BinarySearchTree("Balanced");
    const skewed = new BinarySearchTree("Skewed");

    for (const key of buildMedianFirst(values)) {
        balanced.insert(key);
    }

    for (const key of values) {
        skewed.insert(key);
    }

    const target = 2000;

    for (const tree of [balanced, skewed]) {
        const start = performance.now();
        const found = tree.search(target);
        const duration = performance.now() - start;

        console.log({
            tree: tree.name,
            found,
            height: tree.height(),
            comparisons: tree.lastComparisons,
            milliseconds: duration.toFixed(5)
        });
    }
}

async function main() {
    const tree = new BinarySearchTree("InventoryIndex");

    tree.on("inserted", event => {
        console.log("Inserted:", event.key);
    });

    tree.on("duplicate", event => {
        console.log("Duplicate rejected:", event.key);
    });

    tree.on("search", event => {
        console.log(
            `Search ${event.key}: ${event.found}, ` +
            `comparisons=${event.comparisons}`
        );
    });

    console.log("\n=== Inventory Index ===");

    const inventoryIds = [
        500, 300, 700, 200, 400, 600, 800, 350, 450
    ];

    for (const id of inventoryIds) {
        tree.insert(id);
    }

    tree.insert(500);

    console.log("Search 400:", tree.search(400));
    console.log("Search 999:", tree.search(999));
    console.log("Minimum ID:", tree.minimum());
    console.log("Maximum ID:", tree.maximum());
    console.log("Sorted IDs:", tree.inorder());
    console.log("Tree height:", tree.height());
    console.log("Valid BST:", tree.validate());

    if (!tree.validate()) {
        throw new Error("BST integrity validation failed.");
    }

    if (tree.search(400) !== true) {
        throw new Error("Search test failed.");
    }

    if (tree.minimum() !== 200 || tree.maximum() !== 800) {
        throw new Error("Boundary test failed.");
    }

    const empty = new BinarySearchTree("Empty");

    if (
        empty.minimum() !== null ||
        empty.maximum() !== null ||
        empty.search(10)
    ) {
        throw new Error("Empty tree test failed.");
    }

    try {
        tree.insert(1.5);
    } catch (error) {
        console.log("Invalid input rejected:", error.message);
    }

    try {
        await tree.exportJSON("bst_report.json");
        console.log("JSON report exported.");
    } catch (error) {
        console.error("Export failure:", error.message);
    }

    benchmark();

    console.log("\nAll tests completed successfully.");
}

main().catch(error => {
    console.error("Application failure:", error);
    process.exitCode = 1;
});
