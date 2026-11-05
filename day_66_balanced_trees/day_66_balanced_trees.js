"use strict";

const { EventEmitter } = require("node:events");

class TreeInputError extends Error {
    constructor(message) {
        super(message);
        this.name = "TreeInputError";
    }
}

class TreeNode {
    constructor(key) {
        this.key = key;
        this.left = null;
        this.right = null;
        this.height = 1;
    }
}

class AVLTree extends EventEmitter {
    constructor() {
        super();
        this.root = null;
        this.size = 0;
        this.version = 0;
    }

    static validateKey(key) {
        if (!Number.isSafeInteger(key)) {
            throw new TreeInputError(
                "Tree keys must be safe integers."
            );
        }
    }

    height(node) {
        return node ? node.height : 0;
    }

    balance(node) {
        return node
            ? this.height(node.left) - this.height(node.right)
            : 0;
    }

    update(node) {
        node.height =
            1 + Math.max(
                this.height(node.left),
                this.height(node.right)
            );
    }

    rotateRight(y) {
        const x = y.left;

        if (!x) {
            throw new Error("Invalid right rotation.");
        }

        const middle = x.right;
        x.right = y;
        y.left = middle;

        this.update(y);
        this.update(x);

        return x;
    }

    rotateLeft(x) {
        const y = x.right;

        if (!y) {
            throw new Error("Invalid left rotation.");
        }

        const middle = y.left;
        y.left = x;
        x.right = middle;

        this.update(x);
        this.update(y);

        return y;
    }

    rebalance(node) {
        this.update(node);

        const factor = this.balance(node);

        if (factor > 1) {
            if (this.balance(node.left) < 0) {
                node.left = this.rotateLeft(node.left);
            }
            return this.rotateRight(node);
        }

        if (factor < -1) {
            if (this.balance(node.right) > 0) {
                node.right = this.rotateRight(node.right);
            }
            return this.rotateLeft(node);
        }

        return node;
    }

    insert(key) {
        AVLTree.validateKey(key);

        let inserted = false;

        const visit = (node) => {
            if (!node) {
                inserted = true;
                return new TreeNode(key);
            }

            if (key === node.key) {
                return node;
            }

            if (key < node.key) {
                node.left = visit(node.left);
            } else {
                node.right = visit(node.right);
            }

            return inserted ? this.rebalance(node) : node;
        };

        this.root = visit(this.root);

        if (inserted) {
            this.size++;
            this.version++;

            this.emit("insert", {
                key,
                version: this.version,
                height: this.height(this.root)
            });
        }

        return inserted;
    }

    search(key) {
        AVLTree.validateKey(key);

        let current = this.root;
        let comparisons = 0;

        while (current) {
            comparisons++;

            if (key === current.key) {
                return {
                    found: true,
                    comparisons
                };
            }

            current = key < current.key
                ? current.left
                : current.right;
        }

        return {
            found: false,
            comparisons
        };
    }

    delete(key) {
        AVLTree.validateKey(key);

        let deleted = false;

        const remove = (node, target) => {
            if (!node) return null;

            if (target < node.key) {
                node.left = remove(node.left, target);
            } else if (target > node.key) {
                node.right = remove(node.right, target);
            } else {
                deleted = true;

                if (!node.left) return node.right;
                if (!node.right) return node.left;

                let successor = node.right;

                while (successor.left) {
                    successor = successor.left;
                }

                node.key = successor.key;
                node.right = remove(node.right, successor.key);
            }

            return deleted ? this.rebalance(node) : node;
        };

        this.root = remove(this.root, key);

        if (deleted) {
            this.size--;
            this.version++;

            this.emit("delete", {
                key,
                version: this.version
            });
        }

        return deleted;
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

    inspect() {
        const inspectNode = (node, min, max) => {
            if (!node) {
                return {
                    height: 0,
                    count: 0
                };
            }

            if (
                (min !== null && node.key <= min) ||
                (max !== null && node.key >= max)
            ) {
                throw new Error("BST ordering violation.");
            }

            const left = inspectNode(node.left, min, node.key);
            const right = inspectNode(node.right, node.key, max);

            const expectedHeight =
                1 + Math.max(left.height, right.height);

            if (node.height !== expectedHeight) {
                throw new Error("Stored height is incorrect.");
            }

            if (Math.abs(left.height - right.height) > 1) {
                throw new Error("AVL balance violation.");
            }

            return {
                height: expectedHeight,
                count: left.count + right.count + 1
            };
        };

        const result = inspectNode(this.root, null, null);

        if (result.count !== this.size) {
            throw new Error("Node count mismatch.");
        }

        return {
            valid: true,
            balanced: true,
            height: result.height,
            nodes: result.count
        };
    }
}

class UnbalancedBST {
    constructor() {
        this.root = null;
        this.size = 0;
    }

