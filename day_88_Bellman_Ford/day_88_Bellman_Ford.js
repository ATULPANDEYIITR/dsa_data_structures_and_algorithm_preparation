"use strict";

/*
 * Bellman-Ford: Event-Driven Graph Analysis
 *
 * Features:
 * - Directed weighted graphs
 * - Edge relaxation
 * - Negative-weight support
 * - Reachable negative-cycle detection
 * - Negative-cycle propagation
 * - Shortest-path reconstruction
 * - Dijkstra comparison
 * - Event-driven execution reporting
 *
 * Runtime: Node.js 18+
 */

const { EventEmitter } = require("node:events");
const assert = require("node:assert/strict");

class GraphValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "GraphValidationError";
    }
}

class NegativeWeightError extends Error {
    constructor(message) {
        super(message);
        this.name = "NegativeWeightError";
    }
}

class WeightedGraph extends EventEmitter {
    constructor(vertices) {
        super();

        if (!Array.isArray(vertices) || vertices.length === 0) {
            throw new GraphValidationError(
                "At least one vertex is required."
            );
        }

        if (new Set(vertices).size !== vertices.length) {
            throw new GraphValidationError(
                "Duplicate vertices are not allowed."
            );
        }

        if (!vertices.every(Number.isSafeInteger)) {
            throw new GraphValidationError(
                "Vertex identifiers must be safe integers."
            );
        }

        this.vertices = Object.freeze([...vertices]);
        this.vertexSet = new Set(vertices);
        this.edges = [];
        this.adjacency = new Map(
            vertices.map(vertex => [vertex, []])
        );
    }

    addEdge(source, destination, weight) {
        if (!this.vertexSet.has(source) ||
            !this.vertexSet.has(destination)) {
            throw new GraphValidationError(
                `Invalid edge: ${source} -> ${destination}`
            );
        }

        if (!Number.isSafeInteger(weight)) {
            throw new GraphValidationError(
                "Weights must be safe integers."
            );
        }

        const edge = Object.freeze({
            source,
            destination,
            weight
        });

        this.edges.push(edge);

        this.adjacency.get(source).push({
            destination,
            weight
        });

        this.emit("edgeAdded", edge);
    }

    validateSource(source) {
        if (!this.vertexSet.has(source)) {
            throw new GraphValidationError(
                `Unknown source vertex: ${source}`
            );
        }
    }

    createResult(source, distances, predecessors,
                 affected, iterations, algorithm) {
        return {
            source,
            distances,
            predecessors,
            affected: new Set(affected),
            negativeCycle: affected.size > 0,
            iterations,
            algorithm,

            pathTo: destination => {
                if (!this.vertexSet.has(destination)) {
                    throw new GraphValidationError(
                        "Unknown destination vertex."
                    );
                }

                if (affected.has(destination)) {
                    throw new Error(
                        "Shortest path is undefined due to a reachable negative cycle."
                    );
                }

                if (distances.get(destination) === Infinity) {
                    return null;
                }

                const path = [];
                const visited = new Set();

                let current = destination;

                while (current !== null) {
                    if (visited.has(current)) {
                        throw new Error(
                            "Predecessor cycle detected."
                        );
                    }

                    visited.add(current);
                    path.push(current);
                    current = predecessors.get(current);
                }

                path.reverse();

                return path[0] === source ? path : null;
            }
        };
    }

    async bellmanFord(source) {
        this.validateSource(source);

        const distances = new Map(
            this.vertices.map(vertex => [vertex, Infinity])
        );

        const predecessors = new Map(
            this.vertices.map(vertex => [vertex, null])
        );

        distances.set(source, 0);

        let iterations = 0;

        // Every relaxation pass processes the complete edge list.
        for (let pass = 1; pass < this.vertices.length; pass++) {
            let changed = false;
            iterations++;

            for (const edge of this.edges) {
                const current = distances.get(edge.source);

                if (current === Infinity) {
                    continue;
                }

                const candidate = current + edge.weight;

                if (!Number.isSafeInteger(candidate)) {
                    throw new RangeError(
                        "Distance exceeds JavaScript safe integer precision."
                    );
                }

                if (candidate < distances.get(edge.destination)) {
                    distances.set(edge.destination, candidate);
                    predecessors.set(
                        edge.destination,
                        edge.source
                    );

                    changed = true;

                    this.emit("relaxation", {
                        edge,
                        distance: candidate,
                        pass
                    });
                }
            }

            this.emit("passCompleted", {
                pass,
                changed
            });

            if (!changed) {
                break;
            }

            // Yield between passes so asynchronous consumers can
            // process progress events.
            await new Promise(resolve => setImmediate(resolve));
        }

        // Detect relaxable edges after V-1 passes.
        const affected = new Set();

        for (const edge of this.edges) {
            const current = distances.get(edge.source);

            if (current === Infinity) {
                continue;
            }

            const candidate = current + edge.weight;

            if (!Number.isSafeInteger(candidate)) {
                throw new RangeError(
                    "Distance exceeds JavaScript safe integer precision."
                );
            }

            if (candidate < distances.get(edge.destination)) {
                affected.add(edge.destination);
            }
        }

        // Propagate negative-cycle influence using breadth-first search.
        const queue = [...affected];

        for (let index = 0; index < queue.length; index++) {
            const current = queue[index];

            for (const edge of this.adjacency.get(current)) {
                if (!affected.has(edge.destination)) {
                    affected.add(edge.destination);
                    queue.push(edge.destination);
                }
            }
        }

        this.emit("analysisCompleted", {
            source,
            negativeCycle: affected.size > 0,
            affectedVertices: [...affected]
        });

        return this.createResult(
            source,
            distances,
            predecessors,
            affected,
            iterations,
            "Bellman-Ford"
        );
    }

