"use strict";

/*
 * Tree assessment using iterative algorithms.
 * Height and diameter are measured in edges.
 * Empty tree height = -1 and diameter = 0.
 */

class TreeNode {
    constructor(value, left = null, right = null) {
        if (!Number.isSafeInteger(value)) {
            throw new TypeError("Node value must be a safe integer.");
        }

        this.value = value;
        this.left = left;
        this.right = right;
    }
}

class TreeAssessment {
    constructor(root = null) {
        this.root = root;
        this.validate();
    }

    validate() {
        if (!this.root) return;

        const visited = new WeakSet();
        const stack = [{ node: this.root, exit: false }];

        while (stack.length) {
            const { node, exit } = stack.pop();

            if (!node || exit) continue;

            if (typeof node !== "object" ||
                !Number.isSafeInteger(node.value)) {
                throw new TypeError("Invalid tree node.");
            }

            if (visited.has(node)) {
                throw new Error("Cycle or shared child detected.");
            }

            visited.add(node);

            stack.push({ node: node.right, exit: false });
            stack.push({ node: node.left, exit: false });
        }
    }

    *depthFirst(order = "preorder") {
        if (!["preorder", "inorder", "postorder"].includes(order)) {
            throw new RangeError("Unsupported traversal order.");
        }

        if (!this.root) return;

        if (order === "inorder") {
            const stack = [];
            let current = this.root;

            while (current || stack.length) {
                while (current) {
                    stack.push(current);
                    current = current.left;
                }

                current = stack.pop();
                yield current.value;
                current = current.right;
            }

            return;
        }

        const stack = [{ node: this.root, visited: false }];

        while (stack.length) {
            const { node, visited } = stack.pop();

            if (!node) continue;

            if (visited) {
                yield node.value;
                continue;
            }

            if (order === "preorder") {
                yield node.value;
                stack.push({ node: node.right, visited: false });
                stack.push({ node: node.left, visited: false });
            } else {
                stack.push({ node, visited: true });
                stack.push({ node: node.right, visited: false });
                stack.push({ node: node.left, visited: false });
            }
        }
    }

    preorder() {
        return [...this.depthFirst("preorder")];
    }

    inorder() {
        return [...this.depthFirst("inorder")];
    }

    postorder() {
        return [...this.depthFirst("postorder")];
    }

    levelOrder() {
        if (!this.root) return [];

        const queue = [this.root];
        let head = 0;
        const result = [];

        while (head < queue.length) {
            const end = queue.length;
            const level = [];

            while (head < end) {
                const node = queue[head++];
                level.push(node.value);

                if (node.left) queue.push(node.left);
                if (node.right) queue.push(node.right);
            }

            result.push(level);
        }

        return result;
    }

    async *levelOrderEvents() {
        if (!this.root) return;

        const queue = [this.root];
        let head = 0;
        let levelNumber = 0;

        while (head < queue.length) {
            const end = queue.length;
            const values = [];

            while (head < end) {
                const node = queue[head++];
                values.push(node.value);

                if (node.left) queue.push(node.left);
                if (node.right) queue.push(node.right);
            }

            yield {
                level: levelNumber++,
                values
            };

            // Allows asynchronous consumers to process each level.
            await Promise.resolve();
        }
    }

    height() {
        if (!this.root) return -1;

        let maximum = 0;
        const queue = [[this.root, 0]];
        let head = 0;

        while (head < queue.length) {
            const [node, depth] = queue[head++];
            maximum = Math.max(maximum, depth);

            if (node.left) {
                queue.push([node.left, depth + 1]);
            }

            if (node.right) {
                queue.push([node.right, depth + 1]);
            }
        }

        return maximum;
    }

    diameter() {
        if (!this.root) return 0;

        let diameter = 0;
        const heights = new Map();
        const stack = [[this.root, false]];

        while (stack.length) {
            const [node, visited] = stack.pop();

            if (!node) continue;

            if (!visited) {
                stack.push([node, true]);
                stack.push([node.right, false]);
                stack.push([node.left, false]);
            } else {
                const left = node.left
                    ? heights.get(node.left) : -1;

                const right = node.right
                    ? heights.get(node.right) : -1;

                diameter = Math.max(
                    diameter,
                    left + right + 2
                );

                heights.set(
                    node,
                    Math.max(left, right) + 1
                );
            }
        }

        return diameter;
    }

    isBalanced() {
        if (!this.root) return true;

        const heights = new Map();
        const stack = [[this.root, false]];

        while (stack.length) {
            const [node, visited] = stack.pop();

            if (!node) continue;

            if (!visited) {
                stack.push([node, true]);
                stack.push([node.right, false]);
                stack.push([node.left, false]);
            } else {
                const left = node.left
                    ? heights.get(node.left) : 0;

                const right = node.right
                    ? heights.get(node.right) : 0;

                if (Math.abs(left - right) > 1) {
                    return false;
                }

                heights.set(node, Math.max(left, right) + 1);
            }
        }

        return true;
    }

    hasPathSum(target) {
        if (!Number.isSafeInteger(target)) {
            throw new TypeError("Target must be a safe integer.");
        }

        if (!this.root) return false;

        const stack = [[this.root, this.root.value]];

        while (stack.length) {
            const [node, sum] = stack.pop();

            if (!node.left && !node.right && sum === target) {
                return true;
            }

            if (node.right) {
                stack.push([
                    node.right,
                    sum + node.right.value
                ]);
            }

            if (node.left) {
                stack.push([
                    node.left,
                    sum + node.left.value
                ]);
            }
        }

        return false;
    }

