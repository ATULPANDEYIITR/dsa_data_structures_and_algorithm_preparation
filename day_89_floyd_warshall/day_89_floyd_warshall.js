"use strict";

/*
 * Floyd-Warshall Algorithm
 * Event-driven all-pairs shortest-path engine.
 *
 * Runtime: Node.js 18+
 *
 * Features:
 * - Directed weighted graph
 * - Map-based adjacency representation
 * - Typed arrays for distance storage
 * - Intermediate vertex processing
 * - Path reconstruction
 * - Negative cycle detection
 * - Asynchronous computation interface
 * - EventEmitter-based workflow notifications
 */

const { EventEmitter } = require("node:events");

class GraphError extends Error {
    constructor(message) {
        super(message);
        this.name = "GraphError";
    }
}

class NegativeCycleError extends GraphError {
    constructor(vertices) {
        super(`Negative cycle detected: ${vertices.join(", ")}`);
        this.vertices = vertices;
        this.name = "NegativeCycleError";
    }
}

class WeightedGraph {
    constructor(vertexCount) {
        if (!Number.isSafeInteger(vertexCount) || vertexCount <= 0) {
            throw new GraphError("Vertex count must be a positive integer.");
        }

        this.vertexCount = vertexCount;
        this.adjacency = Array.from(
            { length: vertexCount },
            () => new Map()
        );

        this.version = 0;
    }

    validateVertex(vertex) {
        if (
            !Number.isSafeInteger(vertex) ||
            vertex < 0 ||
            vertex >= this.vertexCount
        ) {
            throw new GraphError(`Invalid vertex: ${vertex}`);
        }
    }

    addEdge(source, destination, weight) {
        this.validateVertex(source);
        this.validateVertex(destination);

        if (typeof weight !== "number" || !Number.isFinite(weight)) {
            throw new GraphError("Edge weight must be finite.");
        }

        const current = this.adjacency[source].get(destination);

        if (current === undefined || weight < current) {
            this.adjacency[source].set(destination, weight);
            this.version++;
        }
    }

    getEdges() {
        const edges = [];

        for (let source = 0; source < this.vertexCount; source++) {
            for (const [destination, weight] of this.adjacency[source]) {
                edges.push({ source, destination, weight });
            }
        }

        return edges;
    }
}

class FloydWarshallEngine extends EventEmitter {
    constructor(graph) {
        super();

        if (!(graph instanceof WeightedGraph)) {
            throw new TypeError("A WeightedGraph instance is required.");
        }

        this.graph = graph;
        this.result = null;
        this.computing = false;
    }

    initialize() {
        const n = this.graph.vertexCount;

        const distance = Array.from(
            { length: n },
            () => new Float64Array(n).fill(Infinity)
        );

        const next = Array.from(
            { length: n },
            () => new Int32Array(n).fill(-1)
        );

        for (let i = 0; i < n; i++) {
            distance[i][i] = 0;
            next[i][i] = i;
        }

        for (const edge of this.graph.getEdges()) {
            if (edge.weight < distance[edge.source][edge.destination]) {
                distance[edge.source][edge.destination] = edge.weight;
                next[edge.source][edge.destination] = edge.destination;
            }
        }

        return { distance, next };
    }

    async compute() {
        if (this.computing) {
            throw new GraphError("A computation is already running.");
        }

        this.computing = true;

        const graphVersion = this.graph.version;

        try {
            const { distance, next } = this.initialize();
            const n = this.graph.vertexCount;

            this.emit("computationStarted", { vertices: n });

            for (let k = 0; k < n; k++) {
                for (let i = 0; i < n; i++) {
                    const left = distance[i][k];

                    if (!Number.isFinite(left)) {
                        continue;
                    }

                    for (let j = 0; j < n; j++) {
                        const right = distance[k][j];

                        if (!Number.isFinite(right)) {
                            continue;
                        }

                        const candidate = left + right;

                        if (candidate < distance[i][j]) {
                            distance[i][j] = candidate;
                            next[i][j] = next[i][k];
                        }
                    }
                }

                this.emit("intermediateVertexProcessed", {
                    vertex: k,
                    totalVertices: n
                });

                // Yield between intermediate-vertex iterations.
                // This improves event-loop responsiveness, but does not
                // make the computation parallel.
                await new Promise(resolve => setImmediate(resolve));
            }

            if (this.graph.version !== graphVersion) {
                throw new GraphError(
                    "Graph changed during computation. Results discarded."
                );
            }

            const negativeVertices = [];

            for (let i = 0; i < n; i++) {
                if (distance[i][i] < 0) {
                    negativeVertices.push(i);
                }
            }

            if (negativeVertices.length > 0) {
                throw new NegativeCycleError(negativeVertices);
            }

            this.result = Object.freeze({
                distance,
                next,
                graphVersion
            });

            this.emit("computationCompleted", {
                vertices: n
            });

            return this.result;
        } catch (error) {
            this.result = null;
            this.emit("computationFailed", error);
            throw error;
        } finally {
            this.computing = false;
        }
    }

