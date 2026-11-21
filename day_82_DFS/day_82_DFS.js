"use strict";

/*
 * Depth-First Search and Connected Components
 *
 * Engineering perspective:
 * - Event-driven traversal
 * - Iterative DFS
 * - Recursive DFS
 * - Graph mutation
 * - Connected component analysis
 * - Asynchronous traversal
 * - Traversal event reporting
 *
 * Runtime: Node.js
 */

const assert = require("node:assert/strict");
const { EventEmitter } = require("node:events");

class Graph extends EventEmitter {
    constructor() {
        super();
        this.adjacency = new Map();
        this.version = 0;
    }

    addVertex(vertex) {
        if (!Number.isSafeInteger(vertex)) {
            throw new TypeError("Vertex must be a safe integer.");
        }

        if (!this.adjacency.has(vertex)) {
            this.adjacency.set(vertex, new Set());
            this.version++;
            this.emit("vertexAdded", { vertex, version: this.version });
        }
    }

    addEdge(u, v) {
        if (!Number.isSafeInteger(u) || !Number.isSafeInteger(v)) {
            throw new TypeError("Edge endpoints must be safe integers.");
        }

        if (u === v) {
            throw new Error("Self-loops are not supported.");
        }

        this.addVertex(u);
        this.addVertex(v);

        if (!this.adjacency.get(u).has(v)) {
            this.adjacency.get(u).add(v);
            this.adjacency.get(v).add(u);
            this.version++;

            this.emit("edgeAdded", { u, v, version: this.version });
        }
    }

    removeEdge(u, v) {
        if (!this.adjacency.has(u) || !this.adjacency.has(v)) {
            throw new Error("Unknown vertex.");
        }

        if (!this.adjacency.get(u).has(v)) {
            throw new Error("Edge does not exist.");
        }

        this.adjacency.get(u).delete(v);
        this.adjacency.get(v).delete(u);
        this.version++;
    }

    validateStart(start) {
        if (!this.adjacency.has(start)) {
            throw new Error(`Unknown starting vertex: ${start}`);
        }
    }

    /*
     * Recursive DFS.
     *
     * Recursive calls follow the graph's sorted adjacency order.
     * Deep graphs may exceed the JavaScript call-stack limit.
     */
    recursiveDFS(start) {
        this.validateStart(start);

        const visited = new Set();
        const order = [];
        const parents = new Map([[start, null]]);
        const depths = new Map([[start, 0]]);

        const visit = (vertex) => {
            visited.add(vertex);
            order.push(vertex);

            this.emit("visited", { vertex });

            const neighbors = [...this.adjacency.get(vertex)].sort(
                (a, b) => a - b
            );

            for (const neighbor of neighbors) {
                if (!visited.has(neighbor)) {
                    parents.set(neighbor, vertex);
                    depths.set(neighbor, depths.get(vertex) + 1);
                    visit(neighbor);
                }
            }
        };

        visit(start);

        return {
            start,
            order,
            parents,
            depths,
            graphVersion: this.version
        };
    }

    /*
     * Iterative DFS.
     *
     * Marks nodes when pushing them, preventing duplicate
     * stack entries in graphs with multiple connecting edges.
     */
    iterativeDFS(start) {
        this.validateStart(start);

        const visited = new Set([start]);
        const stack = [start];
        const order = [];

        const parents = new Map([[start, null]]);
        const depths = new Map([[start, 0]]);

        while (stack.length > 0) {
            const vertex = stack.pop();

            order.push(vertex);
            this.emit("visited", { vertex });

            const neighbors = [...this.adjacency.get(vertex)]
                .sort((a, b) => b - a);

            for (const neighbor of neighbors) {
                if (!visited.has(neighbor)) {
                    visited.add(neighbor);
                    parents.set(neighbor, vertex);
                    depths.set(neighbor, depths.get(vertex) + 1);
                    stack.push(neighbor);
                }
            }
        }

        return {
            start,
            order,
            parents,
            depths,
            graphVersion: this.version
        };
    }

