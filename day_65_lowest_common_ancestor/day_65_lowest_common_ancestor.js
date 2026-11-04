"use strict";

/**
 * Lowest Common Ancestor implementation.
 *
 * Includes:
 * - Binary tree construction and validation
 * - Recursive LCA
 * - Parent-pointer LCA
 * - Iterative LCA
 * - Binary lifting for repeated queries
 * - Event-driven query processing
 */

const { EventEmitter } = require("node:events");

class TreeNode {
    constructor(value) {
        if (!Number.isSafeInteger(value)) {
            throw new TypeError("Node value must be a safe integer.");
        }

        this.value = value;
        this.left = null;
        this.right = null;
        this.parent = null;
    }
}

class BinaryTree {
    constructor(root = null) {
        this.root = root;
        this.nodes = new Map();
    }

    register(node) {
        if (!(node instanceof TreeNode)) {
            throw new TypeError("Invalid tree node.");
        }

        if (this.nodes.has(node.value)) {
            throw new Error(`Duplicate node value: ${node.value}`);
        }

        this.nodes.set(node.value, node);
    }

    attach(parentValue, childValue, side) {
        const parent = this.nodes.get(parentValue);
        const child = this.nodes.get(childValue);

        if (!parent || !child) {
            throw new Error("Parent or child does not exist.");
        }

        if (!["left", "right"].includes(side)) {
            throw new Error("Side must be left or right.");
        }

        if (parent === child || child.parent !== null) {
            throw new Error("Invalid child attachment.");
        }

        let current = parent;

        while (current !== null) {
            if (current === child) {
                throw new Error("Attachment would create a cycle.");
            }
            current = current.parent;
        }

        if (parent[side] !== null) {
            throw new Error(`${side} child already exists.`);
        }

        parent[side] = child;
        child.parent = parent;
    }

    validate() {
        if (this.root === null) {
            if (this.nodes.size !== 0) {
                throw new Error("Nodes exist without a root.");
            }
            return true;
        }

        const visited = new Set();
        const stack = [{ node: this.root, parent: null }];

        while (stack.length > 0) {
            const { node, parent } = stack.pop();

            if (visited.has(node)) {
                throw new Error("Cycle or shared child detected.");
            }

            if (node.parent !== parent) {
                throw new Error("Parent pointer inconsistency.");
            }

            visited.add(node);

            if (node.left) {
                stack.push({ node: node.left, parent: node });
            }

            if (node.right) {
                stack.push({ node: node.right, parent: node });
            }
        }

        if (visited.size !== this.nodes.size) {
            throw new Error("Tree contains unreachable nodes.");
        }

        return true;
    }

    getNode(value) {
        return this.nodes.get(value) ?? null;
    }
}

class LCAService {
    constructor(tree) {
        tree.validate();
        this.tree = tree;
    }

    recursive(first, second) {
        this.requireNodes(first, second);

        const search = (node) => {
            if (!node || node === first || node === second) {
                return node;
            }

            const left = search(node.left);
            const right = search(node.right);

            if (left && right) {
                return node;
            }

            return left || right;
        };

        const result = search(this.tree.root);

        // A single matching node is not sufficient when the other
        // target does not exist in the tree.
        return this.contains(first) && this.contains(second)
            ? result
            : null;
    }

    contains(target) {
        if (!target) return false;

        const stack = this.tree.root ? [this.tree.root] : [];

        while (stack.length) {
            const node = stack.pop();

            if (node === target) return true;

            if (node.left) stack.push(node.left);
            if (node.right) stack.push(node.right);
        }

        return false;
    }

    requireNodes(first, second) {
        if (!(first instanceof TreeNode) ||
            !(second instanceof TreeNode)) {
            throw new TypeError("Both targets must be TreeNode instances.");
        }
    }

    parentBased(first, second) {
        this.requireNodes(first, second);

        if (!this.contains(first) || !this.contains(second)) {
            return null;
        }

        const ancestors = new Set();
        let current = first;

        while (current) {
            if (ancestors.has(current)) {
                throw new Error("Parent cycle detected.");
            }

            ancestors.add(current);
            current = current.parent;
        }

        current = second;

        while (current) {
            if (ancestors.has(current)) {
                return current;
            }
            current = current.parent;
        }

        return null;
    }

    iterative(first, second) {
        this.requireNodes(first, second);

        const parentMap = new Map();
        const stack = this.tree.root ? [this.tree.root] : [];

        while (stack.length) {
            const node = stack.pop();

            if (node.left) {
                parentMap.set(node.left, node);
                stack.push(node.left);
            }

            if (node.right) {
                parentMap.set(node.right, node);
                stack.push(node.right);
            }
        }

        if (first !== this.tree.root && !parentMap.has(first)) {
            return null;
        }

        if (second !== this.tree.root && !parentMap.has(second)) {
            return null;
        }

        const ancestors = new Set();
        let current = first;

        while (current) {
            ancestors.add(current);
            current = parentMap.get(current) ?? null;
        }

        current = second;

        while (current) {
            if (ancestors.has(current)) return current;
            current = parentMap.get(current) ?? null;
        }

        return null;
    }
}

/**
 * Binary lifting supports many LCA queries after preprocessing.
 * Each node stores its 2^k-th ancestor.
 */
