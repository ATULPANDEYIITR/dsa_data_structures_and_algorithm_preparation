"use strict";

/*
 * GRAPH ASSESSMENT ENGINE
 *
 * BFS, DFS, Connected Components, Cycle Detection,
 * Bipartite Graphs, and Topological Sorting.
 *
 * Runtime: Node.js 18+
 * Dependencies: Node.js standard library only.
 */

const EventEmitter = require("node:events");

class GraphError extends Error {
    constructor(message) {
        super(message);
        this.name = "GraphError";
    }
}

class Graph {
    constructor(vertices, directed = false) {
        if (!Array.isArray(vertices)) {
            throw new TypeError("Vertices must be an array.");
        }

        if (vertices.some(
            v => !Number.isSafeInteger(v)
        )) {
            throw new TypeError("Vertices must be safe integers.");
        }

        if (new Set(vertices).size !== vertices.length) {
            throw new GraphError("Duplicate vertices are not allowed.");
        }

        this.vertices = Object.freeze([...vertices]);
        this.directed = directed;
        this.adjacency = new Map();
        this.edges = new Set();

        for (const vertex of vertices) {
            this.adjacency.set(vertex, new Set());
        }
    }

    validateVertex(vertex) {
        if (!this.adjacency.has(vertex)) {
            throw new GraphError(`Unknown vertex: ${vertex}`);
        }
    }

    edgeKey(u, v) {
        if (this.directed) {
            return `${u}:${v}`;
        }

        return u <= v ? `${u}:${v}` : `${v}:${u}`;
    }

    addEdge(u, v) {
        this.validateVertex(u);
        this.validateVertex(v);

        const key = this.edgeKey(u, v);

        if (this.edges.has(key)) {
            return false;
        }

        this.edges.add(key);
        this.adjacency.get(u).add(v);

        if (!this.directed && u !== v) {
            this.adjacency.get(v).add(u);
        }

        return true;
    }

    removeEdge(u, v) {
        this.validateVertex(u);
        this.validateVertex(v);

        const key = this.edgeKey(u, v);

        if (!this.edges.has(key)) {
            return false;
        }

        this.edges.delete(key);
        this.adjacency.get(u).delete(v);

        if (!this.directed && u !== v) {
            this.adjacency.get(v).delete(u);
        }

        return true;
    }

    bfs(start) {
        this.validateVertex(start);

        const queue = [start];
        let head = 0;

        const visited = new Set([start]);
        const parent = new Map([[start, null]]);
        const distance = new Map([[start, 0]]);
        const order = [];

        // A moving head avoids repeated Array.shift() operations.
        while (head < queue.length) {
            const vertex = queue[head++];
            order.push(vertex);

            for (const neighbor of this.adjacency.get(vertex)) {
                if (!visited.has(neighbor)) {
                    visited.add(neighbor);
                    parent.set(neighbor, vertex);
                    distance.set(
                        neighbor,
                        distance.get(vertex) + 1
                    );
                    queue.push(neighbor);
                }
            }
        }

        return { order, parent, distance };
    }

    async *bfsEvents(start) {
        this.validateVertex(start);

        const queue = [start];
        let head = 0;
        const visited = new Set([start]);

        while (head < queue.length) {
            const vertex = queue[head++];

            yield {
                type: "vertex-visited",
                vertex
            };

            for (const neighbor of this.adjacency.get(vertex)) {
                if (!visited.has(neighbor)) {
                    visited.add(neighbor);
                    queue.push(neighbor);
                }
            }

            // Yielding to the event loop allows consumers to process
            // traversal events without blocking the application.
            await new Promise(resolve => setImmediate(resolve));
        }
    }

    dfs(start) {
        this.validateVertex(start);

        const visited = new Set([start]);
        const parent = new Map([[start, null]]);
        const order = [];
        const stack = [start];

        while (stack.length) {
            const vertex = stack.pop();
            order.push(vertex);

            const neighbors = [
                ...this.adjacency.get(vertex)
            ].reverse();

            for (const neighbor of neighbors) {
                if (!visited.has(neighbor)) {
                    visited.add(neighbor);
                    parent.set(neighbor, vertex);
                    stack.push(neighbor);
                }
            }
        }

        return { order, parent };
    }