    /*
     * Async iterative traversal.
     *
     * A batch is processed before yielding control.
     * This avoids blocking the event loop for the entire traversal.
     */
    async *asyncDFS(start, batchSize = 100) {
        this.validateStart(start);

        if (!Number.isSafeInteger(batchSize) || batchSize < 1) {
            throw new RangeError("Batch size must be positive.");
        }

        const expectedVersion = this.version;
        const visited = new Set([start]);
        const stack = [start];

        let processed = 0;

        while (stack.length > 0) {
            if (this.version !== expectedVersion) {
                throw new Error("Graph changed during traversal.");
            }

            const vertex = stack.pop();
            yield vertex;

            processed++;

            for (const neighbor of [...this.adjacency.get(vertex)].sort(
                (a, b) => b - a
            )) {
                if (!visited.has(neighbor)) {
                    visited.add(neighbor);
                    stack.push(neighbor);
                }
            }

            if (processed % batchSize === 0) {
                await new Promise(resolve => setImmediate(resolve));
            }
        }
    }

    connectedComponents() {
        const visited = new Set();
        const components = [];

        const vertices = [...this.adjacency.keys()].sort(
            (a, b) => a - b
        );

        for (const start of vertices) {
            if (visited.has(start)) {
                continue;
            }

            const component = [];
            const stack = [start];
            visited.add(start);

            while (stack.length > 0) {
                const vertex = stack.pop();
                component.push(vertex);

                for (const neighbor of [...this.adjacency.get(vertex)].sort(
                    (a, b) => b - a
                )) {
                    if (!visited.has(neighbor)) {
                        visited.add(neighbor);
                        stack.push(neighbor);
                    }
                }
            }

            components.push(component.sort((a, b) => a - b));
        }

        return components;
    }

    reconstructPath(result, destination) {
        if (!result.parents.has(destination)) {
            return null;
        }

        const path = [];
        let current = destination;

        while (current !== null) {
            path.push(current);
            current = result.parents.get(current);
        }

        return path.reverse();
    }

    hasCycle() {
        const visited = new Set();

        const visit = (vertex, parent) => {
            visited.add(vertex);

            for (const neighbor of this.adjacency.get(vertex)) {
                if (!visited.has(neighbor)) {
                    if (visit(neighbor, vertex)) {
                        return true;
                    }
                } else if (neighbor !== parent) {
                    return true;
                }
            }

            return false;
        };

        for (const vertex of this.adjacency.keys()) {
            if (!visited.has(vertex) && visit(vertex, null)) {
                return true;
            }
        }

        return false;
    }
}

async function main() {
    const graph = new Graph();

    graph.on("vertexAdded", ({ vertex }) => {
        console.log(`Vertex registered: ${vertex}`);
    });

    graph.on("edgeAdded", ({ u, v }) => {
        console.log(`Edge registered: ${u} -- ${v}`);
    });

    for (let vertex = 1; vertex <= 10; vertex++) {
        graph.addVertex(vertex);
    }

    const edges = [
        [1, 2], [1, 3],
        [2, 4], [2, 5],
        [3, 6], [3, 7],
        [5, 8], [6, 8],
        [9, 10]
    ];

    for (const [u, v] of edges) {
        graph.addEdge(u, v);
    }

    console.log("\nRecursive DFS:");

    const recursive = graph.recursiveDFS(1);
    console.log(recursive.order);

    console.log("\nIterative DFS:");

    const iterative = graph.iterativeDFS(1);
    console.log(iterative.order);

    assert.deepEqual(recursive.order, iterative.order);

    console.log("\nReconstructed path:");
    console.log(graph.reconstructPath(iterative, 8));

    console.log("\nUnreachable vertex:");
    console.log(graph.reconstructPath(iterative, 10));

    console.log("\nConnected components:");
    console.log(graph.connectedComponents());

    console.log("\nCycle detection:");
    console.log(graph.hasCycle());

    console.log("\nAsynchronous DFS:");

    const asyncOrder = [];

    for await (const vertex of graph.asyncDFS(1, 2)) {
        asyncOrder.push(vertex);
    }

    console.log(asyncOrder);

    assert.deepEqual(asyncOrder, iterative.order);

    console.log("\nIsolated vertex test:");

    const isolated = new Graph();
    isolated.addVertex(100);
    isolated.addVertex(200);
    isolated.addVertex(300);
    isolated.addEdge(100, 200);

    console.log(isolated.connectedComponents());

    console.log("\nValidation test:");

    try {
        graph.iterativeDFS(999);
    } catch (error) {
        console.log(error.message);
    }

    console.log("\nAll assertions passed.");
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
