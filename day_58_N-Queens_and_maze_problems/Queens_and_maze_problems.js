"use strict";

class Position {
    constructor(row, col) {
        if (!Number.isInteger(row) || !Number.isInteger(col)) {
            throw new TypeError("row and col must be integers");
        }
        this.row = row;
        this.col = col;
    }

    key() {
        return `${this.row},${this.col}`;
    }
}

class NQueensSolver {
    constructor(n) {
        if (!Number.isInteger(n) || n < 1 || n > 14) {
            throw new RangeError("n must be an integer between 1 and 14");
        }
        this.n = n;
        this.solutions = [];
    }

    solve() {
        this.solutions = [];

        const columns = new Set();
        const descending = new Set(); // row - col
        const ascending = new Set();  // row + col
        const placement = Array(this.n).fill(-1);

        const backtrack = (row) => {
            if (row === this.n) {
                this.solutions.push([...placement]);
                return;
            }

            for (let col = 0; col < this.n; col++) {
                const d1 = row - col;
                const d2 = row + col;

                if (
                    columns.has(col) ||
                    descending.has(d1) ||
                    ascending.has(d2)
                ) {
                    continue;
                }

                placement[row] = col;
                columns.add(col);
                descending.add(d1);
                ascending.add(d2);

                backtrack(row + 1);

                placement[row] = -1;
                columns.delete(col);
                descending.delete(d1);
                ascending.delete(d2);
            }
        };

        backtrack(0);
        return this.solutions;
    }

    count() {
        let count = 0;
        const columns = new Set();
        const descending = new Set();
        const ascending = new Set();

        const backtrack = (row) => {
            if (row === this.n) {
                count++;
                return;
            }

            for (let col = 0; col < this.n; col++) {
                const d1 = row - col;
                const d2 = row + col;

                if (
                    columns.has(col) ||
                    descending.has(d1) ||
                    ascending.has(d2)
                ) {
                    continue;
                }

                columns.add(col);
                descending.add(d1);
                ascending.add(d2);

                backtrack(row + 1);

                columns.delete(col);
                descending.delete(d1);
                ascending.delete(d2);
            }
        };

        backtrack(0);
        return count;
    }

    render(solution) {
        if (
            !Array.isArray(solution) ||
            solution.length !== this.n
        ) {
            throw new Error("invalid solution");
        }

        return solution
            .map((queenColumn) => {
                if (!Number.isInteger(queenColumn) ||
                    queenColumn < 0 ||
                    queenColumn >= this.n) {
                    throw new Error("invalid queen position");
                }

                return Array.from(
                    { length: this.n },
                    (_, col) => col === queenColumn ? "Q" : "."
                ).join(" ");
            })
            .join("\n");
    }
}

