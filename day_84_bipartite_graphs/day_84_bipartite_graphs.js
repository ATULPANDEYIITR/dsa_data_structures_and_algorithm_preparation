"use strict";

/**
 * Bipartite Graphs
 *
 * Demonstrates:
 * - Two-coloring with BFS and DFS.
 * - Connected component processing.
 * - Odd-cycle detection.
 * - Event-driven graph updates.
 * - Incremental edge insertion validation.
 * - Graph snapshots and version management.
 *
 * Runtime: Node.js 18+
 */

const Color = Object.freeze({
    UNCOLORED: -1,
    RED: 0,
    BLUE: 1
});

class GraphError extends Error {
    constructor(message) {
        super(message);
        this.name = "GraphError";
    }
}

class BipartiteGraph {
    #adjacency;
    #listeners;
    #version;

    constructor(vertexCount) {
        if (!Number.isSafeInteger(vertexCount) || vertexCount < 0) {
            throw new GraphError(
                "Vertex count must be a non-negative safe integer."
            );
        }

        this.vertexCount = vertexCount;
        this.#adjacency = Array.from(
            { length: vertexCount },
            () => new Set()
        );

        this.#listeners = new Map();
        this.#version = 0;
    }

    get version() {
        return this.#version;
    }

    #validateVertex(vertex) {
        if (
            !Number.isSafeInteger(vertex) ||
            vertex < 0 ||
            vertex >= this.vertexCount
        ) {
            throw new GraphError(`Invalid vertex: ${vertex}`);
        }
    }

    on(event, listener) {
        if (typeof listener !== "function") {
            throw new TypeError("Listener must be a function.");
        }

        if (!this.#listeners.has(event)) {
            this.#listeners.set(event, new Set());
        }

        this.#listeners.get(event).add(listener);

        return () => this.#listeners.get(event)?.delete(listener);
    }

    #emit(event, payload) {
        for (const listener of this.#listeners.get(event) ?? []) {
            try {
                listener(Object.freeze({ ...payload }));
            } catch (error) {
                // Observer failures must not corrupt graph updates.
                process.stderr.write(
                    `Event listener error: ${error.message}\n`
                );
            }
        }
    }

    addEdge(u, v) {
        this.#validateVertex(u);
        this.#validateVertex(v);

        const existed = this.#adjacency[u].has(v);

        if (existed) {
            return false;
        }

        this.#adjacency[u].add(v);

        if (u !== v) {
            this.#adjacency[v].add(u);
        }

        this.#version++;

        this.#emit("edgeAdded", {
            u,
            v,
            version: this.#version
        });

        return true;
    }

    removeEdge(u, v) {
        this.#validateVertex(u);
        this.#validateVertex(v);

        if (!this.#adjacency[u].has(v)) {
            return false;
        }

        this.#adjacency[u].delete(v);

        if (u !== v) {
            this.#adjacency[v].delete(u);
        }

        this.#version++;

        this.#emit("edgeRemoved", {
            u,
            v,
            version: this.#version
        });

        return true;
    }

    snapshot() {
        return this.#adjacency.map(
            neighbors => Object.freeze([...neighbors])
        );
    }

    #reconstructCycle(u, v, parent, depth) {
        let a = u;
        let b = v;

        const pathA = [a];
        const pathB = [b];

        while (depth[a] > depth[b]) {
            a = parent[a];
            pathA.push(a);
        }

        while (depth[b] > depth[a]) {
            b = parent[b];
            pathB.push(b);
        }

        while (a !== b) {
            a = parent[a];
            b = parent[b];

            pathA.push(a);
            pathB.push(b);
        }

        return [...pathA, ...pathB.slice(0, -1).reverse(), u];
    }

    analyzeBFS() {
        const adjacency = this.snapshot();
        const colors = Array(this.vertexCount).fill(Color.UNCOLORED);
        const parent = Array(this.vertexCount).fill(-1);
        const depth = Array(this.vertexCount).fill(0);

        let components = 0;

        for (let start = 0; start < this.vertexCount; start++) {
            if (colors[start] !== Color.UNCOLORED) {
                continue;
            }

            components++;
            colors[start] = Color.RED;

            const queue = [start];
            let head = 0;

            while (head < queue.length) {
                const u = queue[head++];

                for (const v of adjacency[u]) {
                    if (colors[v] === Color.UNCOLORED) {
                        colors[v] = 1 - colors[u];
                        parent[v] = u;
                        depth[v] = depth[u] + 1;
                        queue.push(v);
                    } else if (colors[v] === colors[u]) {
                        return {
                            isBipartite: false,
                            colors,
                            components,
                            oddCycle: this.#reconstructCycle(
                                u, v, parent, depth
                            ),
                            version: this.#version
                        };
                    }
                }
            }
        }

        return {
            isBipartite: true,
            colors,
            components,
            oddCycle: null,
            version: this.#version
        };
    }

    analyzeDFS() {
        const adjacency = this.snapshot();
        const colors = Array(this.vertexCount).fill(-1);
        const parent = Array(this.vertexCount).fill(-1);
        const depth = Array(this.vertexCount).fill(0);

        let components = 0;

        for (let start = 0; start < this.vertexCount; start++) {
            if (colors[start] !== -1) continue;

            components++;
            colors[start] = Color.RED;

            const stack = [start];

            while (stack.length > 0) {
                const u = stack.pop();

                for (const v of adjacency[u]) {
                    if (colors[v] === -1) {
                        colors[v] = 1 - colors[u];
                        parent[v] = u;
                        depth[v] = depth[u] + 1;
                        stack.push(v);
                    } else if (colors[v] === colors[u]) {
                        return {
                            isBipartite: false,
                            colors,
                            components,
                            oddCycle: this.#reconstructCycle(
                                u, v, parent, depth
                            ),
                            version: this.#version
                        };
                    }
                }
            }
        }

        return {
            isBipartite: true,
            colors,
            components,
            oddCycle: null,
            version: this.#version
        };
    }

    async analyzeAsync() {
        // Promise-based interface allows asynchronous orchestration.
        return Promise.resolve().then(() => this.analyzeBFS());
    }

    printResult(result, algorithm) {
        console.log(`\n${algorithm}`);

        if (result.isBipartite) {
            const groups = [[], []];

            result.colors.forEach((color, vertex) => {
                groups[color].push(vertex);
            });

            console.log("Bipartite: YES");
            console.log("RED:", groups[0]);
            console.log("BLUE:", groups[1]);
        } else {
            console.log("Bipartite: NO");
            console.log("Odd cycle:", result.oddCycle);
        }

        console.log("Connected components:", result.components);
        console.log("Graph version:", result.version);
    }
}

