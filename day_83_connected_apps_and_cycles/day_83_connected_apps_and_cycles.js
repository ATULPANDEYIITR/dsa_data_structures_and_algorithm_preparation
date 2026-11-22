'use strict';

/*
 * Connected Components and Cycles in Graphs
 *
 * Event-driven graph analysis using Node.js.
 *
 * Features:
 * - Undirected connected components.
 * - Undirected cycle detection with Union-Find.
 * - Directed cycle detection using iterative DFS.
 * - Directed cycle detection using Kahn's algorithm.
 * - Asynchronous graph-analysis pipeline.
 * - Validation and structured reporting.
 *
 * Run:
 * node connected_components_cycles.js
 */

const GraphKind = Object.freeze({
    DIRECTED: 'directed',
    UNDIRECTED: 'undirected'
});

class GraphError extends Error {
    constructor(message) {
        super(message);
        this.name = 'GraphError';
    }
}

class Graph {
    #adjacency = new Map();

    constructor(kind = GraphKind.UNDIRECTED) {
        if (!Object.values(GraphKind).includes(kind)) {
            throw new GraphError('Invalid graph type.');
        }

        this.kind = kind;
    }

    addVertex(vertex) {
        if (!Number.isSafeInteger(vertex)) {
            throw new GraphError('Vertices must be safe integers.');
        }

        if (!this.#adjacency.has(vertex)) {
            this.#adjacency.set(vertex, []);
        }

        return this;
    }

    addEdge(source, destination) {
        this.addVertex(source);
        this.addVertex(destination);

        this.#adjacency.get(source).push(destination);

        if (
            this.kind === GraphKind.UNDIRECTED &&
            source !== destination
        ) {
            this.#adjacency.get(destination).push(source);
        }

        return this;
    }

    get vertices() {
        return [...this.#adjacency.keys()];
    }

    neighbors(vertex) {
        const result = this.#adjacency.get(vertex);

        if (!result) {
            throw new GraphError(`Unknown vertex: ${vertex}`);
        }

        return result;
    }

    get size() {
        return this.#adjacency.size;
    }

    validate() {
        for (const [vertex, neighbors] of this.#adjacency) {
            if (!Array.isArray(neighbors)) {
                throw new GraphError(
                    `Invalid adjacency list for ${vertex}`
                );
            }

            for (const neighbor of neighbors) {
                if (!this.#adjacency.has(neighbor)) {
                    throw new GraphError(
                        `Unknown neighbor: ${neighbor}`
                    );
                }
            }
        }
    }

    getUndirectedEdges() {
        if (this.kind !== GraphKind.UNDIRECTED) {
            throw new GraphError('Expected an undirected graph.');
        }

        const edges = [];

        for (const [source, neighbors] of this.#adjacency) {
            for (const destination of neighbors) {
                if (source <= destination) {
                    edges.push([source, destination]);
                }
            }
        }

        return edges;
    }
}

class DisjointSet {
    constructor(vertices) {
        this.parent = new Map();
        this.rank = new Map();
        this.components = vertices.length;

        for (const vertex of vertices) {
            this.parent.set(vertex, vertex);
            this.rank.set(vertex, 0);
        }
    }

    find(vertex) {
        if (!this.parent.has(vertex)) {
            throw new GraphError(`Unknown vertex: ${vertex}`);
        }

        let root = vertex;

        while (this.parent.get(root) !== root) {
            root = this.parent.get(root);
        }

        // Iterative path compression avoids recursive call depth.
        let current = vertex;

        while (this.parent.get(current) !== current) {
            const next = this.parent.get(current);
            this.parent.set(current, root);
            current = next;
        }

        return root;
    }

    union(first, second) {
        let rootA = this.find(first);
        let rootB = this.find(second);

        if (rootA === rootB) {
            return false;
        }

        const rankA = this.rank.get(rootA);
        const rankB = this.rank.get(rootB);

        if (rankA < rankB) {
            [rootA, rootB] = [rootB, rootA];
        }

        this.parent.set(rootB, rootA);

        if (rankA === rankB) {
            this.rank.set(rootA, this.rank.get(rootA) + 1);
        }

