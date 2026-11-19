"use strict";

/*
 * Graph Representation: Adjacency Matrix and Adjacency List
 *
 * Node.js 18+
 * No third-party dependencies.
 *
 * Features:
 * - Directed and undirected graphs
 * - Weighted edges
 * - Matrix and list representations
 * - Event-driven graph changes
 * - BFS and DFS
 * - Async traversal
 * - Representation comparison
 * - Input validation
 * - Snapshot and mutation handling
 */

const { EventEmitter } = require("node:events");
const { performance } = require("node:perf_hooks");

class GraphError extends Error {}

class VertexNotFoundError extends GraphError {}

class Graph {
    constructor({ directed = false, weighted = false } = {}) {
        this.directed = directed;
        this.weighted = weighted;

        this.vertices = [];
        this.indices = new Map();

        this.matrix = [];
        this.adjacency = new Map();

        this.events = new EventEmitter();
        this.version = 0;
    }

    validateVertex(vertex) {
        if (typeof vertex !== "string" || vertex.trim() === "") {
            throw new TypeError("Vertex must be a non-empty string.");
        }
    }

    requireVertex(vertex) {
        if (!this.indices.has(vertex)) {
            throw new VertexNotFoundError(
                `Vertex does not exist: ${vertex}`
            );
        }
    }

    validateWeight(weight) {
        if (
            typeof weight !== "number" ||
            !Number.isFinite(weight)
        ) {
            throw new TypeError("Weight must be a finite number.");
        }

        if (!this.weighted && weight !== 1) {
            throw new RangeError(
                "Unweighted graphs only accept weight 1."
            );
        }
    }

    changed(type, details) {
        this.version++;

        this.events.emit("change", {
            type,
            details,
            version: this.version,
            timestamp: new Date().toISOString()
        });
    }

    addVertex(vertex) {
        this.validateVertex(vertex);

        if (this.indices.has(vertex)) {
            return false;
        }

        const index = this.vertices.length;

        this.vertices.push(vertex);
        this.indices.set(vertex, index);
        this.adjacency.set(vertex, new Map());

        for (const row of this.matrix) {
            row.push(null);
        }

        this.matrix.push(
            Array(this.vertices.length).fill(null)
        );

        this.changed("vertex-added", { vertex });

        return true;
    }

    addEdge(source, target, weight = 1) {
        this.requireVertex(source);
        this.requireVertex(target);
        this.validateWeight(weight);

        const i = this.indices.get(source);
        const j = this.indices.get(target);

        const previous = this.matrix[i][j];

        this.matrix[i][j] = weight;
        this.adjacency.get(source).set(target, weight);

        if (!this.directed) {
            this.matrix[j][i] = weight;
            this.adjacency.get(target).set(source, weight);
        }

        this.changed("edge-added", {
            source,
            target,
            weight,
            replaced: previous !== null
        });

        return true;
    }

    removeEdge(source, target) {
        this.requireVertex(source);
        this.requireVertex(target);

        const i = this.indices.get(source);
        const j = this.indices.get(target);

        const existed = this.matrix[i][j] !== null;

        this.matrix[i][j] = null;
        this.adjacency.get(source).delete(target);

        if (!this.directed) {
            this.matrix[j][i] = null;
            this.adjacency.get(target).delete(source);
        }

        if (existed) {
            this.changed("edge-removed", { source, target });
        }

        return existed;
    }

    removeVertex(vertex) {
        this.requireVertex(vertex);

        const index = this.indices.get(vertex);

        this.vertices.splice(index, 1);
        this.matrix.splice(index, 1);

        for (const row of this.matrix) {
            row.splice(index, 1);
        }

        this.adjacency.delete(vertex);

        for (const neighbors of this.adjacency.values()) {
            neighbors.delete(vertex);
        }

        this.indices.clear();

        this.vertices.forEach((name, position) => {
            this.indices.set(name, position);
        });

        this.changed("vertex-removed", { vertex });

        return true;
    }

    hasEdge(source, target) {
        this.requireVertex(source);
        this.requireVertex(target);

        return this.matrix[
            this.indices.get(source)
        ][
            this.indices.get(target)
        ] !== null;
    }

    getWeight(source, target) {
        this.requireVertex(source);
        this.requireVertex(target);

        return this.matrix[
            this.indices.get(source)
        ][
            this.indices.get(target)
        ];
    }

