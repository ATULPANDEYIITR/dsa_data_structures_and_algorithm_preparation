"use strict";

/*
 * Tree Diameter Practice Project
 *
 * Models a validated organizational hierarchy and calculates:
 * - Rooted tree height
 * - Longest path through every node
 * - Diameter using bottom-up dynamic programming
 * - Diameter using two BFS traversals
 *
 * Distances are measured in edges.
 * Requires Node.js with the standard EventEmitter and setImmediate APIs.
 */

const { EventEmitter } = require("node:events");

class TreeValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "TreeValidationError";
    }
}

class TreeIndex extends EventEmitter {
    constructor(nodes, links) {
        super();

        if (!Array.isArray(nodes) || nodes.length === 0) {
            throw new TreeValidationError(
                "A tree must contain at least one node."
            );
        }

        if (!Array.isArray(links)) {
            throw new TreeValidationError("Links must be supplied as an array.");
        }

        this.nodes = [...nodes];
        this.adjacency = new Map();

        for (const node of this.nodes) {
            if (typeof node !== "string" || node.trim().length === 0) {
                throw new TreeValidationError(
                    "Node identifiers must be non-empty strings."
                );
            }

            if (this.adjacency.has(node)) {
                throw new TreeValidationError(
                    `Duplicate node identifier: ${node}`
                );
            }

            this.adjacency.set(node, new Set());
        }

        for (const link of links) {
            if (
                link === null ||
                typeof link !== "object" ||
                typeof link.from !== "string" ||
                typeof link.to !== "string"
            ) {
                throw new TreeValidationError(
                    "Every link must contain string properties 'from' and 'to'."
                );
            }

            const { from, to } = link;

            if (!this.adjacency.has(from) || !this.adjacency.has(to)) {
                throw new TreeValidationError(
                    `Link references an unknown node: ${from} -> ${to}`
                );
            }

            if (from === to) {
                throw new TreeValidationError("Self-links are not allowed.");
            }

            if (this.adjacency.get(from).has(to)) {
                throw new TreeValidationError(
                    `Duplicate link: ${from} -> ${to}`
                );
            }

            this.adjacency.get(from).add(to);
            this.adjacency.get(to).add(from);
        }

        if (links.length !== nodes.length - 1) {
            throw new TreeValidationError(
                "A valid tree must contain exactly n - 1 links."
            );
        }

        this.validateStructure();
    }

    validateStructure() {
        const start = this.nodes[0];
        const visited = new Set([start]);
        const stack = [{ node: start, parent: null }];

        while (stack.length > 0) {
            const { node, parent } = stack.pop();

            for (const neighbor of this.adjacency.get(node)) {
                if (neighbor === parent) {
                    continue;
                }

                if (visited.has(neighbor)) {
                    throw new TreeValidationError(
                        "The graph contains a cycle."
                    );
                }

                visited.add(neighbor);
                stack.push({ node: neighbor, parent: node });
            }
        }

        if (visited.size !== this.nodes.length) {
            throw new TreeValidationError("The graph is disconnected.");
        }

        this.emit("validated", {
            nodeCount: this.nodes.length,
            edgeCount: this.nodes.length - 1,
        });
    }

    assertNode(node) {
        if (!this.adjacency.has(node)) {
            throw new TreeValidationError(`Unknown node: ${node}`);
        }
    }

    rootedTraversal(root) {
        this.assertNode(root);

        const parent = new Map([[root, null]]);
        const depth = new Map([[root, 0]]);
        const order = [];
        const stack = [root];

        while (stack.length > 0) {
            const current = stack.pop();
            order.push(current);

            for (const neighbor of this.adjacency.get(current)) {
                if (neighbor === parent.get(current)) {
                    continue;
                }

                if (parent.has(neighbor)) {
                    throw new TreeValidationError(
                        "Unexpected cycle during rooted traversal."
                    );
                }

                parent.set(neighbor, current);
                depth.set(neighbor, depth.get(current) + 1);
                stack.push(neighbor);
            }
        }

        if (order.length !== this.nodes.length) {
            throw new TreeValidationError(
                "The selected root cannot reach every node."
            );
        }

        return { parent, depth, order };
    }

