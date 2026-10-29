"use strict";

const assert = require("node:assert/strict");

const EMPTY = 0;
const DIGITS = new Set([1, 2, 3, 4, 5, 6, 7, 8, 9]);

class SudokuError extends Error {}

class SudokuBoard {
    constructor(board) {
        this.validateShape(board);
        this.board = board.map(row => [...row]);
        this.rows = Array.from({ length: 9 }, () => new Set());
        this.cols = Array.from({ length: 9 }, () => new Set());
        this.boxes = Array.from({ length: 9 }, () => new Set());
        this.loadConstraints();
    }

    validateShape(board) {
        if (!Array.isArray(board) || board.length !== 9) {
            throw new SudokuError("Sudoku requires nine rows.");
        }

        for (const row of board) {
            if (!Array.isArray(row) || row.length !== 9) {
                throw new SudokuError("Every row must contain nine cells.");
            }

            for (const value of row) {
                if (!Number.isInteger(value) || value < 0 || value > 9) {
                    throw new SudokuError("Cells must contain integers from 0 through 9.");
                }
            }
        }
    }

    boxIndex(row, col) {
        return Math.floor(row / 3) * 3 + Math.floor(col / 3);
    }

    loadConstraints() {
        for (let row = 0; row < 9; row++) {
            for (let col = 0; col < 9; col++) {
                const value = this.board[row][col];

                if (value === EMPTY) continue;

                const box = this.boxIndex(row, col);

                if (
                    this.rows[row].has(value) ||
                    this.cols[col].has(value) ||
                    this.boxes[box].has(value)
                ) {
                    throw new SudokuError(
                        `Duplicate value ${value} at row ${row}, column ${col}.`
                    );
                }

                this.rows[row].add(value);
                this.cols[col].add(value);
                this.boxes[box].add(value);
            }
        }
    }

    candidates(row, col) {
        if (this.board[row][col] !== EMPTY) {
            return new Set();
        }

        const used = new Set([
            ...this.rows[row],
            ...this.cols[col],
            ...this.boxes[this.boxIndex(row, col)]
        ]);

        return new Set([...DIGITS].filter(value => !used.has(value)));
    }

    findMostConstrainedCell() {
        let best = null;

        for (let row = 0; row < 9; row++) {
            for (let col = 0; col < 9; col++) {
                if (this.board[row][col] !== EMPTY) continue;

                const options = this.candidates(row, col);

                if (options.size === 0) {
                    return { row, col, options };
                }

                if (best === null || options.size < best.options.size) {
                    best = { row, col, options };
                }

                if (options.size === 1) return best;
            }
        }

        return best;
    }

    place(row, col, value) {
        const box = this.boxIndex(row, col);

        this.board[row][col] = value;
        this.rows[row].add(value);
        this.cols[col].add(value);
        this.boxes[box].add(value);
    }

    undo(row, col, value) {
        const box = this.boxIndex(row, col);

        this.board[row][col] = EMPTY;
        this.rows[row].delete(value);
        this.cols[col].delete(value);
        this.boxes[box].delete(value);
    }
}

class SudokuSolver {
    constructor(board) {
        this.sudoku = new SudokuBoard(board);
        this.decisions = 0;
        this.backtracks = 0;
    }

    backtrack() {
        const cell = this.sudoku.findMostConstrainedCell();

        if (cell === null) {
            return true;
        }

        if (cell.options.size === 0) {
            return false;
        }

        for (const value of [...cell.options].sort((a, b) => a - b)) {
            this.decisions++;
            this.sudoku.place(cell.row, cell.col, value);

            if (this.backtrack()) {
                return true;
            }

            this.sudoku.undo(cell.row, cell.col, value);
            this.backtracks++;
        }

        return false;
    }

    solve() {
        const started = process.hrtime.bigint();
        const solved = this.backtrack();
        const elapsedMs = Number(process.hrtime.bigint() - started) / 1e6;

        return {
            solved,
            board: this.sudoku.board.map(row => [...row]),
            decisions: this.decisions,
            backtracks: this.backtracks,
            elapsedMs
        };
    }
}

async function evaluatePolicy(policy, context) {
    if (!policy || typeof policy !== "object") {
        throw new TypeError("Policy must be an object.");
    }

    const checks = [
        ["requiredReviews", context.approvals >= policy.requiredReviews],
        ["checks", context.failedChecks === 0],
        ["openConversations", context.openConversations === 0]
    ];

    await new Promise(resolve => setImmediate(resolve));

    return {
        eligible: checks.every(([, passed]) => passed),
        checks: Object.fromEntries(checks)
    };
}

function subsetsWithTarget(values, target) {
    if (!Array.isArray(values) || !Number.isInteger(target)) {
        throw new TypeError("Invalid subset-sum input.");
    }

    const sorted = [...values].sort((a, b) => a - b);
    const result = [];
    const path = [];

    function backtrack(start, remaining) {
        if (remaining === 0) {
            result.push([...path]);
            return;
        }

        if (remaining < 0) return;

        for (let i = start; i < sorted.length; i++) {
            if (i > start && sorted[i] === sorted[i - 1]) continue;
            if (sorted[i] > remaining) break;

            path.push(sorted[i]);
            backtrack(i + 1, remaining - sorted[i]);
            path.pop();
        }
    }

    backtrack(0, target);
    return result;
}

function printBoard(board) {
    for (let row = 0; row < 9; row++) {
        if (row > 0 && row % 3 === 0) {
            console.log("------+-------+------");
        }

        const formatted = board[row].map(value => value || ".").join(" ");
        console.log(
            formatted.slice(0, 5) +
            " | " +
            board[row].slice(3, 6).map(value => value || ".").join(" ") +
            " | " +
            board[row].slice(6).map(value => value || ".").join(" ")
        );
    }
}

async function main() {
    const puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ];

    console.log("Original Sudoku:");
    printBoard(puzzle);

    const result = new SudokuSolver(puzzle).solve();

    console.log("\nSolved Sudoku:");
    printBoard(result.board);
    console.log(
        `\nSolved=${result.solved}, decisions=${result.decisions}, ` +
        `backtracks=${result.backtracks}, time=${result.elapsedMs.toFixed(3)} ms`
    );

    assert.equal(result.solved, true);
    assert.equal(result.board.flat().includes(0), false);

    console.log("\nSubset-sum:");
    console.log(subsetsWithTarget([2, 3, 5, 6, 8], 10));

    const policyResult = await evaluatePolicy(
        { requiredReviews: 2 },
        { approvals: 2, failedChecks: 0, openConversations: 0 }
    );

    console.log("\nAsynchronous policy evaluation:");
    console.log(policyResult);
}

main().catch(error => {
    console.error(`Execution failed: ${error.message}`);
    process.exitCode = 1;
});