class BinaryLiftingIndex {
    constructor(tree) {
        tree.validate();

        if (!tree.root) {
            throw new Error("Cannot index an empty tree.");
        }

        this.depth = new Map();
        this.up = new Map();
        this.maxLevel = Math.ceil(
            Math.log2(Math.max(1, tree.nodes.size))
        ) + 1;

        const queue = [tree.root];
        this.depth.set(tree.root, 0);
        this.up.set(tree.root, [null]);

        for (let index = 0; index < queue.length; index++) {
            const node = queue[index];

            for (const child of [node.left, node.right]) {
                if (!child) continue;

                this.depth.set(child, this.depth.get(node) + 1);

                const ancestors = [node];

                for (let k = 1; k < this.maxLevel; k++) {
                    const previous = ancestors[k - 1];
                    ancestors[k] = previous
                        ? (this.up.get(previous)?.[k - 1] ?? null)
                        : null;
                }

                this.up.set(child, ancestors);
                queue.push(child);
            }
        }
    }

    query(first, second) {
        if (!this.depth.has(first) || !this.depth.has(second)) {
            return null;
        }

        let a = first;
        let b = second;

        if (this.depth.get(a) < this.depth.get(b)) {
            [a, b] = [b, a];
        }

        let difference = this.depth.get(a) - this.depth.get(b);
        let bit = 0;

        while (difference > 0) {
            if (difference & 1) {
                a = this.up.get(a)[bit];
            }

            difference >>= 1;
            bit++;
        }

        if (a === b) return a;

        for (let k = this.maxLevel - 1; k >= 0; k--) {
            const ancestorA = this.up.get(a)?.[k] ?? null;
            const ancestorB = this.up.get(b)?.[k] ?? null;

            if (ancestorA !== ancestorB) {
                a = ancestorA;
                b = ancestorB;
            }
        }

        return this.up.get(a)?.[0] ?? null;
    }
}

class LCAQueryProcessor extends EventEmitter {
    constructor(service) {
        super();
        this.service = service;
        this.queryCount = 0;
    }

    process(firstValue, secondValue, strategy = "recursive") {
        const first = this.service.tree.getNode(firstValue);
        const second = this.service.tree.getNode(secondValue);

        if (!first || !second) {
            const error = {
                firstValue,
                secondValue,
                message: "Target node not found."
            };

            this.emit("queryError", error);
            return null;
        }

        const methods = {
            recursive: () => this.service.recursive(first, second),
            parent: () => this.service.parentBased(first, second),
            iterative: () => this.service.iterative(first, second)
        };

        if (!methods[strategy]) {
            throw new Error("Unsupported LCA strategy.");
        }

        const result = methods[strategy]();

        this.queryCount++;

        const response = {
            first: firstValue,
            second: secondValue,
            ancestor: result?.value ?? null,
            strategy,
            sequence: this.queryCount
        };

        this.emit("queryCompleted", response);
        return response;
    }
}

function buildTree() {
    const tree = new BinaryTree();

    const values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    const nodes = new Map();

    for (const value of values) {
        const node = new TreeNode(value);
        nodes.set(value, node);
        tree.register(node);
    }

    tree.root = nodes.get(1);

    const relationships = [
        [1, 2, "left"],
        [1, 3, "right"],
        [2, 4, "left"],
        [2, 5, "right"],
        [3, 6, "left"],
        [3, 7, "right"],
        [5, 8, "left"],
        [5, 9, "right"],
        [7, 10, "right"]
    ];

    for (const [parent, child, side] of relationships) {
        tree.attach(parent, child, side);
    }

    return tree;
}

function runTests() {
    const tree = buildTree();
    const service = new LCAService(tree);
    const index = new BinaryLiftingIndex(tree);

    const expected = [
        [4, 5, 2],
        [4, 6, 1],
        [8, 9, 5],
        [8, 10, 1],
        [2, 8, 2],
        [7, 10, 7]
    ];

    for (const [a, b, expectedValue] of expected) {
        const first = tree.getNode(a);
        const second = tree.getNode(b);

        console.assert(
            service.recursive(first, second)?.value === expectedValue
        );

        console.assert(
            service.parentBased(first, second)?.value === expectedValue
        );

        console.assert(
            service.iterative(first, second)?.value === expectedValue
        );

        console.assert(
            index.query(first, second)?.value === expectedValue
        );
    }

    console.assert(
        service.recursive(tree.getNode(4), new TreeNode(99)) === null
    );

    console.assert(
        index.query(tree.getNode(4), new TreeNode(99)) === null
    );

    console.assert(
        index.query(tree.getNode(8), tree.getNode(8)).value === 8
    );

    console.log("All JavaScript LCA tests passed.");
}

function main() {
    const tree = buildTree();
    const service = new LCAService(tree);
    const processor = new LCAQueryProcessor(service);

    processor.on("queryCompleted", (event) => {
        console.log(
            `LCA(${event.first}, ${event.second}) = ${event.ancestor} ` +
            `[${event.strategy}]`
        );
    });

    processor.on("queryError", (error) => {
        console.error("Query rejected:", error.message);
    });

    runTests();

    console.log("\nInteractive query simulation:");

    processor.process(4, 5, "recursive");
    processor.process(8, 10, "parent");
    processor.process(8, 9, "iterative");
    processor.process(4, 100, "recursive");

    const index = new BinaryLiftingIndex(tree);

    console.log("\nRepeated-query binary lifting:");

    for (const [a, b] of [[4, 6], [8, 9], [7, 10]]) {
        const result = index.query(
            tree.getNode(a),
            tree.getNode(b)
        );

        console.log(`LCA(${a}, ${b}) = ${result?.value ?? "Not found"}`);
    }

    console.log(`\nSuccessful queries: ${processor.queryCount}`);
}

main();