    insert(key) {
        AVLTree.validateKey(key);

        if (!this.root) {
            this.root = new TreeNode(key);
            this.size++;
            return;
        }

        let current = this.root;

        while (true) {
            if (key === current.key) return;

            const direction = key < current.key
                ? "left"
                : "right";

            if (!current[direction]) {
                current[direction] = new TreeNode(key);
                this.size++;
                return;
            }

            current = current[direction];
        }
    }

    search(key) {
        AVLTree.validateKey(key);

        let current = this.root;
        let comparisons = 0;

        while (current) {
            comparisons++;

            if (key === current.key) {
                return { found: true, comparisons };
            }

            current = key < current.key
                ? current.left
                : current.right;
        }

        return { found: false, comparisons };
    }

    height() {
        if (!this.root) return 0;

        const stack = [[this.root, 1]];
        let maximum = 0;

        while (stack.length) {
            const [node, depth] = stack.pop();
            maximum = Math.max(maximum, depth);

            if (node.left) stack.push([node.left, depth + 1]);
            if (node.right) stack.push([node.right, depth + 1]);
        }

        return maximum;
    }
}

async function processInsertions(tree, keys) {
    // Asynchronous interface allows insertion jobs to be integrated
    // into a larger event-driven application.
    for (const key of keys) {
        await Promise.resolve();
        tree.insert(key);
    }
}

async function main() {
    const avl = new AVLTree();

    avl.on("insert", (event) => {
        console.log(
            `Inserted ${event.key}; version=${event.version}`
        );
    });

    avl.on("delete", (event) => {
        console.log(`Deleted ${event.key}`);
    });

    await processInsertions(
        avl,
        [50, 30, 70, 20, 40, 60, 80, 10, 25]
    );

    console.log("\nAVL inorder:", avl.inorder());
    console.log("AVL inspection:", avl.inspect());
    console.log("Search 60:", avl.search(60));

    avl.delete(50);

    console.log("After deletion:", avl.inorder());
    console.log("After deletion validation:", avl.inspect());

    // Sorted input creates a chain in an ordinary BST.
    const ordinary = new UnbalancedBST();

    for (let i = 1; i <= 100; i++) {
        ordinary.insert(i);
    }

    console.log("\nORDINARY BST");
    console.log("Nodes:", ordinary.size);
    console.log("Height:", ordinary.height());
    console.log("Search 100:", ordinary.search(100));

    console.log("\nPERFORMANCE COMPARISON");
    console.log("AVL height:", avl.inspect().height);
    console.log("Ordinary BST height:", ordinary.height());

    // Edge cases.
    const empty = new AVLTree();

    console.assert(empty.inspect().height === 0);
    console.assert(empty.delete(10) === false);

    const single = new AVLTree();
    single.insert(10);
    single.insert(10);

    console.assert(single.size === 1);
    console.assert(single.delete(10) === true);
    console.assert(single.size === 0);

    try {
        avl.insert(Number.MAX_SAFE_INTEGER + 1);
    } catch (error) {
        console.log("\nExpected validation error:", error.message);
    }

    console.log("\nAll checks completed.");
}

main().catch((error) => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
