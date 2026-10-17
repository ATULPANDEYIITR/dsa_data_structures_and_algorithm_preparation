"use strict";

/*
 * Maps and sets for repository analytics.
 * Run with Node.js 18 or later: node maps_sets.js
 *
 * Map preserves explicit key-value relationships. Set stores distinct
 * values. This program also demonstrates streaming event processing,
 * object identity, safe aggregation, and set-based access analysis.
 */

function heading(title) {
    console.log(`\n${"=".repeat(68)}\n${title}\n${"=".repeat(68)}`);
}

function countOccurrences(iterable) {
    const counts = new Map();

    for (const value of iterable) {
        counts.set(value, (counts.get(value) ?? 0) + 1);
    }

    return counts;
}

function uniqueValues(iterable) {
    return [...new Set(iterable)];
}

function duplicateValues(iterable) {
    const seen = new Set();
    const duplicates = new Set();

    for (const value of iterable) {
        if (seen.has(value)) {
            duplicates.add(value);
        } else {
            seen.add(value);
        }
    }

    return duplicates;
}

function intersection(first, second) {
    const right = second instanceof Set ? second : new Set(second);
    const result = new Set();

    for (const value of first) {
        if (right.has(value)) {
            result.add(value);
        }
    }

    return result;
}

function union(first, second) {
    return new Set([...first, ...second]);
}

function difference(first, second) {
    const right = second instanceof Set ? second : new Set(second);
    return new Set([...first].filter(value => !right.has(value)));
}

function symmetricDifference(first, second) {
    return union(difference(first, second), difference(second, first));
}

function membershipIndex(values) {
    return new Set(values);
}

function formatMap(map) {
    return Object.fromEntries(map);
}

class RepositoryEventProcessor {
    #events = [];
    #eventCounts = new Map();
    #reviewersByPullRequest = new Map();
    #failedChecks = new Set();

    ingest(event) {
        if (!event || typeof event !== "object") {
            throw new TypeError("Event must be an object.");
        }

        const { pullRequestId, actor, eventType } = event;

        if (!Number.isInteger(pullRequestId) || pullRequestId < 1) {
            throw new RangeError("Pull request ID must be a positive integer.");
        }

        if (typeof actor !== "string" || actor.trim() === "") {
            throw new TypeError("Actor must be a non-empty string.");
        }

        const validTypes = new Set([
            "opened",
            "reviewed",
            "check_failed",
            "check_passed",
            "merged",
            "closed"
        ]);

        if (!validTypes.has(eventType)) {
            throw new RangeError(`Unsupported event type: ${eventType}`);
        }

        const stored = Object.freeze({
            pullRequestId,
            actor: actor.trim(),
            eventType
        });

        this.#events.push(stored);

        const key = `${pullRequestId}:${eventType}`;
        this.#eventCounts.set(key, (this.#eventCounts.get(key) ?? 0) + 1);

        if (eventType === "reviewed") {
            if (!this.#reviewersByPullRequest.has(pullRequestId)) {
                this.#reviewersByPullRequest.set(pullRequestId, new Set());
            }

            this.#reviewersByPullRequest.get(pullRequestId).add(stored.actor);
        }

        if (eventType === "check_failed") {
            this.#failedChecks.add(pullRequestId);
        }

        // A failure remains in this set until a corresponding passing check
        // is received, illustrating an event-driven current-state projection.
        if (eventType === "check_passed") {
            this.#failedChecks.delete(pullRequestId);
        }
    }

    countEvents(pullRequestId, eventType) {
        return this.#eventCounts.get(`${pullRequestId}:${eventType}`) ?? 0;
    }

    reviewers(pullRequestId) {
        return new Set(this.#reviewersByPullRequest.get(pullRequestId) ?? []);
    }

    get failedPullRequests() {
        return new Set(this.#failedChecks);
    }

    eventsFor(pullRequestId) {
        return this.#events.filter(event => event.pullRequestId === pullRequestId);
    }
}

async function processEventStream(events, processor) {
    // An async iterator supports future integration with queues and streams.
    for await (const event of events) {
        processor.ingest(event);
    }
}

async function main() {
    heading("Frequency counting and duplicate detection");

    const changedFiles = [
        "src/auth.js",
        "src/router.js",
        "src/auth.js",
        "tests/auth.test.js",
        "src/router.js",
        "README.md"
    ];

    console.log("File frequencies:", formatMap(countOccurrences(changedFiles)));
    console.log("Duplicate paths:", [...duplicateValues(changedFiles)]);
    console.log("Distinct paths:", uniqueValues(changedFiles));

    heading("Set algebra for reviewer assignment");

    const frontendReviewers = new Set(["Mira", "Dev", "Anika"]);
    const securityReviewers = new Set(["Anika", "Rohan", "Mira"]);

    console.log("Shared reviewers:", [...intersection(frontendReviewers, securityReviewers)]);
    console.log("Combined reviewer pool:", [...union(frontendReviewers, securityReviewers)]);
    console.log("Frontend-only reviewers:", [...difference(frontendReviewers, securityReviewers)]);
    console.log("Reviewers exclusive to one team:", [
        ...symmetricDifference(frontendReviewers, securityReviewers)
    ]);

    heading("Event-driven Pull Request analytics");

    const processor = new RepositoryEventProcessor();

    const events = [
        { pullRequestId: 42, actor: "Mira", eventType: "opened" },
        { pullRequestId: 42, actor: "Anika", eventType: "reviewed" },
        { pullRequestId: 42, actor: "Anika", eventType: "reviewed" },
        { pullRequestId: 42, actor: "Dev", eventType: "check_failed" },
        { pullRequestId: 43, actor: "Rohan", eventType: "opened" },
        { pullRequestId: 43, actor: "Mira", eventType: "reviewed" },
        { pullRequestId: 42, actor: "Dev", eventType: "check_passed" }
    ];

    await processEventStream(events, processor);

    console.log("Review events for PR 42:", processor.countEvents(42, "reviewed"));
    console.log("Distinct reviewers for PR 42:", [...processor.reviewers(42)]);
    console.log("Pull requests with failing checks:", [...processor.failedPullRequests]);
    console.log("PR 42 event history:", processor.eventsFor(42));

    heading("Membership and JavaScript identity behavior");

    const requiredChecks = membershipIndex(["lint", "unit-tests", "security-scan"]);
    console.log("Security scan required:", requiredChecks.has("security-scan"));
    console.log("Deployment check required:", requiredChecks.has("deployment"));

    // Map and Set compare object keys by identity, not by matching object shape.
    const firstBranch = { name: "main" };
    const secondBranch = { name: "main" };
    const branchSet = new Set([firstBranch, secondBranch]);

    console.log("Distinct object references:", branchSet.size);
    console.log("Same object is present:", branchSet.has(firstBranch));
    console.log("Equivalent-looking object is present:", branchSet.has({ name: "main" }));

    heading("Validation and limitations");

    try {
        processor.ingest({
            pullRequestId: 0,
            actor: "Mira",
            eventType: "opened"
        });
    } catch (error) {
        console.log("Invalid event rejected:", error.message);
    }

    // Map and Set are in-memory structures, not durable storage. Production
    // processors must persist events, define replay semantics, and handle
    // out-of-order events before treating projections as authoritative.
    console.log("All event-processing demonstrations completed.");
}

main().catch(error => {
    console.error("Processing failed:", error.message);
    process.exitCode = 1;
});
