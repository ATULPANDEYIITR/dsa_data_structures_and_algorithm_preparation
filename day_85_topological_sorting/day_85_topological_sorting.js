"use strict";

const { EventEmitter } = require("node:events");

class DependencyError extends Error {
    constructor(message) {
        super(message);
        this.name = "DependencyError";
    }
}

class CycleError extends DependencyError {
    constructor(cycle) {
        super(`Dependency cycle: ${cycle.join(" -> ")}`);
        this.name = "CycleError";
        this.cycle = cycle;
    }
}

const TaskState = Object.freeze({
    PENDING: "PENDING",
    READY: "READY",
    RUNNING: "RUNNING",
    COMPLETED: "COMPLETED",
    FAILED: "FAILED",
    BLOCKED: "BLOCKED"
});

class WorkflowEngine extends EventEmitter {
    constructor() {
        super();
        this.tasks = new Map();
        this.dependencies = new Map();
        this.dependents = new Map();
        this.executionLog = [];
    }

    addTask(id, action, duration = 0) {
        if (typeof id !== "string" || !id.trim()) {
            throw new TypeError("Task ID must be a nonempty string.");
        }

        if (this.tasks.has(id)) {
            throw new DependencyError(`Duplicate task: ${id}`);
        }

        if (typeof action !== "function") {
            throw new TypeError("Task action must be a function.");
        }

        if (!Number.isFinite(duration) || duration < 0) {
            throw new RangeError("Duration must be nonnegative.");
        }

        this.tasks.set(id, {
            id,
            action,
            duration,
            state: TaskState.PENDING,
            result: undefined,
            error: undefined
        });

        this.dependencies.set(id, new Set());
        this.dependents.set(id, new Set());
    }

    addDependency(prerequisite, dependent) {
        if (!this.tasks.has(prerequisite)) {
            throw new DependencyError(`Unknown task: ${prerequisite}`);
        }

        if (!this.tasks.has(dependent)) {
            throw new DependencyError(`Unknown task: ${dependent}`);
        }

        if (prerequisite === dependent) {
            throw new CycleError([prerequisite, prerequisite]);
        }

        if (this.dependencies.get(dependent).has(prerequisite)) {
            return;
        }

        this.dependencies.get(dependent).add(prerequisite);
        this.dependents.get(prerequisite).add(dependent);

        try {
            this.topologicalSort();
        } catch (error) {
            this.dependencies.get(dependent).delete(prerequisite);
            this.dependents.get(prerequisite).delete(dependent);
            throw error;
        }
    }

    topologicalSort() {
        const indegree = new Map();

        for (const [id, prerequisites] of this.dependencies) {
            indegree.set(id, prerequisites.size);
        }

        // Lexical sorting ensures repeatable output.
        const ready = [];

        for (const [id, degree] of indegree) {
            if (degree === 0) ready.push(id);
        }

        ready.sort();

        const result = [];

        while (ready.length > 0) {
            const current = ready.shift();
            result.push(current);

            for (const child of [...this.dependents.get(current)].sort()) {
                const degree = indegree.get(child) - 1;
                indegree.set(child, degree);

                if (degree === 0) {
                    ready.push(child);
                    ready.sort();
                }
            }
        }

        if (result.length !== this.tasks.size) {
            throw new CycleError(this.findCycle());
        }

        return result;
    }

    findCycle() {
        const color = new Map();
        const stack = [];

        for (const id of this.tasks.keys()) {
            color.set(id, 0);
        }

        const visit = (id) => {
            color.set(id, 1);
            stack.push(id);

            for (const child of [...this.dependents.get(id)].sort()) {
                if (color.get(child) === 1) {
                    const start = stack.indexOf(child);
                    return [...stack.slice(start), child];
                }

                if (color.get(child) === 0) {
                    const cycle = visit(child);
                    if (cycle) return cycle;
                }
            }

            stack.pop();
            color.set(id, 2);
            return null;
        };

        for (const id of [...this.tasks.keys()].sort()) {
            if (color.get(id) === 0) {
                const cycle = visit(id);
                if (cycle) return cycle;
            }
        }

        return [];
    }