function buildGraph(vertices, edges) {
    const graph = new BipartiteGraph(vertices);

    for (const [u, v] of edges) {
        graph.addEdge(u, v);
    }

    return graph;
}

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

async function main() {
    const graph = buildGraph(6, [
        [0, 1],
        [1, 2],
        [2, 3],
        [3, 4],
        [4, 5],
        [5, 0]
    ]);

    graph.on("edgeAdded", event => {
        console.log(
            `Edge added: ${event.u}-${event.v}, version ${event.version}`
        );
    });

    graph.on("edgeRemoved", event => {
        console.log(
            `Edge removed: ${event.u}-${event.v}, version ${event.version}`
        );
    });

    const bfs = graph.analyzeBFS();
    const dfs = graph.analyzeDFS();

    graph.printResult(bfs, "BFS COLORING");
    graph.printResult(dfs, "DFS COLORING");

    assert(bfs.isBipartite, "Even cycle must be bipartite.");
    assert(dfs.isBipartite, "DFS must identify even cycle.");

    // Adding a diagonal creates an odd cycle.
    graph.addEdge(0, 2);

    const updated = await graph.analyzeAsync();
    graph.printResult(updated, "UPDATED GRAPH");

    assert(!updated.isBipartite, "Triangle must not be bipartite.");

    // Removing the conflicting edge restores the even cycle.
    graph.removeEdge(0, 2);

    assert(
        graph.analyzeBFS().isBipartite,
        "Removing conflicting edge should restore bipartiteness."
    );

    // Disconnected graph.
    const disconnected = buildGraph(7, [
        [0, 1],
        [1, 2],
        [3, 4],
        [5, 6]
    ]);

    assert(
        disconnected.analyzeBFS().components === 3,
        "Disconnected component count must be three."
    );

    // Self-loop.
    const selfLoop = buildGraph(2, [[0, 0]]);
    assert(!selfLoop.analyzeBFS().isBipartite, "Self-loop is invalid.");

    // Empty graph.
    const empty = new BipartiteGraph(0);
    assert(empty.analyzeBFS().isBipartite, "Empty graph is bipartite.");

    console.log("\nAll JavaScript tests passed.");
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
