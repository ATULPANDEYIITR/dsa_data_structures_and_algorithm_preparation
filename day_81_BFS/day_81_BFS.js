"use strict";

/*
 * Breadth-First Search (BFS)
 *
 * JavaScript implementation emphasizing:
 * - Map-based graph storage
 * - Set-based visited tracking
 * - Queue-based traversal
 * - Event-driven level processing
 * - Shortest paths
 * - Multi-source BFS
 * - Grid traversal
 * - Asynchronous traversal
 *
 * Runtime: Node.js 18+
 */

const assert = require("node:assert/strict");
const { EventEmitter } = require("node:events");


class Graph extends EventEmitter {
    constructor({ directed = false } = {}) {
        super();

        this.directed = directed;
        this.adjacency = new Map();
    }

    addVertex(vertex) {
        if (!Number.isSafeInteger(vertex)) {
            throw new TypeError("Vertex must be a safe integer");
        }

        if (!this.adjacency.has(vertex)) {
            this.adjacency.set(vertex, []);
        }
    }

    addEdge(source, destination) {
        this.addVertex(source);
        this.addVertex(destination);

        this.adjacency.get(source).push(destination);

        if (!this.directed) {
            this.adjacency.get(destination).push(source);
        }
    }

    validateSources(sources) {
        if (!Array.isArray(sources) || sources.length === 0) {
            throw new Error("At least one source is required");
        }

        for (const source of sources) {
            if (!this.adjacency.has(source)) {
                throw new Error(`Unknown vertex: ${source}`);
            }
        }
    }

    createResult(distances, parents, levels) {
        return {
            distances,
            parents,
            levels,

            shortestPath(target) {
                if (!distances.has(target)) {
                    return null;
                }

                const path = [];
                let current = target;

                while (current !== null) {
                    path.push(current);
                    current = parents.get(current);
                }

                return path.reverse();
            }
        };
    }

    bfs(start) {
        return this.multiSourceBfs([start]);
    }

    multiSourceBfs(sources) {
        this.validateSources(sources);

        const uniqueSources = [...new Set(sources)];

        const queue = [...uniqueSources];
        let head = 0;

        const distances = new Map();
        const parents = new Map();
        const levels = new Map();

        levels.set(0, [...uniqueSources]);

        for (const source of uniqueSources) {
            distances.set(source, 0);
            parents.set(source, null);
        }

        while (head < queue.length) {
            const current = queue[head++];

            for (const neighbor of this.adjacency.get(current)) {
                if (distances.has(neighbor)) {
                    continue;
                }

                const distance = distances.get(current) + 1;

                distances.set(neighbor, distance);
                parents.set(neighbor, current);

                if (!levels.has(distance)) {
                    levels.set(distance, []);
                }

                levels.get(distance).push(neighbor);
                queue.push(neighbor);
            }
        }

        return this.createResult(distances, parents, levels);
    }

    async *traverseByLevel(start) {
        if (!this.adjacency.has(start)) {
            throw new Error(`Unknown vertex: ${start}`);
        }

        const queue = [start];
        let head = 0;

        const visited = new Set([start]);
        let level = 0;

        while (head < queue.length) {
            const levelEnd = queue.length;
            const currentLevel = [];

            while (head < levelEnd) {
                const current = queue[head++];
                currentLevel.push(current);

                for (const neighbor of this.adjacency.get(current)) {
                    if (!visited.has(neighbor)) {
                        visited.add(neighbor);
                        queue.push(neighbor);
                    }
                }
            }

            this.emit("level", {
                level,
                vertices: currentLevel
            });

            yield {
                level,
                vertices: currentLevel
            };

            level++;
        }
    }
}