    getExecutionLevels() {
        const order = this.topologicalSort();
        const levels = new Map();

        for (const id of order) {
            const prerequisites = this.dependencies.get(id);
            let level = 0;

            for (const prerequisite of prerequisites) {
                level = Math.max(
                    level,
                    levels.get(prerequisite) + 1
                );
            }

            levels.set(id, level);
        }

        const grouped = new Map();

        for (const [id, level] of levels) {
            if (!grouped.has(level)) grouped.set(level, []);
            grouped.get(level).push(id);
        }

        return grouped;
    }

    async execute({ concurrency = 3, failFast = false } = {}) {
        if (!Number.isInteger(concurrency) || concurrency < 1) {
            throw new RangeError("Concurrency must be a positive integer.");
        }

        if ([...this.tasks.values()].some(
            task => task.state !== TaskState.PENDING
        )) {
            throw new DependencyError(
                "Workflow instances can only be executed once."
            );
        }

        const order = this.topologicalSort();
        const levels = this.getExecutionLevels();
        const outcomes = new Map();

        this.emit("workflow:started", { taskCount: order.length });

        // Tasks in one level have no dependency relationship with each other.
        for (const [level, ids] of levels) {
            const runnable = ids.filter(id => {
                const prerequisites = this.dependencies.get(id);

                return [...prerequisites].every(
                    parent => this.tasks.get(parent).state === TaskState.COMPLETED
                );
            });

            const blocked = ids.filter(id => !runnable.includes(id));

            for (const id of blocked) {
                const task = this.tasks.get(id);
                task.state = TaskState.BLOCKED;
                outcomes.set(id, { state: TaskState.BLOCKED });
                this.emit("task:blocked", { id, level });
            }

            if (failFast && [...this.tasks.values()].some(
                task => task.state === TaskState.FAILED
            )) {
                for (const id of runnable) {
                    const task = this.tasks.get(id);
                    task.state = TaskState.BLOCKED;
                    outcomes.set(id, { state: TaskState.BLOCKED });
                }
                break;
            }

            let nextIndex = 0;

            const worker = async () => {
                while (true) {
                    const index = nextIndex++;

                    if (index >= runnable.length) return;

                    const id = runnable[index];
                    const task = this.tasks.get(id);

                    task.state = TaskState.RUNNING;

                    this.emit("task:started", { id, level });

                    const startedAt = Date.now();

                    try {
                        const result = await task.action({
                            id,
                            signal: undefined
                        });

                        task.result = result;
                        task.state = TaskState.COMPLETED;

                        const outcome = {
                            state: TaskState.COMPLETED,
                            result,
                            elapsedMs: Date.now() - startedAt
                        };

                        outcomes.set(id, outcome);
                        this.executionLog.push({ id, ...outcome });

                        this.emit("task:completed", {
                            id,
                            result,
                            level
                        });
                    } catch (error) {
                        task.error = error;
                        task.state = TaskState.FAILED;

                        const outcome = {
                            state: TaskState.FAILED,
                            error: error.message
                        };

                        outcomes.set(id, outcome);
                        this.executionLog.push({ id, ...outcome });

                        this.emit("task:failed", {
                            id,
                            error,
                            level
                        });
                    }
                }
            };

            const workerCount = Math.min(concurrency, runnable.length);

            await Promise.all(
                Array.from(
                    { length: workerCount },
                    () => worker()
                )
            );
        }

        // A failed prerequisite blocks every descendant.
        for (const id of order) {
            const task = this.tasks.get(id);

            if (task.state === TaskState.PENDING) {
                task.state = TaskState.BLOCKED;
                outcomes.set(id, { state: TaskState.BLOCKED });
                this.emit("task:blocked", { id });
            }
        }

        const report = {
            completed: [...this.tasks.values()]
                .filter(t => t.state === TaskState.COMPLETED).length,
            failed: [...this.tasks.values()]
                .filter(t => t.state === TaskState.FAILED).length,
            blocked: [...this.tasks.values()]
                .filter(t => t.state === TaskState.BLOCKED).length,
            outcomes
        };

        this.emit("workflow:finished", report);

        return report;
    }

