"use strict";

/*
 * Graph Fundamentals: Event-Driven Graph Analysis Engine.
 *
 * Features:
 * - Directed and undirected graphs
 * - Weighted and unweighted edges
 * - Vertex and edge management
 * - Degree calculations
 * - Adjacency lists and matrices
 * - BFS and DFS
 * - Connected components
 * - Cycle detection
 * - Dijkstra shortest paths
 * - Event-driven graph modifications
 * - Graph validation and snapshots
 *
 * Runtime: Node.js 18+
 */

const { EventEmitter } = require("node:events");
const fs = require("node:fs/promises");

class GraphError extends Error {}
class VertexNotFoundError extends GraphError {}
class InvalidEdgeError extends GraphError {}

const GraphType = Object.freeze({
    DIRECTED: "directed",
    UNDIRECTED: "undirected"
});

class Graph extends EventEmitter {
    #adjacency = new Map();
    #edgeCount = 0;
    #version = 0;

    constructor({
        type = GraphType.UNDIRECTED,
        weighted = false
    } = {}) {
        super();

        if (!Object.values(GraphType).includes(type)) {
            throw new GraphError("Invalid graph type.");
        }

        this.type = type;
        this.weighted = Boolean(weighted);
    }

    get vertexCount() {
        return this.#adjacency.size;
    }

    get edgeCount() {
        return this.#edgeCount;
    }

    get version() {
        return this.#version;
    }

    get vertices() {
        return [...this.#adjacency.keys()];
    }

    #validateVertex(vertex) {
        if (
            vertex === null ||
            vertex === undefined ||
            !["string", "number", "bigint"].includes(typeof vertex)
        ) {
            throw new GraphError(
                "Vertices must be non-null strings, numbers, or bigints."
            );
        }

        if (typeof vertex === "number" && !Number.isFinite(vertex)) {
            throw new GraphError("Numeric vertices must be finite.");
        }
    }