class Maze {
    constructor(grid) {
        if (!Array.isArray(grid) || grid.length === 0) {
            throw new TypeError("maze must contain at least one row");
        }

        const width = grid[0].length;
        if (width === 0) {
            throw new Error("maze rows cannot be empty");
        }

        for (const row of grid) {
            if (typeof row !== "string" || row.length !== width) {
                throw new Error("maze must be rectangular");
            }
            if (!/^[.#]+$/.test(row)) {
                throw new Error("maze may contain only '.' and '#'");
            }
        }

        this.grid = grid;
        this.rows = grid.length;
        this.cols = width;
    }

    valid(position) {
        return (
            position.row >= 0 &&
            position.row < this.rows &&
            position.col >= 0 &&
            position.col < this.cols &&
            this.grid[position.row][position.col] === "."
        );
    }

    allPaths(start, target, maxPaths = 10000) {
        if (!Number.isInteger(maxPaths) || maxPaths < 1) {
            throw new RangeError("maxPaths must be positive");
        }

        if (!this.valid(start) || !this.valid(target)) {
            return [];
        }

        const paths = [];
        const path = [start];
        const visited = new Set([start.key()]);

        const directions = [
            [-1, 0],
            [1, 0],
            [0, -1],
            [0, 1]
        ];

        const backtrack = (current) => {
            if (paths.length >= maxPaths) {
                return;
            }

            if (current.row === target.row && current.col === target.col) {
                paths.push([...path]);
                return;
            }

            for (const [dr, dc] of directions) {
                const next = new Position(
                    current.row + dr,
                    current.col + dc
                );

                const key = next.key();

                if (!this.valid(next) || visited.has(key)) {
                    continue;
                }

                visited.add(key);
                path.push(next);

                backtrack(next);

                path.pop();
                visited.delete(key);
            }
        };

        backtrack(start);
        return paths;
    }

    shortestPath(start, target) {
        if (!this.valid(start) || !this.valid(target)) {
            return null;
        }

        const queue = [start];
        let head = 0;
        const previous = new Map([[start.key(), null]]);
        const directions = [
            [-1, 0],
            [1, 0],
            [0, -1],
            [0, 1]
        ];

        while (head < queue.length) {
            const current = queue[head++];

            if (current.row === target.row && current.col === target.col) {
                const path = [];
                let key = current.key();

                while (key !== null) {
                    const [row, col] = key.split(",").map(Number);
                    path.push(new Position(row, col));
                    key = previous.get(key);
                }

                return path.reverse();
            }

            for (const [dr, dc] of directions) {
                const next = new Position(
                    current.row + dr,
                    current.col + dc
                );
                const key = next.key();

                if (!this.valid(next) || previous.has(key)) {
                    continue;
                }

                previous.set(key, current.key());
                queue.push(next);
            }
        }

        return null;
    }

    renderPath(path) {
        const cells = new Set(path.map((p) => p.key()));

        return this.grid
            .map((row, r) =>
                Array.from(row, (cell, c) =>
                    cells.has(`${r},${c}`) ? "*" : cell
                ).join(" ")
            )
            .join("\n");
    }
}

function validateQueensSolution(solution) {
    const n = solution.length;
    if (n === 0) return false;

    const columns = new Set();
    const descending = new Set();
    const ascending = new Set();

    for (let row = 0; row < n; row++) {
        const col = solution[row];

        if (!Number.isInteger(col) || col < 0 || col >= n) {
            return false;
        }

        if (
            columns.has(col) ||
            descending.has(row - col) ||
            ascending.has(row + col)
        ) {
            return false;
        }

        columns.add(col);
        descending.add(row - col);
        ascending.add(row + col);
    }

    return true;
}

async function main() {
    console.log("=== N-Queens ===");

    const solver = new NQueensSolver(4);
    const solutions = solver.solve();

    if (solutions.length !== 2) {
        throw new Error("unexpected number of 4-Queens solutions");
    }

    for (const [index, solution] of solutions.entries()) {
        if (!validateQueensSolution(solution)) {
            throw new Error("invalid N-Queens solution");
        }

        console.log(`\nSolution ${index + 1}`);
        console.log(solver.render(solution));
    }

    console.log(`\nTotal solutions: ${solver.count()}`);

    console.log("\n=== Maze Path Generation ===");

    const maze = new Maze([
        "...#.",
        ".#...",
        "...#.",
        "#....",
        "....."
    ]);

    const start = new Position(0, 0);
    const target = new Position(4, 4);

    const paths = maze.allPaths(start, target, 5);
    console.log(`Generated paths: ${paths.length}`);

    paths.forEach((path, index) => {
        console.log(`\nPath ${index + 1}, length=${path.length}`);
        console.log(maze.renderPath(path));
    });

    const shortest = maze.shortestPath(start, target);

    if (!shortest) {
        throw new Error("expected a reachable target");
    }

    console.log(`\nShortest path length: ${shortest.length}`);
    console.log(maze.renderPath(shortest));

    if (new NQueensSolver(1).count() !== 1) {
        throw new Error("1-Queens test failed");
    }

    if (new NQueensSolver(2).count() !== 0) {
        throw new Error("2-Queens test failed");
    }

    if (new NQueensSolver(3).count() !== 0) {
        throw new Error("3-Queens test failed");
    }

    const blocked = new Maze([
        ".#",
        "#."
    ]);

    if (
        blocked.allPaths(
            new Position(0, 0),
            new Position(1, 1)
        ).length !== 0
    ) {
        throw new Error("blocked-maze test failed");
    }

    console.log("\nAll validation checks passed.");
}

main().catch((error) => {
    console.error(`Failure: ${error.message}`);
    process.exitCode = 1;
});