    dynamicProgrammingAnalysis(root) {
        const { parent, depth, order } = this.rootedTraversal(root);

        const down = new Map();
        const up = new Map([[root, 0]]);
        const through = new Map();

        const childFirst = new Map();
        const childSecond = new Map();
        const bestChild = new Map();

        // Bottom-up calculation of the two longest downward branches.
        for (let index = order.length - 1; index >= 0; index--) {
            const node = order[index];

            let first = 0;
            let second = 0;
            let firstChild = null;

            for (const child of this.adjacency.get(node)) {
                if (parent.get(child) !== node) {
                    continue;
                }

                const height = 1 + down.get(child);

                if (height > first) {
                    second = first;
                    first = height;
                    firstChild = child;
                } else if (height > second) {
                    second = height;
                }
            }

            down.set(node, first);
            childFirst.set(node, first);
            childSecond.set(node, second);
            bestChild.set(node, firstChild);
        }

        // Top-down rerooting pass calculates the parent-side branch.
        for (const node of order) {
            const branches = [];

            if (parent.get(node) !== null) {
                branches.push(up.get(node));
            }

            for (const child of this.adjacency.get(node)) {
                if (parent.get(child) === node) {
                    branches.push(1 + down.get(child));
                }
            }

            branches.sort((a, b) => b - a);
            through.set(node, (branches[0] || 0) + (branches[1] || 0));

            for (const child of this.adjacency.get(node)) {
                if (parent.get(child) !== node) {
                    continue;
                }

                const siblingHeight =
                    bestChild.get(node) === child
                        ? childSecond.get(node)
                        : childFirst.get(node);

                up.set(
                    child,
                    1 + Math.max(0, up.get(node), siblingHeight)
                );
            }
        }

        return {
            heightEdges: Math.max(...depth.values()),
            diameterEdges: Math.max(...through.values()),
            through,
        };
    }

    breadthFirstSearch(start) {
        const distances = new Map([[start, 0]]);
        const parent = new Map([[start, null]]);
        const queue = [start];
        let head = 0;

        while (head < queue.length) {
            const current = queue[head++];

            for (const neighbor of this.adjacency.get(current)) {
                if (distances.has(neighbor)) {
                    continue;
                }

                distances.set(neighbor, distances.get(current) + 1);
                parent.set(neighbor, current);
                queue.push(neighbor);
            }
        }

        return { distances, parent };
    }

    farthestNode(distances) {
        let farthest = null;
        let maximumDistance = -1;

        // Preserve traversal order when several nodes have equal distance.
        for (const [node, distance] of distances) {
            if (distance > maximumDistance) {
                maximumDistance = distance;
                farthest = node;
            }
        }

        return farthest;
    }

    twoSweepAnalysis(start) {
        const first = this.breadthFirstSearch(start);
        const endpointA = this.farthestNode(first.distances);

        const second = this.breadthFirstSearch(endpointA);
        const endpointB = this.farthestNode(second.distances);

        const reversePath = [];
        let current = endpointB;

        while (current !== null) {
            reversePath.push(current);
            current = second.parent.get(current);
        }

        return {
            diameterEdges: second.distances.get(endpointB),
            endpointA,
            endpointB,
            path: reversePath.reverse(),
        };
    }

    analyze(root) {
        this.assertNode(root);

        this.emit("analysis-started", { root });

        const dp = this.dynamicProgrammingAnalysis(root);
        const sweep = this.twoSweepAnalysis(root);

        if (dp.diameterEdges !== sweep.diameterEdges) {
            throw new Error(
                `Diameter mismatch: DP=${dp.diameterEdges}, ` +
                `two-sweep=${sweep.diameterEdges}`
            );
        }

        const result = Object.freeze({
            root,
            heightEdges: dp.heightEdges,
            diameterEdges: dp.diameterEdges,
            diameterNodes: dp.diameterEdges + 1,
            endpointA: sweep.endpointA,
            endpointB: sweep.endpointB,
            longestPath: Object.freeze([...sweep.path]),
            diameterThroughNode: Object.freeze(
                Object.fromEntries(dp.through)
            ),
        });

        this.emit("analysis-completed", result);
        return result;
    }

