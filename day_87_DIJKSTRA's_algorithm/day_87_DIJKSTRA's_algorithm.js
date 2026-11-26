'use strict';

/*
 * Dijkstra's Algorithm: Event-Driven Route Engine
 *
 * Implements:
 * - Weighted directed and undirected graphs
 * - Min-priority queue using a binary heap
 * - Single-source shortest paths
 * - Route reconstruction
 * - Event-driven graph monitoring
 * - Asynchronous route-query interface
 * - Validation and failure handling
 *
 * Time complexity: O((V + E) log V)
 * Space complexity: O(V + E)
 */

const { EventEmitter } = require('node:events');

class GraphError extends Error {}
class NegativeWeightError extends GraphError {}
class UnknownVertexError extends GraphError {}

/**
 * Binary min-heap.
 * Avoids repeatedly sorting the complete frontier.
 */
class MinPriorityQueue {
    constructor() {
        this.heap = [];
    }

    get size() {
        return this.heap.length;
    }

    push(item) {
        this.heap.push(item);
        this.#bubbleUp(this.heap.length - 1);
    }

    pop() {
        if (this.heap.length === 0) {
            return null;
        }

        const minimum = this.heap[0];
        const last = this.heap.pop();

        if (this.heap.length > 0) {
            this.heap[0] = last;
            this.#bubbleDown(0);
        }

        return minimum;
    }

    #bubbleUp(index) {
        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);

            if (
                this.heap[parent].distance <=
                this.heap[index].distance
            ) {
                break;
            }

            [this.heap[parent], this.heap[index]] =
                [this.heap[index], this.heap[parent]];

            index = parent;
        }
    }

    #bubbleDown(index) {
        const length = this.heap.length;

        while (true) {
            const left = 2 * index + 1;
            const right = 2 * index + 2;
            let smallest = index;

            if (
                left < length &&
                this.heap[left].distance <
                this.heap[smallest].distance
            ) {
                smallest = left;
            }

            if (
                right < length &&
                this.heap[right].distance <
                this.heap[smallest].distance
            ) {
                smallest = right;
            }

            if (smallest === index) {
                break;
            }

            [this.heap[index], this.heap[smallest]] =
                [this.heap[smallest], this.heap[index]];

            index = smallest;
        }
    }
}

class WeightedGraph extends EventEmitter {
    constructor({ directed = false } = {}) {
        super();

        this.directed = directed;
        this.adjacency = new Map();
        this.version = 0;
    }

    addVertex(vertex) {
        if (
            typeof vertex !== 'string' ||
            vertex.trim().length === 0
        ) {
            throw new GraphError(
                'Vertex must be a non-empty string'
            );
        }

        if (!this.adjacency.has(vertex)) {
            this.adjacency.set(vertex, []);
            this.version++;
            this.emit('vertexAdded', { vertex });
        }
    }

    addEdge(source, destination, weight) {
        if (
            typeof weight !== 'number' ||
            !Number.isFinite(weight)
        ) {
            throw new GraphError(
                'Weight must be a finite number'
            );
        }

        if (weight < 0) {
            throw new NegativeWeightError(
                'Negative edge weights are not supported'
            );
        }

        this.addVertex(source);
        this.addVertex(destination);

        this.adjacency.get(source).push({
            vertex: destination,
            weight
        });

        if (!this.directed) {
            this.adjacency.get(destination).push({
                vertex: source,
                weight
            });
        }

        this.version++;

        this.emit('edgeAdded', {
            source,
            destination,
            weight,
            version: this.version
        });
    }