    #requireVertex(vertex) {
        if (!this.#adjacency.has(vertex)) {
            throw new VertexNotFoundError(
                `Vertex not found: ${String(vertex)}`
            );
        }
    }

    #changed(event, details) {
        this.#version++;

        this.emit("change", {
            event,
            version: this.#version,
            ...details
        });
    }

    addVertex(vertex) {
        this.#validateVertex(vertex);

        if (this.#adjacency.has(vertex)) {
            return false;
        }

        this.#adjacency.set(vertex, new Map());

        this.#changed("vertex-added", { vertex });
        return true;
    }

    addEdge(source, target, weight = 1) {
        this.#validateVertex(source);
        this.#validateVertex(target);

        if (
            typeof weight !== "number" ||
            !Number.isFinite(weight)
        ) {
            throw new InvalidEdgeError(
                "Weight must be a finite number."
            );
        }

        if (!this.weighted && weight !== 1) {
            throw new InvalidEdgeError(
                "Unweighted graph edges must have weight 1."
            );
        }

        this.addVertex(source);
        this.addVertex(target);

        const exists = this.#adjacency.get(source).has(target);

        this.#adjacency.get(source).set(target, weight);

        if (this.type === GraphType.UNDIRECTED) {
            this.#adjacency.get(target).set(source, weight);
        }

        if (!exists) {
            this.#edgeCount++;
        }

        this.#changed("edge-added", {
            source,
            target,
            weight,
            replaced: exists
        });
    }

    removeEdge(source, target) {
        this.#requireVertex(source);
        this.#requireVertex(target);

        if (!this.#adjacency.get(source).has(target)) {
            return false;
        }

        this.#adjacency.get(source).delete(target);

        if (this.type === GraphType.UNDIRECTED) {
            this.#adjacency.get(target).delete(source);
        }

        this.#edgeCount--;

        this.#changed("edge-removed", { source, target });
        return true;
    }

    removeVertex(vertex) {
        this.#requireVertex(vertex);

        if (this.type === GraphType.DIRECTED) {
            const outgoing = this.#adjacency.get(vertex).size;

            let incoming = 0;

            for (const neighbors of this.#adjacency.values()) {
                if (neighbors.has(vertex)) {
                    incoming++;
                    neighbors.delete(vertex);
                }
            }

            this.#edgeCount -= outgoing + incoming;
        } else {
            this.#edgeCount -= this.#adjacency.get(vertex).size;

            for (const neighbors of this.#adjacency.values()) {
                neighbors.delete(vertex);
            }
        }

        this.#adjacency.delete(vertex);

        this.#changed("vertex-removed", { vertex });
    }

    neighbors(vertex) {
        this.#requireVertex(vertex);

        return new Map(this.#adjacency.get(vertex));
    }

    degree(vertex) {
        this.#requireVertex(vertex);

        if (this.type !== GraphType.UNDIRECTED) {
            throw new GraphError(
                "Use inDegree and outDegree for directed graphs."
            );
        }

        return this.#adjacency.get(vertex).size;
    }

    inDegree(vertex) {
        this.#requireVertex(vertex);

        if (this.type !== GraphType.DIRECTED) {
            throw new GraphError("In-degree requires a directed graph.");
        }

        let degree = 0;

        for (const neighbors of this.#adjacency.values()) {
            if (neighbors.has(vertex)) {
                degree++;
            }
        }

        return degree;
    }

    outDegree(vertex) {
        this.#requireVertex(vertex);

        if (this.type !== GraphType.DIRECTED) {
            throw new GraphError("Out-degree requires a directed graph.");
        }

        return this.#adjacency.get(vertex).size;
    }

    bfs(start) {
        this.#requireVertex(start);

        const visited = new Set([start]);
        const queue = [start];
        const result = [];

        let head = 0;

        while (head < queue.length) {
            const current = queue[head++];
            result.push(current);

            for (const neighbor of this.#adjacency.get(current).keys()) {
                if (!visited.has(neighbor)) {
                    visited.add(neighbor);
                    queue.push(neighbor);
                }
            }
        }

        return result;
    }

    dfs(start) {
        this.#requireVertex(start);

        const visited = new Set();
        const stack = [start];
        const result = [];

        while (stack.length) {
            const current = stack.pop();

            if (visited.has(current)) {
                continue;
            }

            visited.add(current);
            result.push(current);

            const neighbors = [
                ...this.#adjacency.get(current).keys()
            ];

            for (let i = neighbors.length - 1; i >= 0; i--) {
                if (!visited.has(neighbors[i])) {
                    stack.push(neighbors[i]);
                }
            }
        }

        return result;
    }

    connectedComponents() {
        if (this.type !== GraphType.UNDIRECTED) {
            throw new GraphError(
                "Connected components require an undirected graph."
            );
        }

        const visited = new Set();
        const components = [];

        for (const vertex of this.#adjacency.keys()) {
            if (!visited.has(vertex)) {
                const component = this.bfs(vertex);
                components.push(component);

                for (const member of component) {
                    visited.add(member);
                }
            }
        }

        return components;
    }

    hasCycle() {
        if (this.type === GraphType.UNDIRECTED) {
            const visited = new Set();

            const visit = (vertex, parent) => {
                visited.add(vertex);

                for (const neighbor of this.#adjacency.get(vertex).keys()) {
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

            for (const vertex of this.#adjacency.keys()) {
                if (!visited.has(vertex) && visit(vertex, undefined)) {
                    return true;
                }
            }

            return false;
        }

        const colors = new Map(
            [...this.#adjacency.keys()].map(vertex => [vertex, 0])
        );

        const visit = vertex => {
            colors.set(vertex, 1);

            for (const neighbor of this.#adjacency.get(vertex).keys()) {
                if (colors.get(neighbor) === 1) {
                    return true;
                }

                if (
                    colors.get(neighbor) === 0 &&
                    visit(neighbor)
                ) {
                    return true;
                }
            }

            colors.set(vertex, 2);
            return false;
        };

        for (const vertex of this.#adjacency.keys()) {
            if (colors.get(vertex) === 0 && visit(vertex)) {
                return true;
            }
        }

        return false;
    }

    dijkstra(start) {
        this.#requireVertex(start);

        for (const neighbors of this.#adjacency.values()) {
            for (const weight of neighbors.values()) {
                if (weight < 0) {
                    throw new GraphError(
                        "Dijkstra requires non-negative weights."
                    );
                }
            }
        }

        const distances = new Map();

        for (const vertex of this.#adjacency.keys()) {
            distances.set(vertex, Infinity);
        }

        distances.set(start, 0);

        // A binary heap avoids repeatedly sorting the entire queue.
        const heap = new MinHeap();

        heap.push({ vertex: start, distance: 0 });

        while (!heap.isEmpty()) {
            const current = heap.pop();

            if (current.distance !== distances.get(current.vertex)) {
                continue;
            }

            for (
                const [neighbor, weight]
                of this.#adjacency.get(current.vertex)
            ) {
                const candidate = current.distance + weight;

                if (candidate < distances.get(neighbor)) {
                    distances.set(neighbor, candidate);

                    heap.push({
                        vertex: neighbor,
                        distance: candidate
                    });
                }
            }
        }

        return distances;
    }

    adjacencyMatrix() {
        const vertices = this.vertices;
        const index = new Map(
            vertices.map((vertex, i) => [vertex, i])
        );

        const matrix = Array.from(
            { length: vertices.length },
            () => Array(vertices.length).fill(null)
        );

        for (const [source, neighbors] of this.#adjacency) {
            for (const [target, weight] of neighbors) {
                matrix[index.get(source)][index.get(target)] = weight;
            }
        }

        return { vertices, matrix };
    }

    snapshot() {
        return {
            type: this.type,
            weighted: this.weighted,
            version: this.#version,
            vertices: this.vertices,
            edges: [...this.#adjacency].flatMap(
                ([source, neighbors]) =>
                    [...neighbors].filter(
                        ([target]) =>
                            this.type === GraphType.DIRECTED ||
                            this.vertices.indexOf(source) <=
                            this.vertices.indexOf(target)
                    ).map(([target, weight]) => ({
                        source,
                        target,
                        weight
                    }))
            )
        };
    }

    async saveToFile(filename) {
        const data = JSON.stringify(this.snapshot(), null, 2);

        await fs.writeFile(filename, data, {
            encoding: "utf8",
            mode: 0o600
        });
    }
}

class MinHeap {
    #items = [];

    isEmpty() {
        return this.#items.length === 0;
    }

    push(item) {
        this.#items.push(item);

        let index = this.#items.length - 1;

        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);

            if (
                this.#items[parent].distance <= item.distance
            ) {
                break;
            }

            this.#items[index] = this.#items[parent];
            index = parent;
        }

        this.#items[index] = item;
    }

    pop() {
        if (this.isEmpty()) {
            throw new GraphError("Cannot remove from an empty heap.");
        }

        const minimum = this.#items[0];
        const last = this.#items.pop();

        if (this.#items.length > 0) {
            let index = 0;

            while (true) {
                const left = index * 2 + 1;
                const right = index * 2 + 2;
                let smallest = index;

                if (
                    left < this.#items.length &&
                    this.#items[left].distance <
                    this.#items[smallest].distance
                ) {
                    smallest = left;
                }

                if (
                    right < this.#items.length &&
                    this.#items[right].distance <
                    this.#items[smallest].distance
                ) {
                    smallest = right;
                }

                if (smallest === index) {
                    break;
                }

                [
                    this.#items[index],
                    this.#items[smallest]
                ] = [
                    this.#items[smallest],
                    this.#items[index]
                ];

                index = smallest;
            }

            // The replacement root is already handled by heap ordering.
            if (last !== undefined) {
                // Rebuild through insertion to preserve heap invariants.
                this.#items.pop();
                this.push(last);
            }
        }

        return minimum;
    }
}

async function main() {
    const graph = new Graph({
        type: GraphType.UNDIRECTED,
        weighted: false
    });

    graph.on("change", event => {
        console.log(
            `[EVENT] ${event.event} | version=${event.version}`
        );
    });

    console.log("\n=== UNDIRECTED GRAPH ===");

    [
        ["A", "B"],
        ["A", "C"],
        ["B", "D"],
        ["C", "D"],
        ["D", "E"]
    ].forEach(([source, target]) => {
        graph.addEdge(source, target);
    });

    graph.addVertex("isolated");

    console.log("Vertices:", graph.vertices);
    console.log("Edge count:", graph.edgeCount);
    console.log("Degree of D:", graph.degree("D"));
    console.log("BFS:", graph.bfs("A"));
    console.log("DFS:", graph.dfs("A"));
    console.log("Components:", graph.connectedComponents());
    console.log("Contains cycle:", graph.hasCycle());

    console.log("\n=== DIRECTED GRAPH ===");

    const directed = new Graph({
        type: GraphType.DIRECTED
    });

    directed.addEdge("A", "B");
    directed.addEdge("A", "C");
    directed.addEdge("C", "B");

    console.log("In-degree B:", directed.inDegree("B"));
    console.log("Out-degree A:", directed.outDegree("A"));

    console.log("\n=== WEIGHTED GRAPH ===");

    const weighted = new Graph({
        type: GraphType.UNDIRECTED,
        weighted: true
    });

    [
        ["A", "B", 4],
        ["A", "C", 2],
        ["C", "B", 1],
        ["B", "D", 5],
        ["D", "E", 2]
    ].forEach(([source, target, weight]) => {
        weighted.addEdge(source, target, weight);
    });

    console.log(
        "Shortest distances:",
        Object.fromEntries(weighted.dijkstra("A"))
    );

    console.log("\n=== ADJACENCY MATRIX ===");
    console.log(graph.adjacencyMatrix());

    console.log("\n=== VALIDATION ===");

    try {
        graph.addEdge("A", "B", 5);
    } catch (error) {
        console.log("Expected validation:", error.message);
    }

    try {
        weighted.addEdge("X", "Y", -10);
        weighted.dijkstra("X");
    } catch (error) {
        console.log("Expected algorithm error:", error.message);
    }

    // A separate snapshot is persisted as structured JSON.
    await graph.saveToFile("graph_snapshot.json");

    console.log("\nGraph snapshot saved.");
    console.log("All demonstrations completed.");
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