    dijkstra(source) {
        this.validateSource(source);

        if (this.edges.some(edge => edge.weight < 0)) {
            throw new NegativeWeightError(
                "Dijkstra requires nonnegative edge weights."
            );
        }

        const distances = new Map(
            this.vertices.map(vertex => [vertex, Infinity])
        );

        const predecessors = new Map(
            this.vertices.map(vertex => [vertex, null])
        );

        const settled = new Set();
        const queue = [{ vertex: source, distance: 0 }];

        distances.set(source, 0);

        let iterations = 0;

        // A sorted array is used as a simple priority queue.
        // A binary heap is preferable for large production graphs.
        while (queue.length > 0) {
            queue.sort((a, b) => a.distance - b.distance);

            const current = queue.shift();
            iterations++;

            if (current.distance !== distances.get(current.vertex)) {
                continue;
            }

            if (settled.has(current.vertex)) {
                continue;
            }

            settled.add(current.vertex);

            for (const edge of this.adjacency.get(current.vertex)) {
                const candidate = current.distance + edge.weight;

                if (!Number.isSafeInteger(candidate)) {
                    throw new RangeError(
                        "Distance exceeds JavaScript safe integer precision."
                    );
                }

                if (candidate < distances.get(edge.destination)) {
                    distances.set(edge.destination, candidate);
                    predecessors.set(
                        edge.destination,
                        current.vertex
                    );

                    queue.push({
                        vertex: edge.destination,
                        distance: candidate
                    });
                }
            }
        }

        return this.createResult(
            source,
            distances,
            predecessors,
            new Set(),
            iterations,
            "Dijkstra"
        );
    }
}

function printResult(result, vertices) {
    console.log(`\nAlgorithm: ${result.algorithm}`);
    console.log(`Source: ${result.source}`);
    console.log(`Negative cycle: ${result.negativeCycle}`);

    console.table(
        vertices.map(vertex => ({
            vertex,
            distance: result.affected.has(vertex)
                ? "Undefined (-cycle)"
                : result.distances.get(vertex) === Infinity
                    ? "Unreachable"
                    : result.distances.get(vertex),

            path: result.affected.has(vertex)
                ? "Undefined"
                : result.pathTo(vertex)?.join(" -> ") ?? "None"
        }))
    );
}

async function demonstrateNegativeEdges() {
    console.log("\n=== NEGATIVE EDGE SCENARIO ===");

    const graph = new WeightedGraph([0, 1, 2, 3, 4, 5]);

    graph.on("relaxation", event => {
        console.log(
            `Relaxed ${event.edge.source} -> ${event.edge.destination}, ` +
            `new distance = ${event.distance}`
        );
    });

    graph.on("passCompleted", event => {
        console.log(
            `Pass ${event.pass}: changed=${event.changed}`
        );
    });

    [
        [0, 1, 4],
        [0, 2, 5],
        [1, 2, -2],
        [1, 3, 6],
        [2, 3, 3],
        [3, 4, 2],
        [4, 1, 1]
    ].forEach(edge => graph.addEdge(...edge));

    const result = await graph.bellmanFord(0);

    printResult(result, graph.vertices);

    assert.equal(result.distances.get(4), 7);
    assert.equal(result.distances.get(5), Infinity);
    assert.equal(result.negativeCycle, false);

    try {
        graph.dijkstra(0);
    } catch (error) {
        assert.ok(error instanceof NegativeWeightError);
        console.log(`Dijkstra rejected: ${error.message}`);
    }
}

async function demonstrateNegativeCycle() {
    console.log("\n=== NEGATIVE CYCLE SCENARIO ===");

    const graph = new WeightedGraph([0, 1, 2, 3, 4, 5]);

    [
        [0, 1, 2],
        [1, 2, 2],
        [2, 3, -5],
        [3, 1, 1],
        [3, 4, 3],
        [5, 5, -1]
    ].forEach(edge => graph.addEdge(...edge));

    const result = await graph.bellmanFord(0);

    printResult(result, graph.vertices);

    assert.equal(result.negativeCycle, true);

    for (const vertex of [1, 2, 3, 4]) {
        assert.ok(result.affected.has(vertex));
    }

    assert.ok(!result.affected.has(5));

    console.log("Reachable negative-cycle detection passed.");

    try {
        result.pathTo(4);
    } catch (error) {
        console.log(`Path reconstruction rejected: ${error.message}`);
    }
}

async function demonstrateAlgorithmComparison() {
    console.log("\n=== ALGORITHM COMPARISON ===");

    const graph = new WeightedGraph([0, 1, 2, 3, 4]);

    [
        [0, 1, 10],
        [0, 2, 3],
        [2, 1, 2],
        [1, 3, 4],
        [2, 3, 8],
        [2, 4, 2],
        [4, 3, 1]
    ].forEach(edge => graph.addEdge(...edge));

    const bellman = await graph.bellmanFord(0);
    const dijkstra = graph.dijkstra(0);

    printResult(bellman, graph.vertices);
    printResult(dijkstra, graph.vertices);

    for (const vertex of graph.vertices) {
        assert.equal(
            bellman.distances.get(vertex),
            dijkstra.distances.get(vertex)
        );
    }

    console.log("Both algorithms agree.");
}

async function main() {
    await demonstrateNegativeEdges();
    await demonstrateNegativeCycle();
    await demonstrateAlgorithmComparison();

    console.log("\nAll JavaScript tests passed.");
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