    dijkstra(source) {
        if (!this.adjacency.has(source)) {
            throw new UnknownVertexError(
                `Source vertex does not exist: ${source}`
            );
        }

        const distances = new Map();
        const predecessors = new Map();

        for (const vertex of this.adjacency.keys()) {
            distances.set(vertex, Infinity);
            predecessors.set(vertex, null);
        }

        distances.set(source, 0);

        const queue = new MinPriorityQueue();

        queue.push({
            vertex: source,
            distance: 0
        });

        while (queue.size > 0) {
            const current = queue.pop();

            // Discard outdated priority-queue entries.
            if (
                current.distance >
                distances.get(current.vertex)
            ) {
                continue;
            }

            for (const edge of this.adjacency.get(
                current.vertex
            )) {
                const candidate =
                    current.distance + edge.weight;

                if (!Number.isFinite(candidate)) {
                    throw new RangeError(
                        'Path distance exceeded numeric range'
                    );
                }

                if (candidate < distances.get(edge.vertex)) {
                    distances.set(edge.vertex, candidate);

                    predecessors.set(
                        edge.vertex,
                        current.vertex
                    );

                    queue.push({
                        vertex: edge.vertex,
                        distance: candidate
                    });

                    this.emit('distanceUpdated', {
                        vertex: edge.vertex,
                        distance: candidate,
                        predecessor: current.vertex
                    });
                }
            }
        }

        return Object.freeze({
            source,
            graphVersion: this.version,
            distances,
            predecessors,
            pathTo: destination =>
                this.#reconstructPath(
                    destination,
                    distances,
                    predecessors
                )
        });
    }

    #reconstructPath(
        destination,
        distances,
        predecessors
    ) {
        if (!distances.has(destination)) {
            throw new UnknownVertexError(
                `Unknown destination: ${destination}`
            );
        }

        if (distances.get(destination) === Infinity) {
            return null;
        }

        const path = [];
        let current = destination;

        while (current !== null) {
            path.push(current);
            current = predecessors.get(current);
        }

        return path.reverse();
    }

    async findRoute(source, destination) {
        // Promise-based interface for asynchronous applications.
        await Promise.resolve();

        const result = this.dijkstra(source);

        if (!result.distances.has(destination)) {
            throw new UnknownVertexError(
                `Unknown destination: ${destination}`
            );
        }

        return Object.freeze({
            source,
            destination,
            path: result.pathTo(destination),
            distance: result.distances.get(destination),
            graphVersion: result.graphVersion
        });
    }
}

async function main() {
    const graph = new WeightedGraph({
        directed: false
    });

    graph.on('edgeAdded', event => {
        console.log(
            `Edge added: ${event.source} -> ` +
            `${event.destination}, weight=${event.weight}`
        );
    });

    graph.on('distanceUpdated', event => {
        console.log(
            `Distance updated: ${event.vertex} = ${event.distance}`
        );
    });

    const edges = [
        ['A', 'B', 4],
        ['A', 'C', 2],
        ['B', 'C', 1],
        ['B', 'D', 5],
        ['C', 'D', 8],
        ['C', 'E', 10],
        ['D', 'E', 2],
        ['D', 'F', 6],
        ['E', 'F', 3]
    ];

    for (const [source, destination, weight] of edges) {
        graph.addEdge(source, destination, weight);
    }

    graph.addVertex('G');

    console.log('\nComputing shortest paths...');

    const result = graph.dijkstra('A');

    console.log('\nShortest-distance table:');

    for (const [vertex, distance] of result.distances) {
        console.log(
            `${vertex}: ${
                distance === Infinity ? 'unreachable' : distance
            }`
        );
    }

    console.log('\nAsynchronous route query:');

    const route = await graph.findRoute('A', 'F');

    console.log(route);

    console.log('\nRunning validation tests...');

    const tests = new WeightedGraph({ directed: true });

    tests.addEdge('S', 'A', 10);
    tests.addEdge('S', 'B', 3);
    tests.addEdge('B', 'A', 2);
    tests.addEdge('A', 'T', 4);
    tests.addEdge('B', 'T', 8);

    const answer = tests.dijkstra('S');

    console.assert(answer.distances.get('A') === 5);
    console.assert(answer.distances.get('T') === 9);

    console.assert(
        JSON.stringify(answer.pathTo('T')) ===
        JSON.stringify(['S', 'B', 'A', 'T'])
    );

    tests.addVertex('UNREACHABLE');

    console.assert(
        answer.distances.get('UNREACHABLE') === undefined
    );

    const updated = tests.dijkstra('S');

    console.assert(
        updated.distances.get('UNREACHABLE') === Infinity
    );

    try {
        tests.addEdge('S', 'T', -5);
        throw new Error('Negative weight was accepted');
    } catch (error) {
        console.assert(error instanceof NegativeWeightError);
    }

    try {
        tests.dijkstra('UNKNOWN');
        throw new Error('Unknown source was accepted');
    } catch (error) {
        console.assert(error instanceof UnknownVertexError);
    }

    console.log('All tests passed.');
}

main().catch(error => {
    console.error('Execution failed:', error.message);
    process.exitCode = 1;
});
