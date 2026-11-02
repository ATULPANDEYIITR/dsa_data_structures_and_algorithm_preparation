'use strict';

const fs = require('node:fs/promises');
const path = require('node:path');

class TreeNode {
    constructor(value, left = null, right = null) {
        if (!Number.isInteger(value)) {
            throw new TypeError('Tree node values must be integers.');
        }
        this.value = value;
        this.left = left;
        this.right = right;
    }
}

class TreeValidationError extends Error {}

class BinaryTreeAnalyzer {
    constructor(root) {
        this.root = root;
    }

    static fromLevelOrder(values) {
        if (!Array.isArray(values)) {
            throw new TreeValidationError('Tree input must be an array.');
        }

        if (values.length > 100000) {
            throw new TreeValidationError('Tree input is too large.');
        }

        for (const value of values) {
            if (value !== null && !Number.isInteger(value)) {
                throw new TreeValidationError(
                    'Every value must be an integer or null.'
                );
            }
        }

        if (values.length === 0 || values[0] === null) {
            return null;
        }

        const root = new TreeNode(values[0]);
        const queue = [root];
        let head = 0;
        let index = 1;

        while (head < queue.length && index < values.length) {
            const node = queue[head++];

            if (index < values.length) {
                const left = values[index++];
                if (left !== null) {
                    node.left = new TreeNode(left);
                    queue.push(node.left);
                }
            }

            if (index < values.length) {
                const right = values[index++];
                if (right !== null) {
                    node.right = new TreeNode(right);
                    queue.push(node.right);
                }
            }
        }

        if (index < values.length) {
            throw new TreeValidationError(
                'Input contains nodes that cannot be attached to the tree.'
            );
        }

        return root;
    }

    maximumDepth() {
        const depth = (node) => {
            if (node === null) {
                return 0;
            }
            return 1 + Math.max(depth(node.left), depth(node.right));
        };

        return depth(this.root);
    }

    minimumDepth() {
        if (this.root === null) {
            return 0;
        }

        const queue = [{ node: this.root, depth: 1 }];
        let head = 0;

        while (head < queue.length) {
            const current = queue[head++];
            const { node, depth } = current;

            if (node.left === null && node.right === null) {
                return depth;
            }

            if (node.left !== null) {
                queue.push({ node: node.left, depth: depth + 1 });
            }

            if (node.right !== null) {
                queue.push({ node: node.right, depth: depth + 1 });
            }
        }

        throw new Error('Unable to locate a leaf.');
    }

    countLeaves() {
        if (this.root === null) {
            return 0;
        }

        let count = 0;
        const stack = [this.root];

        while (stack.length > 0) {
            const node = stack.pop();

            if (node.left === null && node.right === null) {
                count++;
                continue;
            }

            if (node.right !== null) {
                stack.push(node.right);
            }

            if (node.left !== null) {
                stack.push(node.left);
            }
        }

        return count;
    }

    isBalanced() {
        const height = (node) => {
            if (node === null) {
                return 0;
            }

            const left = height(node.left);
            if (left === -1) {
                return -1;
            }

            const right = height(node.right);
            if (right === -1) {
                return -1;
            }

            if (Math.abs(left - right) > 1) {
                return -1;
            }

            return 1 + Math.max(left, right);
        };

        return height(this.root) !== -1;
    }

    shortestPath() {
        if (this.root === null) {
            return { depth: 0, path: [] };
        }

        const queue = [{ node: this.root, path: [this.root.value] }];
        let head = 0;

        while (head < queue.length) {
            const current = queue[head++];
            const { node, path } = current;

            if (node.left === null && node.right === null) {
                return {
                    depth: path.length,
                    path
                };
            }

            if (node.left !== null) {
                queue.push({
                    node: node.left,
                    path: [...path, node.left.value]
                });
            }

            if (node.right !== null) {
                queue.push({
                    node: node.right,
                    path: [...path, node.right.value]
                });
            }
        }

        throw new Error('Unable to locate a leaf.');
    }

    analyze() {
        const shortest = this.shortestPath();

        return {
            maximumDepth: this.maximumDepth(),
            minimumDepth: shortest.depth,
            shortestPath: shortest.path,
            leafCount: this.countLeaves(),
            balanced: this.isBalanced()
        };
    }
}

class TreeAnalysisService {
    constructor() {
        this.listeners = new Map();
    }

    on(eventName, listener) {
        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, new Set());
        }
        this.listeners.get(eventName).add(listener);
        return () => this.listeners.get(eventName)?.delete(listener);
    }

    emit(eventName, payload) {
        const listeners = this.listeners.get(eventName) ?? new Set();
        for (const listener of listeners) {
            listener(payload);
        }
    }

    async analyze(values) {
        this.emit('analysis.started', { nodeInputSize: values.length });

        try {
            const root = BinaryTreeAnalyzer.fromLevelOrder(values);
            const result = new BinaryTreeAnalyzer(root).analyze();

            this.emit('analysis.completed', result);
            return result;
        } catch (error) {
            this.emit('analysis.failed', {
                name: error.name,
                message: error.message
            });
            throw error;
        }
    }
}

async function main() {
    const service = new TreeAnalysisService();

    service.on('analysis.started', event => {
        console.log(`Analysis started for ${event.nodeInputSize} input slots.`);
    });

    service.on('analysis.completed', result => {
        console.log(
            `Completed: depth=${result.maximumDepth}, leaves=${result.leafCount}, balanced=${result.balanced}`
        );
    });

    service.on('analysis.failed', error => {
        console.error(`Analysis failed: ${error.name}: ${error.message}`);
    });

    const examples = new Map([
        ['balanced', [3, 9, 20, null, null, 15, 7]],
        ['unbalanced', [1, 2, 2, 3, 3, null, null, 4, 4]],
        ['single', [42]],
        ['skewed', [1, 2, null, 3, null, 4]],
        ['empty', []]
    ]);

    for (const [name, values] of examples) {
        console.log(`\n${name}`);
        const result = await service.analyze(values);
        console.log(JSON.stringify(result, null, 2));
    }

    const productionTree = [
        10, 5, 15, 3, 7, 12, 18,
        1, 4, 6, 8, null, 13, 17, 20
    ];

    const report = await service.analyze(productionTree);

    if (
        report.maximumDepth !== 4 ||
        report.minimumDepth !== 3 ||
        report.leafCount !== 7 ||
        report.balanced !== true
    ) {
        throw new Error('Production assertions failed.');
    }

    const output = path.resolve(process.cwd(), 'tree_analysis_report.json');
    await fs.writeFile(output, JSON.stringify(report, null, 2) + '\n', 'utf8');

    console.log(`\nValidated production example.`);
    console.log(`Report written to: ${output}`);
}

main().catch(error => {
    console.error(error);
    process.exitCode = 1;
});