    neighbors(vertex) {
        this.requireVertex(vertex);

        return [...this.adjacency.get(vertex).entries()]
            .map(([name, weight]) => ({ name, weight }));
    }

    degree(vertex) {
        this.requireVertex(vertex);

        if (!this.directed) {
            return this.adjacency.get(vertex).size;
        }

        return this.inDegree(vertex) + this.outDegree(vertex);
    }

    outDegree(vertex) {
        this.requireVertex(vertex);
        return this.adjacency.get(vertex).size;
    }

    inDegree(vertex) {
        this.requireVertex(vertex);

        let count = 0;

        for (const neighbors of this.adjacency.values()) {
            if (neighbors.has(vertex)) {
                count++;
            }
        }

        return count;
    }

    get edgeCount() {
        let count = 0;

        for (const neighbors of this.adjacency.values()) {
            count += neighbors.size;
        }

        if (this.directed) {
            return count;
        }

        let selfLoops = 0;

        for (const vertex of this.vertices) {
            if (this.adjacency.get(vertex).has(vertex)) {
                selfLoops++;
            }
        }

        return (count + selfLoops) / 2;
    }

    bfs(start) {
        this.requireVertex(start);

        const visited = new Set([start]);
        const queue = [start];
        const result = [];

        let head = 0;

        while (head < queue.length) {
            const current = queue[head++];
            result.push(current);

            for (const neighbor of this.adjacency.get(current).keys()) {
                if (!visited.has(neighbor)) {
                    visited.add(neighbor);
                    queue.push(neighbor);
                }
            }
        }

        return result;
    }

    dfs(start) {
        this.requireVertex(start);

        const visited = new Set();
        const stack = [start];
        const result = [];

        while (stack.length > 0) {
            const current = stack.pop();

            if (visited.has(current)) {
                continue;
            }

            visited.add(current);
            result.push(current);

            const neighbors = [
                ...this.adjacency.get(current).keys()
            ];

            for (let i = neighbors.length - 1; i >= 0; i--) {
                if (!visited.has(neighbors[i])) {
                    stack.push(neighbors[i]);
                }
            }
        }

        return result;
    }

    async bfsAsync(start, { signal, batchSize = 100 } = {}) {
        this.requireVertex(start);

        if (!Number.isInteger(batchSize) || batchSize < 1) {
            throw new RangeError("batchSize must be a positive integer.");
        }

        const snapshotVersion = this.version;
        const visited = new Set([start]);
        const queue = [start];
        const result = [];

        let head = 0;

        while (head < queue.length) {
            if (signal?.aborted) {
                throw new Error("Traversal aborted.");
            }

            for (
                let processed = 0;
                processed < batchSize && head < queue.length;
                processed++
            ) {
                const current = queue[head++];
                result.push(current);

                for (
                    const neighbor of this.adjacency.get(current).keys()
                ) {
                    if (!visited.has(neighbor)) {
                        visited.add(neighbor);
                        queue.push(neighbor);
                    }
                }
            }

            if (head < queue.length) {
                await new Promise(resolve => setImmediate(resolve));
            }
        }

        return {
            traversal: result,
            graphVersion: snapshotVersion,
            consistentVersion: snapshotVersion === this.version
        };
    }

    snapshot() {
        return Object.freeze({
            version: this.version,
            vertices: Object.freeze([...this.vertices]),
            edges: Object.freeze(
                this.vertices.flatMap(source =>
                    [...this.adjacency.get(source)].map(
                        ([target, weight]) => Object.freeze({
                            source,
                            target,
                            weight
                        })
                    )
                )
            )
        });
    }

    statistics() {
        const vertexCount = this.vertices.length;
        const edgeCount = this.edgeCount;

        const maximumEdges = this.directed
            ? vertexCount * (vertexCount - 1)
            : vertexCount * (vertexCount - 1) / 2;

        return {
            vertices: vertexCount,
            edges: edgeCount,
            matrixCells: vertexCount ** 2,
            adjacencyEntries: [...this.adjacency.values()]
                .reduce((sum, map) => sum + map.size, 0),
            density: maximumEdges === 0
                ? 0
                : edgeCount / maximumEdges
        };
    }