    connectedComponents() {
        if (this.directed) {
            throw new GraphError(
                "Connected components require an undirected graph."
            );
        }

        const visited = new Set();
        const components = [];

        for (const start of this.vertices) {
            if (visited.has(start)) continue;

            const component = [];
            const queue = [start];
            let head = 0;

            visited.add(start);

            while (head < queue.length) {
                const vertex = queue[head++];
                component.push(vertex);

                for (const neighbor of this.adjacency.get(vertex)) {
                    if (!visited.has(neighbor)) {
                        visited.add(neighbor);
                        queue.push(neighbor);
                    }
                }
            }

            components.push(component);
        }

        return components;
    }

    hasUndirectedCycle() {
        if (this.directed) {
            throw new GraphError("Expected an undirected graph.");
        }

        const visited = new Set();

        for (const start of this.vertices) {
            if (visited.has(start)) continue;

            visited.add(start);
            const stack = [[start, null]];

            while (stack.length) {
                const [vertex, parent] = stack.pop();

                for (const neighbor of this.adjacency.get(vertex)) {
                    if (!visited.has(neighbor)) {
                        visited.add(neighbor);
                        stack.push([neighbor, vertex]);
                    } else if (neighbor !== parent) {
                        return true;
                    }
                }
            }
        }

        return false;
    }

    hasDirectedCycle() {
        if (!this.directed) {
            throw new GraphError("Expected a directed graph.");
        }

        // 0 = unvisited, 1 = active, 2 = completed.
        const state = new Map(
            this.vertices.map(v => [v, 0])
        );

        for (const start of this.vertices) {
            if (state.get(start) !== 0) continue;

            state.set(start, 1);

            const stack = [{
                vertex: start,
                iterator: this.adjacency.get(start).values()
            }];

            while (stack.length) {
                const frame = stack[stack.length - 1];
                const next = frame.iterator.next();

                if (next.done) {
                    state.set(frame.vertex, 2);
                    stack.pop();
                    continue;
                }

                const neighbor = next.value;

                if (state.get(neighbor) === 1) {
                    return true;
                }

                if (state.get(neighbor) === 0) {
                    state.set(neighbor, 1);

                    stack.push({
                        vertex: neighbor,
                        iterator: this.adjacency.get(neighbor).values()
                    });
                }
            }
        }

        return false;
    }

    isBipartite() {
        if (this.directed) {
            throw new GraphError(
                "Bipartite checking requires an undirected graph."
            );
        }

        const colors = new Map();

        for (const start of this.vertices) {
            if (colors.has(start)) continue;

            colors.set(start, 0);

            const queue = [start];
            let head = 0;

            while (head < queue.length) {
                const vertex = queue[head++];
                const currentColor = colors.get(vertex);

                for (const neighbor of this.adjacency.get(vertex)) {
                    if (!colors.has(neighbor)) {
                        colors.set(neighbor, 1 - currentColor);
                        queue.push(neighbor);
                    } else if (colors.get(neighbor) === currentColor) {
                        return {
                            bipartite: false,
                            colors
                        };
                    }
                }
            }
        }

        return {
            bipartite: true,
            colors
        };
    }

    topologicalSort() {
        if (!this.directed) {
            throw new GraphError(
                "Topological sorting requires a directed graph."
            );
        }

        const indegree = new Map(
            this.vertices.map(v => [v, 0])
        );

        for (const neighbors of this.adjacency.values()) {
            for (const neighbor of neighbors) {
                indegree.set(
                    neighbor,
                    indegree.get(neighbor) + 1
                );
            }
        }

        const queue = this.vertices.filter(
            v => indegree.get(v) === 0
        );

        let head = 0;
        const order = [];

        while (head < queue.length) {
            const vertex = queue[head++];
            order.push(vertex);

            for (const neighbor of this.adjacency.get(vertex)) {
                const degree = indegree.get(neighbor) - 1;
                indegree.set(neighbor, degree);

                if (degree === 0) {
                    queue.push(neighbor);
                }
            }
        }

        return {
            order,
            hasCycle: order.length !== this.vertices.length
        };
    }

    shortestPath(start, target) {
        this.validateVertex(start);
        this.validateVertex(target);

        const { parent } = this.bfs(start);

        if (!parent.has(target)) {
            return null;
        }

        const path = [];

        for (
            let current = target;
            current !== null;
            current = parent.get(current)
        ) {
            path.push(current);
        }

        return path.reverse();
    }
}


class GraphAssessmentService extends EventEmitter {
    constructor(graph) {
        super();

        if (!(graph instanceof Graph)) {
            throw new TypeError("A Graph instance is required.");
        }

        this.graph = graph;
        this.runCount = 0;
        this.history = [];
    }

    record(operation, result) {
        const record = Object.freeze({
            id: ++this.runCount,
            operation,
            timestamp: new Date().toISOString(),
            result
        });