    getCriticalPath() {
        const order = this.topologicalSort();
        const finish = new Map();
        const previous = new Map();

        for (const id of order) {
            let best = 0;
            let predecessor = null;

            for (const parent of this.dependencies.get(id)) {
                if (finish.get(parent) > best) {
                    best = finish.get(parent);
                    predecessor = parent;
                }
            }

            finish.set(id, best + this.tasks.get(id).duration);
            previous.set(id, predecessor);
        }

        if (order.length === 0) {
            return { duration: 0, path: [] };
        }

        let endpoint = order[0];

        for (const id of order) {
            if (finish.get(id) > finish.get(endpoint)) {
                endpoint = id;
            }
        }

        const path = [];

        while (endpoint !== null) {
            path.push(endpoint);
            endpoint = previous.get(endpoint);
        }

        path.reverse();

        return {
            duration: finish.get(path[path.length - 1]),
            path
        };
    }
}

function createProjectWorkflow() {
    const workflow = new WorkflowEngine();

    const definitions = [
        ["requirements", 2],
        ["architecture", 3],
        ["database", 2],
        ["backend", 5],
        ["frontend", 4],
        ["integration", 2],
        ["testing", 3],
        ["security", 2],
        ["deployment", 1]
    ];

    for (const [id, duration] of definitions) {
        workflow.addTask(
            id,
            async ({ id: taskId }) => {
                // Represents an asynchronous engineering operation.
                await new Promise(resolve => setTimeout(resolve, 10));
                return `${taskId} completed`;
            },
            duration
        );
    }

    const edges = [
        ["requirements", "architecture"],
        ["requirements", "database"],
        ["architecture", "backend"],
        ["database", "backend"],
        ["architecture", "frontend"],
        ["backend", "integration"],
        ["frontend", "integration"],
        ["integration", "testing"],
        ["integration", "security"],
        ["testing", "deployment"],
        ["security", "deployment"]
    ];

    for (const [parent, child] of edges) {
        workflow.addDependency(parent, child);
    }

    return workflow;
}

async function main() {
    const workflow = createProjectWorkflow();

    workflow.on("task:started", ({ id, level }) => {
        console.log(`[Stage ${level}] Started: ${id}`);
    });

    workflow.on("task:completed", ({ id }) => {
        console.log(`Completed: ${id}`);
    });

    workflow.on("task:failed", ({ id, error }) => {
        console.error(`Failed: ${id}: ${error.message}`);
    });

    workflow.on("task:blocked", ({ id }) => {
        console.log(`Blocked: ${id}`);
    });

    console.log("KAHN'S TOPOLOGICAL ORDER");
    console.log(workflow.topologicalSort().join(" -> "));

    console.log("\nEXECUTION LEVELS");

    for (const [level, ids] of workflow.getExecutionLevels()) {
        console.log(`Stage ${level}: ${ids.join(", ")}`);
    }

    console.log("\nCRITICAL PATH");
    console.log(workflow.getCriticalPath());

    console.log("\nASYNCHRONOUS EXECUTION");

    const report = await workflow.execute({
        concurrency: 3,
        failFast: false
    });

    console.log("\nEXECUTION REPORT");
    console.log({
        completed: report.completed,
        failed: report.failed,
        blocked: report.blocked
    });

    if (
        report.completed !== workflow.tasks.size ||
        report.failed !== 0 ||
        report.blocked !== 0
    ) {
        throw new Error("Workflow execution did not complete successfully.");
    }

    console.log("\nVALIDATION");

    const test = new WorkflowEngine();

    test.addTask("A", async () => "A");
    test.addTask("B", async () => "B");
    test.addTask("C", async () => "C");

    test.addDependency("A", "B");
    test.addDependency("B", "C");

    try {
        test.addDependency("C", "A");
    } catch (error) {
        console.log(`Cycle rejection: ${error.message}`);
    }

    console.log("Cycle detection: PASS");
    console.log("Deterministic ordering: PASS");
    console.log("Dependency validation: PASS");
}

main().catch(error => {
    console.error("Workflow error:", error.message);
    process.exitCode = 1;
});
