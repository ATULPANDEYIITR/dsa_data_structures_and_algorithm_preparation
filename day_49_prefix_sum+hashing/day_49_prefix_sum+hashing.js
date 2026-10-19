"use strict";

/*
 * Prefix sum + hashing can be viewed as a state-matching problem:
 *
 *   currentState - previousState = desired interval property
 *
 * JavaScript's Map is useful because it preserves arbitrary prefix-state
 * keys without the prototype-related behavior of plain objects.
 */

function countSubarraysWithSum(values, target) {
    const frequency = new Map([[0, 1]]);
    let prefix = 0;
    let count = 0;

    for (const value of values) {
        if (!Number.isSafeInteger(value)) {
            throw new TypeError("Values must be safe integers.");
        }

        prefix += value;

        // Every earlier prefix equal to prefix-target creates a valid
        // subarray ending at the current position.
        const needed = prefix - target;
        count += frequency.get(needed) ?? 0;
        frequency.set(prefix, (frequency.get(prefix) ?? 0) + 1);
    }

    return count;
}

function findSubarraysWithSum(values, target) {
    const positions = new Map([[0, [-1]]]);
    const matches = [];
    let prefix = 0;

    for (let end = 0; end < values.length; end++) {
        prefix += values[end];
        const needed = prefix - target;

        const starts = positions.get(needed) ?? [];
        for (const startPrefixIndex of starts) {
            matches.push({
                start: startPrefixIndex + 1,
                end,
                values: values.slice(startPrefixIndex + 1, end + 1)
            });
        }

        if (!positions.has(prefix)) {
            positions.set(prefix, []);
        }
        positions.get(prefix).push(end);
    }

    return matches;
}

function countZeroSumSubarrays(values) {
    return countSubarraysWithSum(values, 0);
}

function longestZeroSumSubarray(values) {
    const earliest = new Map([[0, -1]]);
    let prefix = 0;
    let best = { length: 0, start: null, end: null };

    values.forEach((value, index) => {
        prefix += value;

        if (earliest.has(prefix)) {
            const start = earliest.get(prefix) + 1;
            const length = index - earliest.get(prefix);

            if (length > best.length) {
                best = { length, start, end: index };
            }
        } else {
            // Keeping the earliest occurrence maximizes future intervals.
            earliest.set(prefix, index);
        }
    });

    return best;
}

function validateBinary(values) {
    if (!values.every(value => value === 0 || value === 1)) {
        throw new TypeError("The equal-frequency binary algorithm requires 0 and 1.");
    }
}

function countEqualZeroOne(values) {
    validateBinary(values);

    // Equal zeros and ones become equal prefix balances after mapping
    // zero -> -1 and one -> +1.
    const frequency = new Map([[0, 1]]);
    let balance = 0;
    let count = 0;

    for (const value of values) {
        balance += value === 1 ? 1 : -1;
        count += frequency.get(balance) ?? 0;
        frequency.set(balance, (frequency.get(balance) ?? 0) + 1);
    }

    return count;
}

function equalFrequencyState(values, symbols) {
    if (!Array.isArray(symbols) || symbols.length < 2) {
        throw new Error("At least two distinct symbols are required.");
    }

    const uniqueSymbols = new Set(symbols);
    if (uniqueSymbols.size !== symbols.length) {
        throw new Error("Symbols must be unique.");
    }

    const allowed = uniqueSymbols;
    const reference = symbols[symbols.length - 1];

    // A state stores count(symbol)-count(reference) for every non-reference
    // symbol. Equal states at two prefixes imply equal frequencies inside
    // the interval.
    const state = new Map(symbols.slice(0, -1).map(symbol => [symbol, 0]));

    function stateKey() {
        return symbols
            .slice(0, -1)
            .map(symbol => state.get(symbol))
            .join(",");
    }

    const frequency = new Map([[stateKey(), 1]]);
    let count = 0;

    for (const value of values) {
        if (!allowed.has(value)) {
            throw new Error(`Unexpected symbol: ${value}`);
        }

        if (value === reference) {
            for (const symbol of symbols.slice(0, -1)) {
                state.set(symbol, state.get(symbol) - 1);
            }
        } else {
            state.set(value, state.get(value) + 1);
        }

        const key = stateKey();
        count += frequency.get(key) ?? 0;
        frequency.set(key, (frequency.get(key) ?? 0) + 1);
    }

    return count;
}

function longestEqualFrequency(values, symbols) {
    const reference = symbols[symbols.length - 1];
    const state = new Map(symbols.slice(0, -1).map(symbol => [symbol, 0]));

    function key() {
        return symbols.slice(0, -1).map(symbol => state.get(symbol)).join(",");
    }

    const earliest = new Map([[key(), -1]]);
    let best = { length: 0, start: null, end: null };

    for (let index = 0; index < values.length; index++) {
        const value = values[index];

        if (!symbols.includes(value)) {
            throw new Error(`Unexpected symbol: ${value}`);
        }

        if (value === reference) {
            for (const symbol of symbols.slice(0, -1)) {
                state.set(symbol, state.get(symbol) - 1);
            }
        } else {
            state.set(value, state.get(value) + 1);
        }

        const stateKey = key();

        if (earliest.has(stateKey)) {
            const length = index - earliest.get(stateKey);

            if (length > best.length) {
                best = {
                    length,
                    start: earliest.get(stateKey) + 1,
                    end: index
                };
            }
        } else {
            earliest.set(stateKey, index);
        }
    }

    return best;
}