        this.history.push(record);
        this.emit("assessment-completed", record);

        return record;
    }

    run(operation, ...args) {
        let result;

        switch (operation) {
            case "bfs":
                result = this.graph.bfs(...args);
                break;

            case "dfs":
                result = this.graph.dfs(...args);
                break;

            case "components":
                result = this.graph.connectedComponents();
                break;

            case "cycle":
                result = this.graph.directed
                    ? this.graph.hasDirectedCycle()
                    : this.graph.hasUndirectedCycle();
                break;

            case "bipartite":
                result = this.graph.isBipartite();
                break;

            case "topological":
                result = this.graph.topologicalSort();
                break;

            default:
                throw new GraphError(
                    `Unsupported operation: ${operation}`
                );
        }

        return this.record(operation, result);
    }

    async runBfsWithEvents(start) {
        const visited = [];

        for await (const event of this.graph.bfsEvents(start)) {
            visited.push(event.vertex);
            this.emit("traversal-event", event);
        }

        return this.record("async-bfs", visited);
    }

    getHistory() {
        return [...this.history];
    }
}


function assert(condition, message) {
    if (!condition) {
        throw new Error(`Test failed: ${message}`);
    }
}


async function main() {
    console.log("GRAPH ASSESSMENT ENGINE");
    console.log("=======================\n");

    const graph = new Graph(
        [1, 2, 3, 4, 5, 6, 7, 8],
        false
    );

    [
        [1, 2], [1, 3], [2, 4],
        [3, 4], [5, 6], [7, 8]
    ].forEach(edge => graph.addEdge(...edge));

    const service = new GraphAssessmentService(graph);

    service.on("assessment-completed", record => {
        console.log(
            `[EVENT] Assessment ${record.id}: ${record.operation}`
        );
    });

    console.log("BFS:", service.run("bfs", 1).result.order);
    console.log("DFS:", service.run("dfs", 1).result.order);

    console.log(
        "Components:",
        service.run("components").result
    );

    console.log(
        "Cycle:",
        service.run("cycle").result
    );

    console.log(
        "Bipartite:",
        service.run("bipartite").result.bipartite
    );

    console.log(
        "Shortest path:",
        graph.shortestPath(1, 4)
    );

    console.log("\nAsynchronous BFS:");

    service.on("traversal-event", event => {
        console.log("Visited:", event.vertex);
    });

    await service.runBfsWithEvents(1);

    // Directed dependency graph.
    console.log("\nDIRECTED DEPENDENCY GRAPH");

    const dag = new Graph([1, 2, 3, 4, 5, 6], true);

    [
        [1, 3], [2, 3], [3, 4],
        [3, 5], [4, 6], [5, 6]
    ].forEach(edge => dag.addEdge(...edge));

    const dependencyService = new GraphAssessmentService(dag);

    console.log(
        "Topological order:",
        dependencyService.run("topological").result.order
    );

    console.log(
        "Directed cycle:",
        dependencyService.run("cycle").result
    );

    dag.addEdge(6, 3);

    console.log(
        "After adding 6 -> 3:",
        dag.topologicalSort()
    );

    // Automated verification.
    const testGraph = new Graph([1, 2, 3, 4, 5], false);

    testGraph.addEdge(1, 2);
    testGraph.addEdge(2, 3);
    testGraph.addEdge(4, 5);

    assert(
        testGraph.connectedComponents().length === 2,
        "Connected components"
    );

    assert(
        testGraph.isBipartite().bipartite,
        "Bipartite graph"
    );

    assert(
        testGraph.shortestPath(1, 3).join(",") === "1,2,3",
        "Shortest path"
    );

    testGraph.addEdge(3, 1);

    assert(
        testGraph.hasUndirectedCycle(),
        "Undirected cycle"
    );

    assert(
        !testGraph.isBipartite().bipartite,
        "Odd cycle is not bipartite"
    );

    const cyclic = new Graph([1, 2, 3], true);
    cyclic.addEdge(1, 2);
    cyclic.addEdge(2, 3);
    cyclic.addEdge(3, 1);

    assert(
        cyclic.hasDirectedCycle(),
        "Directed cycle"
    );

    assert(
        cyclic.topologicalSort().hasCycle,
        "Topological cycle rejection"
    );

    assert(
        graph.shortestPath(1, 8) === null,
        "Unreachable vertex"
    );

    console.log("\nAll graph assessment tests passed.");
}

main().catch(error => {
    console.error("Graph assessment failed:", error.message);
    process.exitCode = 1;
});