    validateResult() {
        if (!this.result) {
            throw new GraphError("No valid computation result exists.");
        }

        if (this.result.graphVersion !== this.graph.version) {
            throw new GraphError("Stored result is stale.");
        }
    }

    getDistance(source, destination) {
        this.graph.validateVertex(source);
        this.graph.validateVertex(destination);
        this.validateResult();

        return this.result.distance[source][destination];
    }

    getPath(source, destination) {
        this.graph.validateVertex(source);
        this.graph.validateVertex(destination);
        this.validateResult();

        const { distance, next } = this.result;

        if (!Number.isFinite(distance[source][destination])) {
            return null;
        }

        const path = [source];
        let current = source;

        for (let step = 0; step < this.graph.vertexCount; step++) {
            if (current === destination) {
                return path;
            }

            current = next[current][destination];

            if (current === -1) {
                return null;
            }

            path.push(current);
        }

        throw new GraphError("Path reconstruction exceeded graph size.");
    }

    printMatrix() {
        this.validateResult();

        console.log("\nAll-Pairs Shortest Distance Matrix");

        for (const row of this.result.distance) {
            console.log(
                Array.from(row).map(value =>
                    Number.isFinite(value) ? value : "INF"
                ).join("\t")
            );
        }
    }
}

async function main() {
    const graph = new WeightedGraph(5);

    const edges = [
        [0, 1, 3],
        [0, 2, 8],
        [0, 4, -4],
        [1, 3, 1],
        [1, 4, 7],
        [2, 1, 4],
        [3, 0, 2],
        [3, 2, -5],
        [4, 3, 6]
    ];

    for (const [source, destination, weight] of edges) {
        graph.addEdge(source, destination, weight);
    }

    const engine = new FloydWarshallEngine(graph);

    engine.on("computationStarted", event => {
        console.log(`Processing ${event.vertices} vertices.`);
    });

    engine.on("intermediateVertexProcessed", event => {
        console.log(
            `Intermediate vertex ${event.vertex} processed.`
        );
    });

    engine.on("computationCompleted", () => {
        console.log("All-pairs computation completed.");
    });

    engine.on("computationFailed", error => {
        console.error("Computation failed:", error.message);
    });

    await engine.compute();

    engine.printMatrix();

    console.log("\nShortest-path queries:");

    for (const [source, destination] of [
        [0, 2],
        [0, 3],
        [1, 2],
        [2, 4]
    ]) {
        console.log({
            source,
            destination,
            distance: engine.getDistance(source, destination),
            path: engine.getPath(source, destination)
        });
    }

    // Updating the graph invalidates the previous result.
    graph.addEdge(0, 3, 2);

    try {
        engine.getDistance(0, 3);
    } catch (error) {
        console.log("\nExpected stale-result error:", error.message);
    }

    // Negative cycle test.
    const cyclicGraph = new WeightedGraph(3);

    cyclicGraph.addEdge(0, 1, 1);
    cyclicGraph.addEdge(1, 2, -3);
    cyclicGraph.addEdge(2, 0, 1);

    const cyclicEngine = new FloydWarshallEngine(cyclicGraph);

    try {
        await cyclicEngine.compute();
    } catch (error) {
        if (error instanceof NegativeCycleError) {
            console.log("\nNegative cycle correctly detected.");
        } else {
            throw error;
        }
    }
}

main().catch(error => {
    console.error(error);
    process.exitCode = 1;
});