    analyzeAsync(root, { signal } = {}) {
        return new Promise((resolve, reject) => {
            let scheduledHandle;

            const abortError = () => {
                const error = new Error("Tree analysis was cancelled.");
                error.name = "AbortError";
                return error;
            };

            const cleanup = () => {
                if (signal) {
                    signal.removeEventListener("abort", onAbort);
                }
            };

            const onAbort = () => {
                if (scheduledHandle !== undefined) {
                    clearImmediate(scheduledHandle);
                }

                cleanup();
                reject(abortError());
            };

            if (signal?.aborted) {
                reject(abortError());
                return;
            }

            if (signal) {
                signal.addEventListener("abort", onAbort, { once: true });
            }

            scheduledHandle = setImmediate(() => {
                cleanup();

                if (signal?.aborted) {
                    reject(abortError());
                    return;
                }

                try {
                    resolve(this.analyze(root));
                } catch (error) {
                    reject(error);
                }
            });
        });
    }
}

function runTests() {
    const chain = new TreeIndex(
        ["A", "B", "C", "D", "E"],
        [
            { from: "A", to: "B" },
            { from: "B", to: "C" },
            { from: "C", to: "D" },
            { from: "D", to: "E" },
        ]
    );

    const chainResult = chain.analyze("A");
    console.assert(chainResult.heightEdges === 4);
    console.assert(chainResult.diameterEdges === 4);
    console.assert(chainResult.diameterNodes === 5);

    const star = new TreeIndex(
        ["center", "north", "south", "east", "west"],
        [
            { from: "center", to: "north" },
            { from: "center", to: "south" },
            { from: "center", to: "east" },
            { from: "center", to: "west" },
        ]
    );

    const starResult = star.analyze("center");
    console.assert(starResult.diameterEdges === 2);
    console.assert(starResult.diameterThroughNode.north === 2);

    const singleton = new TreeIndex(["only"], []);
    const singletonResult = singleton.analyze("only");
    console.assert(singletonResult.diameterEdges === 0);
    console.assert(singletonResult.diameterNodes === 1);

    let invalidWasRejected = false;

    try {
        new TreeIndex(
            ["A", "B", "C"],
            [
                { from: "A", to: "B" },
                { from: "B", to: "C" },
                { from: "C", to: "A" },
            ]
        );
    } catch (error) {
        invalidWasRejected = error instanceof TreeValidationError;
    }

    console.assert(invalidWasRejected);
}

async function main() {
    runTests();

    const nodes = [
        "Headquarters",
        "North",
        "South",
        "North-East",
        "North-West",
        "South-Central",
        "South-East",
        "South-West",
    ];

    const links = [
        { from: "Headquarters", to: "North" },
        { from: "Headquarters", to: "South" },
        { from: "North", to: "North-East" },
        { from: "North", to: "North-West" },
        { from: "South", to: "South-Central" },
        { from: "South-Central", to: "South-East" },
        { from: "South-Central", to: "South-West" },
    ];

    const hierarchy = new TreeIndex(nodes, links);

    hierarchy.on("validated", (event) => {
        console.log(
            `Validated hierarchy: ${event.nodeCount} nodes, ` +
            `${event.edgeCount} links`
        );
    });

    hierarchy.on("analysis-completed", (result) => {
        console.log("\nAnalysis event received.");
        console.log(`Diameter: ${result.diameterEdges} edges`);
    });

    const result = await hierarchy.analyzeAsync("Headquarters");

    console.log("\nTREE DIAMETER ANALYSIS");
    console.log("----------------------");
    console.log(`Root: ${result.root}`);
    console.log(`Height: ${result.heightEdges} edges`);
    console.log(`Diameter: ${result.diameterEdges} edges`);
    console.log(`Diameter nodes: ${result.diameterNodes}`);
    console.log(
        `Longest path: ${result.longestPath.join(" -> ")}`
    );

    console.log("\nLongest path through each node:");
    for (const node of nodes) {
        console.log(
            `${node.padEnd(18)} ${result.diameterThroughNode[node]} edges`
        );
    }

    console.log("\nAll tests passed.");
}

main().catch((error) => {
    console.error(`${error.name}: ${error.message}`);
    process.exitCode = 1;
});