function shortestPathGrid(grid, start, target) {
    if (!Array.isArray(grid) || grid.length === 0) {
        throw new Error("Grid cannot be empty");
    }

    const rows = grid.length;
    const cols = grid[0].length;

    if (
        cols === 0 ||
        grid.some(row => !Array.isArray(row) || row.length !== cols)
    ) {
        throw new Error("Grid must be rectangular and nonempty");
    }

    if (grid.some(row => row.some(
        cell => cell !== 0 && cell !== 1
    ))) {
        throw new Error("Grid cells must be 0 or 1");
    }

    const valid = ([r, c]) =>
        Number.isInteger(r) &&
        Number.isInteger(c) &&
        r >= 0 &&
        r < rows &&
        c >= 0 &&
        c < cols &&
        grid[r][c] === 0;

    if (!valid(start) || !valid(target)) {
        return null;
    }

    const key = ([r, c]) => `${r},${c}`;

    const queue = [start];
    let head = 0;

    const parents = new Map();
    parents.set(key(start), null);

    const directions = [
        [-1, 0],
        [1, 0],
        [0, -1],
        [0, 1]
    ];

    while (head < queue.length) {
        const current = queue[head++];
        const currentKey = key(current);

        if (currentKey === key(target)) {
            break;
        }

        for (const [dr, dc] of directions) {
            const next = [
                current[0] + dr,
                current[1] + dc
            ];

            const nextKey = key(next);

            if (valid(next) && !parents.has(nextKey)) {
                parents.set(nextKey, currentKey);
                queue.push(next);
            }
        }
    }

    const targetKey = key(target);

    if (!parents.has(targetKey)) {
        return null;
    }

    const path = [];
    let currentKey = targetKey;

    while (currentKey !== null) {
        const [r, c] = currentKey.split(",").map(Number);
        path.push([r, c]);
        currentKey = parents.get(currentKey);
    }

    return path.reverse();
}


async function main() {
    const graph = new Graph();

    const edges = [
        [0, 1], [0, 2],
        [1, 3], [1, 4],
        [2, 5], [2, 6],
        [4, 7], [5, 7]
    ];

    edges.forEach(([u, v]) => graph.addEdge(u, v));

    console.log("=== BFS Traversal ===");

    const result = graph.bfs(0);

    console.log("Distances:", Object.fromEntries(result.distances));
    console.log("Parents:", Object.fromEntries(result.parents));
    console.log("Levels:", Object.fromEntries(result.levels));

    console.log("Shortest path 0 -> 7:",
        result.shortestPath(7));

    console.log("\n=== Multi-Source BFS ===");

    const multi = graph.multiSourceBfs([0, 7]);

    console.log("Distances:", Object.fromEntries(multi.distances));

    console.log("\n=== Event-Driven Level Processing ===");

    graph.on("level", event => {
        console.log(`Level ${event.level}:`, event.vertices);
    });

    for await (const level of graph.traverseByLevel(0)) {
        // Each completed level is available to asynchronous consumers.
        assert.ok(level.vertices.length > 0);
    }

    console.log("\n=== Grid Shortest Path ===");

    const grid = [
        [0, 0, 0, 1],
        [1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 0]
    ];

    console.log(
        shortestPathGrid(grid, [0, 0], [3, 3])
    );

    console.log("\n=== Validation ===");

    assert.equal(result.distances.get(7), 3);
    assert.deepEqual(result.shortestPath(7), [0, 1, 4, 7]);
    assert.equal(result.shortestPath(100), null);

    assert.equal(multi.distances.get(0), 0);
    assert.equal(multi.distances.get(7), 0);

    assert.equal(
        shortestPathGrid([[0, 1], [1, 0]], [0, 0], [1, 1]),
        null
    );

    assert.throws(
        () => graph.bfs(999),
        /Unknown vertex/
    );

    assert.throws(
        () => graph.multiSourceBfs([]),
        /At least one source/
    );

    assert.throws(
        () => shortestPathGrid([[0], [0, 1]], [0, 0], [1, 1]),
        /rectangular/
    );

    console.log("All tests passed.");
}


main().catch(error => {
    console.error("BFS execution failed:", error.message);
    process.exitCode = 1;
});