    allPathSums(target) {
        if (!Number.isSafeInteger(target)) {
            throw new TypeError("Target must be a safe integer.");
        }

        const result = [];
        const path = [];

        const search = (node, remaining) => {
            if (!node) return;

            path.push(node.value);
            remaining -= node.value;

            if (!node.left && !node.right) {
                if (remaining === 0) {
                    result.push([...path]);
                }
            } else {
                search(node.left, remaining);
                search(node.right, remaining);
            }

            path.pop();
        };

        search(this.root, target);
        return result;
    }

    lowestCommonAncestor(first, second) {
        const parent = new Map();

        if (!this.root) return null;

        parent.set(this.root, null);

        const queue = [this.root];
        let head = 0;
        const found = new Set();

        while (head < queue.length && found.size < 2) {
            const node = queue[head++];

            if (node.value === first) found.add(first);
            if (node.value === second) found.add(second);

            for (const child of [node.left, node.right]) {
                if (child) {
                    parent.set(child, node);
                    queue.push(child);
                }
            }
        }

        if (found.size !== 2) return null;

        const ancestors = new Set();
        let current = queue.find(node => node.value === first);

        while (current) {
            ancestors.add(current);
            current = parent.get(current);
        }

        current = queue.find(node => node.value === second);

        while (current) {
            if (ancestors.has(current)) return current;
            current = parent.get(current);
        }

        return null;
    }

    rightSideView() {
        return this.levelOrder().map(level => level[level.length - 1]);
    }

    maximumPathSum() {
        if (!this.root) return null;

        let maximum = -Infinity;
        const gains = new Map();
        const stack = [[this.root, false]];

        while (stack.length) {
            const [node, visited] = stack.pop();

            if (!node) continue;

            if (!visited) {
                stack.push([node, true]);
                stack.push([node.right, false]);
                stack.push([node.left, false]);
            } else {
                const left = Math.max(
                    0,
                    node.left ? gains.get(node.left) : 0
                );

                const right = Math.max(
                    0,
                    node.right ? gains.get(node.right) : 0
                );

                maximum = Math.max(
                    maximum,
                    node.value + left + right
                );

                gains.set(
                    node,
                    node.value + Math.max(left, right)
                );
            }
        }

        return maximum;
    }

    minimumDepth() {
        if (!this.root) return 0;

        const queue = [[this.root, 1]];
        let head = 0;

        while (head < queue.length) {
            const [node, depth] = queue[head++];

            if (!node.left && !node.right) return depth;

            if (node.left) {
                queue.push([node.left, depth + 1]);
            }

            if (node.right) {
                queue.push([node.right, depth + 1]);
            }
        }

        return 0;
    }
}

async function main() {
    const root = new TreeNode(
        10,
        new TreeNode(
            5,
            new TreeNode(3, new TreeNode(1), new TreeNode(4)),
            new TreeNode(7, null, new TreeNode(8))
        ),
        new TreeNode(15, null, new TreeNode(20))
    );

    const tree = new TreeAssessment(root);

    console.log("PREORDER:", tree.preorder());
    console.log("INORDER:", tree.inorder());
    console.log("POSTORDER:", tree.postorder());
    console.log("LEVEL ORDER:", tree.levelOrder());
    console.log("HEIGHT:", tree.height());
    console.log("DIAMETER:", tree.diameter());
    console.log("BALANCED:", tree.isBalanced());
    console.log("PATH SUM 19:", tree.hasPathSum(19));
    console.log("MATCHING PATHS:", tree.allPathSums(19));
    console.log("LCA 1, 8:", tree.lowestCommonAncestor(1, 8)?.value);
    console.log("RIGHT VIEW:", tree.rightSideView());
    console.log("MAXIMUM PATH SUM:", tree.maximumPathSum());
    console.log("MINIMUM DEPTH:", tree.minimumDepth());

    console.log("\nASYNC LEVEL EVENTS");

    for await (const event of tree.levelOrderEvents()) {
        console.log(event);
    }

    const empty = new TreeAssessment();

    console.assert(empty.height() === -1);
    console.assert(empty.diameter() === 0);
    console.assert(empty.isBalanced());
    console.assert(empty.maximumPathSum() === null);

    const negative = new TreeAssessment(new TreeNode(-5));
    console.assert(negative.maximumPathSum() === -5);
    console.assert(negative.hasPathSum(-5));

    const unbalanced = new TreeAssessment(
        new TreeNode(1,
            new TreeNode(2,
                new TreeNode(3,
                    new TreeNode(4)
                )
            )
        )
    );

    console.assert(!unbalanced.isBalanced());

    const shared = new TreeNode(2);

    try {
        new TreeAssessment(new TreeNode(1, shared, shared));
        throw new Error("Shared-child validation failed.");
    } catch (error) {
        console.assert(error.message.includes("shared child"));
    }

    console.log("\nAll JavaScript tree tests passed.");
}

main().catch(error => {
    console.error("Tree assessment failed:", error.message);
    process.exitCode = 1;
});
