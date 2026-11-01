"use strict";

const { EventEmitter } = require("node:events");
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");

/**
 * Binary tree node.
 */
class TreeNode {
    constructor(value) {
        if (!Number.isSafeInteger(value)) {
            throw new TypeError("Node values must be safe integers.");
        }

        this.value = value;
        this.left = null;
        this.right = null;
    }
}

/**
 * Event-driven BFS engine.
 *
 * Events:
 *   levelStart: beginning of a tree level
 *   visit: individual node processing
 *   levelEnd: completion of a level
 *   complete: traversal completion
 */
class BFSProcessor extends EventEmitter {
    constructor() {
        super();
        this.running = false;
    }

    static fromLevelOrder(values) {
        if (!Array.isArray(values)) {
            throw new TypeError("Expected an array.");
        }

        if (values.some(
            value => value !== null &&
                (!Number.isSafeInteger(value))
        )) {
            throw new TypeError("Values must be safe integers or null.");
        }

        if (values.length === 0) {
            return null;
        }

        if (values[0] === null) {
            if (values.slice(1).some(value => value !== null)) {
                throw new Error("A tree cannot have descendants without a root.");
            }
            return null;
        }

        const root = new TreeNode(values[0]);
        const queue = [root];
        let head = 0;
        let index = 1;

        while (head < queue.length && index < values.length) {
            const node = queue[head++];

            if (index < values.length) {
                const value = values[index++];

                if (value !== null) {
                    node.left = new TreeNode(value);
                    queue.push(node.left);
                }
            }

            if (index < values.length) {
                const value = values[index++];

                if (value !== null) {
                    node.right = new TreeNode(value);
                    queue.push(node.right);
                }
            }
        }

        if (index < values.length) {
            throw new Error("Invalid level-order representation.");
        }

        return root;
    }

    /**
     * Asynchronous level-by-level traversal.
     * A head index avoids the O(n) cost of Array.shift().
     */
    async traverse(root, options = {}) {
        if (this.running) {
            throw new Error("A traversal is already running.");
        }

        const {
            delay = 0,
            signal = undefined,
            stopWhen = undefined
        } = options;

        if (!Number.isFinite(delay) || delay < 0) {
            throw new RangeError("Delay must be a non-negative number.");
        }

        if (stopWhen !== undefined && typeof stopWhen !== "function") {
            throw new TypeError("stopWhen must be a function.");
        }

        if (signal?.aborted) {
            throw new Error("Traversal was cancelled.");
        }

        if (root === null) {
            this.emit("complete", []);
            return [];
        }

        this.running = true;
        const result = [];
        const queue = [root];
        let head = 0;
        let depth = 0;

        try {
            while (head < queue.length) {
                if (signal?.aborted) {
                    throw new Error("Traversal was cancelled.");
                }

                const levelSize = queue.length - head;
                const level = [];

                this.emit("levelStart", {
                    depth,
                    expectedNodes: levelSize
                });

                for (let i = 0; i < levelSize; i++) {
                    if (signal?.aborted) {
                        throw new Error("Traversal was cancelled.");
                    }

                    const node = queue[head++];
                    level.push(node.value);

                    this.emit("visit", {
                        depth,
                        value: node.value
                    });

                    if (stopWhen?.(node)) {
                        result.push(level);
                        this.emit("complete", result);
                        return result;
                    }

                    if (node.left) queue.push(node.left);
                    if (node.right) queue.push(node.right);
                }

                result.push(level);

                this.emit("levelEnd", {
                    depth,
                    values: [...level]
                });

                depth++;

                if (delay > 0) {
                    await new Promise(resolve =>
                        setTimeout(resolve, delay)
                    );
                }
            }

            this.emit("complete", result);
            return result;
        } catch (error) {
            this.emit("errorOccurred", error);
            throw error;
        } finally {
            this.running = false;
        }
    }
}

class TreeAnalytics {
    static averages(levels) {
        return levels.map(level => {
            if (level.length === 0) {
                return null;
            }

            return level.reduce((sum, value) => sum + value, 0)
                / level.length;
        });
    }

    static zigzag(levels) {
        return levels.map((level, index) =>
            index % 2 === 0
                ? [...level]
                : [...level].reverse()
        );
    }

    static statistics(levels) {
        return levels.map((level, depth) => {
            const sum = level.reduce((total, value) => total + value, 0);

            return {
                depth,
                count: level.length,
                minimum: Math.min(...level),
                maximum: Math.max(...level),
                average: sum / level.length,
                sum
            };
        });
    }

    static rightSideView(levels) {
        return levels
            .filter(level => level.length > 0)
            .map(level => level[level.length - 1]);
    }

    static bottomUp(levels) {
        return [...levels].reverse().map(level => [...level]);
    }

    static flatten(levels) {
        return levels.flat();
    }
}

class RepositoryTreeMonitor {
    constructor() {
        this.processor = new BFSProcessor();
        this.audit = [];

        this.processor.on("levelStart", event => {
            this.audit.push({
                type: "LEVEL_START",
                ...event
            });
        });

        this.processor.on("visit", event => {
            this.audit.push({
                type: "NODE_VISITED",
                ...event
            });
        });

        this.processor.on("levelEnd", event => {
            this.audit.push({
                type: "LEVEL_END",
                ...event
            });
        });
    }

    async analyze(root, signal) {
        const levels = await this.processor.traverse(root, {
            signal
        });

        return {
            levels,
            averages: TreeAnalytics.averages(levels),
            zigzag: TreeAnalytics.zigzag(levels),
            statistics: TreeAnalytics.statistics(levels),
            rightSideView: TreeAnalytics.rightSideView(levels),
            audit: [...this.audit]
        };
    }

    async saveAudit(filePath) {
        // Use restrictive file permissions for locally stored audit data.
        await fs.writeFile(
            filePath,
            JSON.stringify(this.audit, null, 2),
            { encoding: "utf8", mode: 0o600 }
        );
    }
}

async function runTests() {
    const root = BFSProcessor.fromLevelOrder([
        10, 20, 30, 40, 50, 60, 70
    ]);

    const monitor = new RepositoryTreeMonitor();
    const report = await monitor.analyze(root);

    assert.deepEqual(report.levels, [
        [10],
        [20, 30],
        [40, 50, 60, 70]
    ]);

    assert.deepEqual(report.zigzag, [
        [10],
        [30, 20],
        [40, 50, 60, 70]
    ]);

    assert.deepEqual(report.rightSideView, [10, 30, 70]);
    assert.deepEqual(report.averages, [10, 25, 55]);

    assert.equal(report.audit.filter(
        entry => entry.type === "NODE_VISITED"
    ).length, 7);

    const empty = await monitor.processor.traverse(null);
    assert.deepEqual(empty, []);

    assert.throws(
        () => BFSProcessor.fromLevelOrder([null, 10]),
        /descendants/
    );

    assert.throws(
        () => BFSProcessor.fromLevelOrder([1, "invalid"]),
        /safe integers/
    );

    const stoppingProcessor = new BFSProcessor();
    const partial = await stoppingProcessor.traverse(root, {
        stopWhen: node => node.value === 30
    });

    assert.deepEqual(partial, [[10], [20, 30]]);

    console.log("All JavaScript tests passed.");
    console.log("\nBFS LEVEL REPORT");
    console.log(JSON.stringify(report, null, 2));
}

runTests().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
