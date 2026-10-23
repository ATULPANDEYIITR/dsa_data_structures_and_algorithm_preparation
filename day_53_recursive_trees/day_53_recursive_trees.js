"use strict";

/*
 * Recursive-tree visualizer for:
 *   Fibonacci
 *   Subsets
 *   Binary choices
 *   Divide-and-conquer merge sort
 *
 * Run with:
 *   node recursive_trees.js
 */

class TreeNode {
    constructor(label) {
        this.label = label;
        this.children = [];
    }

    addChild(child) {
        if (!(child instanceof TreeNode)) {
            throw new TypeError("child must be a TreeNode");
        }
        this.children.push(child);
        return this;
    }
}

function fibonacciTree(n) {
    validateInteger(n, "n", 0);

    const node = new TreeNode(`fib(${n})`);

    if (n <= 1) {
        return node;
    }

    node.addChild(fibonacciTree(n - 1));
    node.addChild(fibonacciTree(n - 2));
    return node;
}

function subsetTree(items) {
    if (!Array.isArray(items)) {
        throw new TypeError("items must be an array");
    }

    function build(index, selected) {
        if (index === items.length) {
            return new TreeNode(
                `subset {${selected.join(", ")}}`
            );
        }

        const item = items[index];
        const node = new TreeNode(`item=${item}`);

        const exclude = build(index + 1, selected);
        exclude.label = `exclude ${item} -> ${exclude.label}`;

        const include = build(index + 1, [...selected, item]);
        include.label = `include ${item} -> ${include.label}`;

        node.addChild(exclude);
        node.addChild(include);

        return node;
    }

    return build(0, []);
}

function binaryChoiceTree(depth) {
    validateInteger(depth, "depth", 0);

    function build(level, choices) {
        const node = new TreeNode(
            `level=${level}, choices=${choices || "∅"}`
        );

        if (level === depth) {
            return node;
        }

        node.addChild(build(level + 1, choices + "0"));
        node.addChild(build(level + 1, choices + "1"));

        return node;
    }

    return build(0, "");
}

function mergeSortTree(values) {
    if (!Array.isArray(values)) {
        throw new TypeError("values must be an array");
    }

    if (!values.every(Number.isInteger)) {
        throw new TypeError("all values must be integers");
    }

    function build(data) {
        const node = new TreeNode(`sort([${data.join(", ")}])`);

        if (data.length <= 1) {
            return node;
        }

        const midpoint = Math.floor(data.length / 2);
        const left = data.slice(0, midpoint);
        const right = data.slice(midpoint);

        node.addChild(build(left));
        node.addChild(build(right));

        return node;
    }

    return build(values);
}

function printTree(root, prefix = "", isLast = true) {
    const connector = isLast ? "└── " : "├── ";
    console.log(prefix + connector + root.label);

    const childPrefix = prefix + (isLast ? "    " : "│   ");

    root.children.forEach((child, index) => {
        printTree(
            child,
            childPrefix,
            index === root.children.length - 1
        );
    });
}

function countNodes(root) {
    return 1 + root.children.reduce(
        (total, child) => total + countNodes(child),
        0
    );
}

function treeHeight(root) {
    if (root.children.length === 0) {
        return 1;
    }

    return 1 + Math.max(
        ...root.children.map(treeHeight)
    );
}

function fibonacci(n) {
    validateInteger(n, "n", 0);

    let previous = 0;
    let current = 1;

    for (let i = 0; i < n; i += 1) {
        [previous, current] = [current, previous + current];
    }

    return previous;
}

function generateSubsets(items) {
    if (!Array.isArray(items)) {
        throw new TypeError("items must be an array");
    }

    const result = [];

    function generate(index, selected) {
        if (index === items.length) {
            result.push([...selected]);
            return;
        }

        generate(index + 1, selected);
        selected.push(items[index]);
        generate(index + 1, selected);
        selected.pop();
    }

    generate(0, []);
    return result;
}

function validateInteger(value, name, minimum) {
    if (!Number.isSafeInteger(value)) {
        throw new TypeError(`${name} must be a safe integer`);
    }

    if (value < minimum) {
        throw new RangeError(
            `${name} must be at least ${minimum}`
        );
    }
}

function main() {
    console.log("FIBONACCI RECURSION TREE");
    const fib = fibonacciTree(5);
    printTree(fib);
    console.log(`Recursive calls: ${countNodes(fib)}`);
    console.log(`Tree height: ${treeHeight(fib)}`);
    console.log(`Fibonacci(5): ${fibonacci(5)}`);

    console.log("\nSUBSET RECURSION TREE");
    const subsets = subsetTree(["A", "B", "C"]);
    printTree(subsets);
    console.log(
        `Generated subsets: ${generateSubsets(["A", "B", "C"]).length}`
    );

    console.log("\nBINARY CHOICE RECURSION TREE");
    const binary = binaryChoiceTree(3);
    printTree(binary);
    console.log("Leaf choices: 8");

    console.log("\nDIVIDE-AND-CONQUER RECURSION TREE");
    const merge = mergeSortTree([8, 3, 7, 4, 2, 6]);
    printTree(merge);
    console.log(`Recursive calls: ${countNodes(merge)}`);
    console.log(`Tree height: ${treeHeight(merge)}`);
}

main();
