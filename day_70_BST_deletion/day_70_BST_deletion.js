"use strict";

/*
 * Binary Search Tree Deletion
 * Node.js 18+
 *
 * Event-driven implementation with:
 * - Map-backed node registry
 * - Unique integer keys
 * - Leaf, one-child and two-child deletion
 * - Successor and predecessor
 * - Parent-aware node replacement
 * - Mutation events
 * - Structural integrity checks
 */

const { EventEmitter } = require("node:events");

class BSTNode {
    constructor(key) {
        this.key = key;
        this.left = null;
        this.right = null;
        this.parent = null;
    }
}

class BinarySearchTree extends EventEmitter {
    constructor() {
        super();
        this.root = null;
        this.nodes = new Map();
    }

    static validateKey(key) {
        if (!Number.isSafeInteger(key)) {
            throw new TypeError("Key must be a safe integer.");
        }
    }

    get size() {
        return this.nodes.size;
    }

    insert(key) {
        BinarySearchTree.validateKey(key);

        if (this.nodes.has(key)) {
            return false;
        }

        const node = new BSTNode(key);

        if (!this.root) {
            this.root = node;
        } else {
            let current = this.root;

            while (true) {
                if (key < current.key) {
                    if (!current.left) {
                        current.left = node;
                        node.parent = current;
                        break;
                    }
                    current = current.left;
                } else {
                    if (!current.right) {
                        current.right = node;
                        node.parent = current;
                        break;
                    }
                    current = current.right;
                }
            }
        }

        this.nodes.set(key, node);
        this.emit("inserted", { key });
        return true;
    }

    search(key) {
        BinarySearchTree.validateKey(key);
        return this.nodes.get(key) ?? null;
    }

    minimum(node) {
        if (!node) return null;

        while (node.left) {
            node = node.left;
        }

        return node;
    }

    maximum(node) {
        if (!node) return null;

        while (node.right) {
            node = node.right;
        }

        return node;
    }

    successor(key) {
        BinarySearchTree.validateKey(key);

        const node = this.search(key);
        if (!node) return null;

        if (node.right) {
            return this.minimum(node.right).key;
        }

        let current = node;
        let parent = current.parent;

        while (parent && current === parent.right) {
            current = parent;
            parent = parent.parent;
        }

        return parent ? parent.key : null;
    }

    predecessor(key) {
        BinarySearchTree.validateKey(key);

        const node = this.search(key);
        if (!node) return null;

        if (node.left) {
            return this.maximum(node.left).key;
        }

        let current = node;
        let parent = current.parent;

        while (parent && current === parent.left) {
            current = parent;
            parent = parent.parent;
        }

        return parent ? parent.key : null;
    }

    /*
     * Replace one subtree with another.
     * Parent pointers are updated together with child pointers.
     */
    transplant(oldNode, newNode) {
        if (!oldNode.parent) {
            this.root = newNode;
        } else if (oldNode === oldNode.parent.left) {
            oldNode.parent.left = newNode;
        } else {
            oldNode.parent.right = newNode;
        }

        if (newNode) {
            newNode.parent = oldNode.parent;
        }
    }