        this.components--;

        return true;
    }
}

class GraphAnalyzer {
    static connectedComponents(graph) {
        this.validateKind(graph, GraphKind.UNDIRECTED);
        graph.validate();

        const visited = new Set();
        const components = [];

        for (const start of graph.vertices) {
            if (visited.has(start)) {
                continue;
            }

            const component = [];
            const stack = [start];

            visited.add(start);

            while (stack.length > 0) {
                const vertex = stack.pop();
                component.push(vertex);

                for (const neighbor of graph.neighbors(vertex)) {
                    if (!visited.has(neighbor)) {
                        visited.add(neighbor);
                        stack.push(neighbor);
                    }
                }
            }

            component.sort((a, b) => a - b);
            components.push(component);
        }

        return components;
    }

    static undirectedCycleUnionFind(graph) {
        this.validateKind(graph, GraphKind.UNDIRECTED);
        graph.validate();

        const dsu = new DisjointSet(graph.vertices);

        for (const [source, destination] of graph.getUndirectedEdges()) {
            if (!dsu.union(source, destination)) {
                return {
                    hasCycle: true,
                    method: 'union-find'
                };
            }
        }

        return {
            hasCycle: false,
            method: 'union-find'
        };
    }

    static directedCycleDFS(graph) {
        this.validateKind(graph, GraphKind.DIRECTED);
        graph.validate();

        const WHITE = 0;
        const GRAY = 1;
        const BLACK = 2;

        const colors = new Map(
            graph.vertices.map(vertex => [vertex, WHITE])
        );

        const parent = new Map();

        for (const start of graph.vertices) {
            if (colors.get(start) !== WHITE) {
                continue;
            }

            colors.set(start, GRAY);
            parent.set(start, null);

            const stack = [{
                vertex: start,
                index: 0
            }];

            while (stack.length > 0) {
                const frame = stack[stack.length - 1];
                const neighbors = graph.neighbors(frame.vertex);

                if (frame.index >= neighbors.length) {
                    colors.set(frame.vertex, BLACK);
                    stack.pop();
                    continue;
                }

                const neighbor = neighbors[frame.index++];

                if (colors.get(neighbor) === WHITE) {
                    colors.set(neighbor, GRAY);
                    parent.set(neighbor, frame.vertex);

                    stack.push({
                        vertex: neighbor,
                        index: 0
                    });
                } else if (colors.get(neighbor) === GRAY) {
                    const cycle = [neighbor];
                    let current = frame.vertex;

                    while (current !== neighbor) {
                        cycle.push(current);
                        current = parent.get(current);
                    }

                    cycle.push(neighbor);
                    cycle.reverse();

                    return {
                        hasCycle: true,
                        cycle
                    };
                }
            }
        }

        return {
            hasCycle: false,
            cycle: null
        };
    }

    static directedCycleKahn(graph) {
        this.validateKind(graph, GraphKind.DIRECTED);
        graph.validate();

        const indegree = new Map(
            graph.vertices.map(vertex => [vertex, 0])
        );

        for (const vertex of graph.vertices) {
            for (const neighbor of graph.neighbors(vertex)) {
                indegree.set(
                    neighbor,
                    indegree.get(neighbor) + 1
                );
            }
        }

        // Array-backed queue avoids repeated shift() operations.
        const queue = [];

        for (const [vertex, degree] of indegree) {
            if (degree === 0) {
                queue.push(vertex);
            }
        }

        let head = 0;
        let processed = 0;

        while (head < queue.length) {
            const vertex = queue[head++];
            processed++;

            for (const neighbor of graph.neighbors(vertex)) {
                const nextDegree = indegree.get(neighbor) - 1;
                indegree.set(neighbor, nextDegree);

                if (nextDegree === 0) {
                    queue.push(neighbor);
                }
            }
        }

        return {
            hasCycle: processed !== graph.size,
            processedVertices: processed,
            totalVertices: graph.size
        };
    }