class PullRequestWorkflow {
    constructor(number, baseBranch, sourceBranch) {
        this.number = number;
        this.baseBranch = baseBranch;
        this.sourceBranch = sourceBranch;
        this.draft = true;
        this.state = "OPEN";
        this.reviews = [];
        this.statusChecks = new Map();
        this.baseRevision = "base-1";
        this.sourceRevision = "head-1";
        this.conflict = false;
    }

    publish() {
        if (this.state !== "OPEN") {
            throw new Error("Only an open Pull Request can be published.");
        }
        this.draft = false;
        this.emit("ready_for_review");
    }

    requestReview(reviewer) {
        if (this.draft) {
            throw new Error("Draft Pull Requests are not ready for formal review.");
        }
        this.emit(`review_requested:${reviewer}`);
    }

    addReview(reviewer, state) {
        const allowed = new Set(["APPROVED", "CHANGES_REQUESTED", "COMMENTED"]);
        if (!allowed.has(state)) {
            throw new Error(`Invalid review state: ${state}`);
        }

        this.reviews.push({ reviewer, state, revision: this.sourceRevision });
        this.emit(`review:${state.toLowerCase()}:${reviewer}`);
    }

    setStatusCheck(name, passed) {
        this.statusChecks.set(name, Boolean(passed));
        this.emit(`check:${name}:${passed ? "passed" : "failed"}`);
    }

    updateSource(revision) {
        if (this.state !== "OPEN") {
            throw new Error("Closed Pull Requests cannot receive source updates.");
        }
        this.sourceRevision = revision;
        this.emit(`source_updated:${revision}`);
    }

    synchronizeWithBase(baseRevision, conflict) {
        this.baseRevision = baseRevision;
        this.conflict = conflict;
        this.emit(conflict ? "merge_conflict" : "base_synchronized");
    }

    resolveConflict() {
        if (!this.conflict) return;
        this.conflict = false;
        this.sourceRevision = `${this.sourceRevision}-rebased`;
        this.emit("conflict_resolved");
    }

    canMerge(policy) {
        if (this.state !== "OPEN" || this.draft || this.conflict) return false;

        for (const required of policy.requiredChecks) {
            if (this.statusChecks.get(required) !== true) return false;
        }

        const approvals = new Set(
            this.reviews
                .filter(review => review.state === "APPROVED")
                .map(review => review.reviewer)
        );

        return approvals.size >= policy.requiredApprovals;
    }

    merge(strategy, policy) {
        if (!this.canMerge(policy)) {
            throw new Error("Pull Request does not satisfy merge policy.");
        }

        if (!["merge", "squash", "rebase"].includes(strategy)) {
            throw new Error("Unsupported merge strategy.");
        }

        this.state = "MERGED";
        this.mergeStrategy = strategy;
        this.emit(`merged:${strategy}`);
    }

    close() {
        if (this.state !== "OPEN") {
            throw new Error("Only an open Pull Request can be closed.");
        }
        this.state = "CLOSED";
        this.emit("closed");
    }

    reopen() {
        if (this.state !== "CLOSED") {
            throw new Error("Only a closed Pull Request can be reopened.");
        }
        this.state = "OPEN";
        this.emit("reopened");
    }

    emit(event) {
        console.log(`[PR #${this.number}] ${event}`);
    }
}

function main() {
    console.log("=== Subarray Sum ===");
    const values = [2, -1, 2, 3, -2, 1];
    console.log("count:", countSubarraysWithSum(values, 3));
    console.log("matches:", findSubarraysWithSum(values, 3));

    console.log("\n=== Zero-Sum ===");
    console.log("count:", countZeroSumSubarrays([3, -1, -2, 4, -4]));
    console.log("longest:", longestZeroSumSubarray([3, -1, -2, 4, -4]));

    console.log("\n=== Equal Frequency ===");
    const binary = [0, 1, 0, 1, 1, 0];
    console.log("equal zero/one count:", countEqualZeroOne(binary));

    const letters = [..."AABBCABCCBA"];
    console.log(
        "A/B/C equal-frequency count:",
        equalFrequencyState(letters, ["A", "B", "C"])
    );
    console.log(
        "longest A/B/C equal-frequency interval:",
        longestEqualFrequency(letters, ["A", "B", "C"])
    );

    console.log("\n=== Event-Driven Pull Request Model ===");
    const policy = {
        requiredApprovals: 2,
        requiredChecks: ["unit-tests", "security-scan"]
    };

    const pullRequest = new PullRequestWorkflow(42, "main", "feature/prefix-state");
    pullRequest.publish();
    pullRequest.requestReview("alice");
    pullRequest.requestReview("bob");
    pullRequest.addReview("alice", "APPROVED");
    pullRequest.addReview("bob", "APPROVED");
    pullRequest.setStatusCheck("unit-tests", true);
    pullRequest.setStatusCheck("security-scan", true);
    pullRequest.synchronizeWithBase("base-2", true);
    console.log("merge eligible before conflict resolution:", pullRequest.canMerge(policy));
    pullRequest.resolveConflict();
    console.log("merge eligible after conflict resolution:", pullRequest.canMerge(policy));
    pullRequest.merge("squash", policy);
}

main();