    delete(key) {
        BinarySearchTree.validateKey(key);

        const node = this.search(key);

        if (!node) {
            this.emit("notFound", { key });
            return false;
        }

        let deletionCase;

        // Case 1: Leaf.
        if (!node.left && !node.right) {
            deletionCase = "leaf";
            this.transplant(node, null);
        }

        // Case 2: Only right child.
        else if (!node.left) {
            deletionCase = "one-child";
            this.transplant(node, node.right);
        }

        // Case 2: Only left child.
        else if (!node.right) {
            deletionCase = "one-child";
            this.transplant(node, node.left);
        }

        // Case 3: Two children.
        else {
            deletionCase = "two-children";

            const successor = this.minimum(node.right);

            if (successor.parent !== node) {
                this.transplant(successor, successor.right);
                successor.right = node.right;
                successor.right.parent = successor;
            }

            this.transplant(node, successor);

            successor.left = node.left;
            successor.left.parent = successor;
        }

        this.nodes.delete(key);

        // Detach the removed object to avoid retaining stale links.
        node.left = null;
        node.right = null;
        node.parent = null;

        this.emit("deleted", {
            key,
            deletionCase,
            size: this.size
        });

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

    preorder() {
        if (!this.root) return [];

        const result = [];
        const stack = [this.root];

        while (stack.length) {
            const node = stack.pop();
            result.push(node.key);

            if (node.right) stack.push(node.right);
            if (node.left) stack.push(node.left);
        }

        return result;
    }

    levelOrder() {
        if (!this.root) return [];

        const result = [];
        const queue = [this.root];

        for (let index = 0; index < queue.length;) {
            const levelSize = queue.length - index;
            const level = [];

            for (let i = 0; i < levelSize; i++) {
                const node = queue[index++];
                level.push(node.key);

                if (node.left) queue.push(node.left);
                if (node.right) queue.push(node.right);
            }

            result.push(level);
        }

        return result;
    }

    validate() {
        if (!this.root) {
            return this.nodes.size === 0;
        }

        if (this.root.parent !== null) return false;

        const visited = new Set();
        const stack = [{
            node: this.root,
            lower: null,
            upper: null,
            parent: null
        }];

        while (stack.length) {
            const item = stack.pop();
            const { node, lower, upper, parent } = item;

            if (visited.has(node)) return false;
            visited.add(node);

            if (node.parent !== parent) return false;

            if (lower !== null && node.key <= lower) return false;
            if (upper !== null && node.key >= upper) return false;

            if (this.nodes.get(node.key) !== node) return false;

            if (node.left) {
                stack.push({
                    node: node.left,
                    lower,
                    upper: node.key,
                    parent: node
                });
            }

            if (node.right) {
                stack.push({
                    node: node.right,
                    lower: node.key,
                    upper,
                    parent: node
                });
            }
        }

        return visited.size === this.nodes.size;
    }

    clear() {
        const removed = this.size;
        this.root = null;
        this.nodes.clear();
        this.emit("cleared", { removed });
    }
}

async function executeWorkflow() {
    const tree = new BinarySearchTree();

    tree.on("inserted", event => {
        console.log("INSERT:", event.key);
    });

    tree.on("deleted", event => {
        console.log(
            `DELETE: ${event.key}, case=${event.deletionCase}, ` +
            `remaining=${event.size}`
        );
    });

    tree.on("notFound", event => {
        console.log("NOT FOUND:", event.key);
    });

    const values = [50, 30, 70, 20, 40, 60, 80, 35, 45, 65];

    // Promise-based workflow allows independent insertion tasks.
    await Promise.all(
        values.map(key => Promise.resolve().then(() => tree.insert(key)))
    );

    console.log("\nINITIAL INORDER:", tree.inorder());

    console.log(
        "SUCCESSOR OF 50:", tree.successor(50)
    );

    console.log(
        "PREDECESSOR OF 50:", tree.predecessor(50)
    );

    console.log("\nLEAF DELETION");
    console.assert(tree.delete(20));

    console.log("\nONE-CHILD DELETION");
    console.assert(tree.delete(60));

    console.log("\nTWO-CHILD DELETION");
    console.assert(tree.delete(70));

    console.log("\nROOT DELETION");
    console.assert(tree.delete(50));

    console.log("\nFINAL STATE");
    console.log("Inorder:", tree.inorder());
    console.log("Preorder:", tree.preorder());
    console.log("Levels:", tree.levelOrder());
    console.log("Size:", tree.size);
    console.log("Valid:", tree.validate());

    console.assert(tree.validate());
    console.assert(!tree.delete(999));

    // Duplicate handling.
    console.assert(!tree.insert(30));

    // Missing-key queries.
    console.assert(tree.successor(999) === null);
    console.assert(tree.predecessor(999) === null);

    // Empty-tree behavior.
    tree.clear();
    console.assert(tree.size === 0);
    console.assert(tree.validate());
    console.assert(tree.delete(30) === false);

    // Input validation.
    try {
        tree.insert(3.14);
    } catch (error) {
        console.log("VALIDATION:", error.message);
    }

    console.log("\nALL CHECKS COMPLETED.");
}

executeWorkflow().catch(error => {
    console.error("Workflow failure:", error);
    process.exitCode = 1;
});