    display() {
        console.log("\nADJACENCY MATRIX");

        console.log(
            "    " + this.vertices.join("\t")
        );

        this.vertices.forEach((vertex, i) => {
            console.log(
                vertex,
                this.matrix[i].map(
                    value => value === null ? "-" : value
                ).join("\t")
            );
        });

        console.log("\nADJACENCY LIST");

        for (const vertex of this.vertices) {
            const connections = this.neighbors(vertex)
                .map(edge => `${edge.name}(${edge.weight})`);

            console.log(
                `${vertex}: ${connections.join(", ") || "None"}`
            );
        }
    }
}

function compareRepresentations(graph) {
    const stats = graph.statistics();

    console.log("\nREPRESENTATION ANALYSIS");
    console.table(stats);

    console.table([
        {
            operation: "Space",
            matrix: "O(V²)",
            list: "O(V + E)"
        },
        {
            operation: "Edge lookup",
            matrix: "O(1)",
            list: "O(degree)"
        },
        {
            operation: "Neighbor iteration",
            matrix: "O(V)",
            list: "O(degree)"
        },
        {
            operation: "Insert edge",
            matrix: "O(1)",
            list: "O(1) average"
        },
        {
            operation: "BFS / DFS",
            matrix: "O(V²)",
            list: "O(V + E)"
        }
    ]);

    return stats;
}

function createSampleGraph() {
    const graph = new Graph({
        directed: false,
        weighted: true
    });

    for (const vertex of ["A", "B", "C", "D", "E", "F"]) {
        graph.addVertex(vertex);
    }

    const edges = [
        ["A", "B", 4],
        ["A", "C", 2],
        ["B", "C", 1],
        ["B", "D", 5],
        ["C", "D", 8],
        ["C", "E", 10],
        ["D", "E", 2],
        ["D", "F", 6],
        ["E", "F", 3]
    ];

    for (const [source, target, weight] of edges) {
        graph.addEdge(source, target, weight);
    }

    return graph;
}

function runTests() {
    const graph = new Graph();

    graph.addVertex("A");
    graph.addVertex("B");
    graph.addVertex("C");

    graph.addEdge("A", "B");

    console.assert(graph.hasEdge("A", "B"));
    console.assert(graph.hasEdge("B", "A"));
    console.assert(graph.edgeCount === 1);
    console.assert(graph.degree("A") === 1);

    graph.removeEdge("A", "B");

    console.assert(!graph.hasEdge("A", "B"));

    const directed = new Graph({ directed: true });

    directed.addVertex("X");
    directed.addVertex("Y");
    directed.addEdge("X", "Y");

    console.assert(directed.outDegree("X") === 1);
    console.assert(directed.inDegree("Y") === 1);
    console.assert(!directed.hasEdge("Y", "X"));

    directed.removeVertex("Y");

    console.assert(directed.vertices.length === 1);

    let rejected = false;

    try {
        graph.addVertex("");
    } catch (error) {
        rejected = error instanceof TypeError;
    }

    if (!rejected) {
        throw new Error("Empty vertex validation failed.");
    }

    console.log("All tests passed.");
}

async function main() {
    runTests();

    const graph = createSampleGraph();

    graph.events.on("change", event => {
        console.log(
            `EVENT ${event.type}: version=${event.version}`
        );
    });

    graph.display();

    console.log("\nTRAVERSALS");
    console.log("BFS:", graph.bfs("A"));
    console.log("DFS:", graph.dfs("A"));

    const asyncResult = await graph.bfsAsync("A", {
        batchSize: 2
    });

    console.log("Asynchronous BFS:", asyncResult);

    console.log("\nCOMPARISON");
    compareRepresentations(graph);

    console.log("\nMUTATION");
    graph.removeEdge("C", "E");
    graph.removeVertex("F");

    console.log("Final graph:", graph.snapshot());

    const start = performance.now();
    graph.bfs("A");
    const elapsed = performance.now() - start;

    console.log(
        `Traversal execution time: ${elapsed.toFixed(4)} ms`
    );
}

if (require.main === module) {
    main().catch(error => {
        console.error("Graph execution failed:", error.message);
        process.exitCode = 1;
    });
}

module.exports = {
    Graph,
    GraphError,
    VertexNotFoundError,
    compareRepresentations
};