    static validateKind(graph, expected) {
        if (!(graph instanceof Graph)) {
            throw new GraphError('Invalid graph instance.');
        }

        if (graph.kind !== expected) {
            throw new GraphError(
                `Expected ${expected} graph.`
            );
        }
    }
}

/*
 * Event-driven monitoring pipeline.
 * Each analysis stage publishes a result to its listeners.
 */
class GraphAnalysisPipeline {
    #listeners = new Map();

    on(event, callback) {
        if (typeof callback !== 'function') {
            throw new TypeError('Listener must be a function.');
        }

        if (!this.#listeners.has(event)) {
            this.#listeners.set(event, new Set());
        }

        this.#listeners.get(event).add(callback);

        return () => this.#listeners.get(event)?.delete(callback);
    }

    emit(event, payload) {
        for (const callback of this.#listeners.get(event) ?? []) {
            callback(payload);
        }
    }

    async analyzeUndirected(graph) {
        const report = {
            componentCount: 0,
            components: [],
            hasCycle: false
        };

        try {
            await Promise.resolve();

            report.components =
                GraphAnalyzer.connectedComponents(graph);

            report.componentCount = report.components.length;

            this.emit('components', report.components);

            report.hasCycle =
                GraphAnalyzer.undirectedCycleUnionFind(graph).hasCycle;

            this.emit('cycle', report.hasCycle);

            return Object.freeze(report);
        } catch (error) {
            this.emit('error', error);
            throw error;
        }
    }

    async analyzeDirected(graph) {
        try {
            await Promise.resolve();

            const dfs = GraphAnalyzer.directedCycleDFS(graph);
            const kahn = GraphAnalyzer.directedCycleKahn(graph);

            if (dfs.hasCycle !== kahn.hasCycle) {
                throw new Error(
                    'Cycle detection algorithms produced inconsistent results.'
                );
            }

            const report = Object.freeze({
                hasCycle: dfs.hasCycle,
                cycle: dfs.cycle,
                processedVertices: kahn.processedVertices
            });

            this.emit('directedAnalysis', report);

            return report;
        } catch (error) {
            this.emit('error', error);
            throw error;
        }
    }
}

async function main() {
    const pipeline = new GraphAnalysisPipeline();

    pipeline.on('components', components => {
        console.log('Connected components:', components);
    });

    pipeline.on('cycle', hasCycle => {
        console.log('Undirected cycle:', hasCycle);
    });

    pipeline.on('directedAnalysis', report => {
        console.log('Directed analysis:', report);
    });

    pipeline.on('error', error => {
        console.error('Analysis failed:', error.message);
    });

    const undirected = new Graph();

    [
        [1, 2],
        [2, 3],
        [3, 1],
        [4, 5],
        [6, 7]
    ].forEach(edge => undirected.addEdge(...edge));

    undirected.addVertex(8);

    const undirectedReport =
        await pipeline.analyzeUndirected(undirected);

    console.log(
        'Undirected component count:',
        undirectedReport.componentCount
    );

    const directed = new Graph(GraphKind.DIRECTED);

    [
        [1, 2],
        [2, 3],
        [3, 4],
        [4, 2],
        [4, 5],
        [6, 7]
    ].forEach(edge => directed.addEdge(...edge));

    await pipeline.analyzeDirected(directed);

    // Acyclic directed graph.
    const dag = new Graph(GraphKind.DIRECTED);

    [
        [1, 2],
        [1, 3],
        [2, 4],
        [3, 4]
    ].forEach(edge => dag.addEdge(...edge));

    const dagReport = await pipeline.analyzeDirected(dag);

    if (dagReport.hasCycle) {
        throw new Error('Expected an acyclic graph.');
    }

    // Edge cases.
    const selfLoop = new Graph();
    selfLoop.addEdge(9, 9);

    if (
        !GraphAnalyzer.undirectedCycleUnionFind(
            selfLoop
        ).hasCycle
    ) {
        throw new Error('Self-loop was not detected.');
    }

    const empty = new Graph();

    if (GraphAnalyzer.connectedComponents(empty).length !== 0) {
        throw new Error('Empty graph must have zero components.');
    }

    console.log('All JavaScript checks passed.');
}

main().catch(error => {
    console.error(error.stack);
    process.exitCode = 1;
});
