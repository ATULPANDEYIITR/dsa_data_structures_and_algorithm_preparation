"use strict";

/*
 * Stack applications in JavaScript.
 * Run with Node.js 18 or later: node stack_applications.js
 */

const assert = require("node:assert/strict");

class Stack {
    #items;

    constructor(values = []) {
        this.#items = [...values];
    }

    push(value) {
        this.#items.push(value);
        return this.size;
    }

    pop() {
        if (this.isEmpty()) {
            throw new RangeError("Cannot pop from an empty stack.");
        }
        return this.#items.pop();
    }

    peek() {
        if (this.isEmpty()) {
            throw new RangeError("Cannot peek at an empty stack.");
        }
        return this.#items[this.#items.length - 1];
    }

    isEmpty() {
        return this.#items.length === 0;
    }

    get size() {
        return this.#items.length;
    }

    toArray() {
        return [...this.#items];
    }
}

function reverseArray(values) {
    const stack = new Stack(values);
    const result = [];

    while (!stack.isEmpty()) {
        result.push(stack.pop());
    }

    return result;
}

function reverseStringByCodePoint(value) {
    // Array.from preserves Unicode code points better than indexing UTF-16 units.
    return reverseArray(Array.from(value)).join("");
}

function matchBrackets(source) {
    const pairs = new Map([
        ["(", ")"],
        ["[", "]"],
        ["{", "}"]
    ]);
    const closingToOpening = new Map(
        [...pairs.entries()].map(([opening, closing]) => [closing, opening])
    );
    const stack = new Stack();

    for (let index = 0; index < source.length; index += 1) {
        const character = source[index];

        if (pairs.has(character)) {
            stack.push({ character, index });
        } else if (closingToOpening.has(character)) {
            if (stack.isEmpty()) {
                return {
                    balanced: false,
                    index,
                    reason: `Unexpected closing bracket ${character}`
                };
            }

            const opening = stack.pop();
            if (opening.character !== closingToOpening.get(character)) {
                return {
                    balanced: false,
                    index,
                    reason: `${character} cannot close ${opening.character} at ${opening.index}`
                };
            }
        }
    }

    if (!stack.isEmpty()) {
        const opening = stack.pop();
        return {
            balanced: false,
            index: opening.index,
            reason: `Unclosed ${opening.character}`
        };
    }

    return { balanced: true, index: null, reason: "Balanced" };
}

function tokenize(expression) {
    if (typeof expression !== "string" || expression.length > 10000) {
        throw new TypeError("Expression must be a string of at most 10000 characters.");
    }

    const pattern = /\s+|(?:\d+(?:\.\d*)?|\.\d+)|[A-Za-z_]\w*|[+\-*/^()]/gy;
    const tokens = [];
    let position = 0;

    while (position < expression.length) {
        pattern.lastIndex = position;
        const match = pattern.exec(expression);

        if (!match) {
            throw new SyntaxError(`Unsupported input at position ${position}.`);
        }

        const value = match[0];
        if (!/^\s+$/.test(value)) {
            tokens.push({ value, position });
        }
        position = pattern.lastIndex;
    }

    return tokens;
}

const operatorInfo = {
    "+": { precedence: 1, associativity: "left", arity: 2 },
    "-": { precedence: 1, associativity: "left", arity: 2 },
    "*": { precedence: 2, associativity: "left", arity: 2 },
    "/": { precedence: 2, associativity: "left", arity: 2 },
    "^": { precedence: 4, associativity: "right", arity: 2 },
    "u+": { precedence: 3, associativity: "right", arity: 1 },
    "u-": { precedence: 3, associativity: "right", arity: 1 }
};

function toPostfix(expression) {
    const tokens = tokenize(expression);
    const output = [];
    const operators = new Stack();
    let expectsOperand = true;

    for (const token of tokens) {
        const value = token.value;

        if (/^(?:\d+(?:\.\d*)?|\.\d+)$/.test(value) ||
            /^[A-Za-z_]\w*$/.test(value)) {
            if (!expectsOperand) {
                throw new SyntaxError(`Missing operator at position ${token.position}.`);
            }
            output.push(value);
            expectsOperand = false;
            continue;
        }

        if (value === "(") {
            if (!expectsOperand) {
                throw new SyntaxError(`Missing operator before '(' at ${token.position}.`);
            }
            operators.push(value);
            expectsOperand = true;
            continue;
        }

        if (value === ")") {
            if (expectsOperand) {
                throw new SyntaxError(`Unexpected ')' at ${token.position}.`);
            }

            while (!operators.isEmpty() && operators.peek() !== "(") {
                output.push(operators.pop());
            }

            if (operators.isEmpty()) {
                throw new SyntaxError(`Unmatched ')' at ${token.position}.`);
            }

            operators.pop();
            expectsOperand = false;
            continue;
        }

        let current = value;

        if (expectsOperand) {
            if (value !== "+" && value !== "-") {
                throw new SyntaxError(`Unexpected operator '${value}' at ${token.position}.`);
            }
            current = `u${value}`;
        } else {
            expectsOperand = true;
        }

        const currentInfo = operatorInfo[current];

        while (!operators.isEmpty() && operators.peek() !== "(") {
            const top = operators.peek();
            const topInfo = operatorInfo[top];

            const popTop =
                topInfo.precedence > currentInfo.precedence ||
                (topInfo.precedence === currentInfo.precedence &&
                    currentInfo.associativity === "left");

            if (!popTop) {
                break;
            }

            output.push(operators.pop());
        }

        operators.push(current);
    }

    if (tokens.length === 0) {
        throw new SyntaxError("Expression cannot be empty.");
    }

    if (expectsOperand) {
        throw new SyntaxError("Expression ends with a missing operand.");
    }

    while (!operators.isEmpty()) {
        const value = operators.pop();
        if (value === "(") {
            throw new SyntaxError("Unmatched '('.");
        }
        output.push(value);
    }

    return output;
}

function evaluatePostfix(postfix, variables = {}) {
    const stack = new Stack();
    const operations = {
        "+": (a, b) => a + b,
        "-": (a, b) => a - b,
        "*": (a, b) => a * b,
        "/": (a, b) => {
            if (b === 0) throw new RangeError("Division by zero.");
            return a / b;
        },
        "^": (a, b) => {
            if (Math.abs(b) > 10000) throw new RangeError("Exponent is too large.");
            return a ** b;
        }
    };

    for (const token of postfix) {
        if (token === "u+" || token === "u-") {
            if (stack.size < 1) {
                throw new SyntaxError(`Missing operand for ${token}.`);
            }
            const value = stack.pop();
            stack.push(token === "u+" ? value : -value);
        } else if (Object.hasOwn(operations, token)) {
            if (stack.size < 2) {
                throw new SyntaxError(`Missing operands for ${token}.`);
            }
            const right = stack.pop();
            const left = stack.pop();
            stack.push(operations[token](left, right));
        } else {
            let value;

            if (/^(?:\d+(?:\.\d*)?|\.\d+)$/.test(token)) {
                value = Number(token);
            } else {
                // Own-property checks prevent inherited properties from becoming variables.
                if (!Object.hasOwn(variables, token)) {
                    throw new ReferenceError(`Unknown variable '${token}'.`);
                }
                value = variables[token];
            }

            if (typeof value !== "number" || !Number.isFinite(value)) {
                throw new TypeError(`Operand '${token}' must be a finite number.`);
            }

            stack.push(value);
        }
    }

    if (stack.size !== 1) {
        throw new SyntaxError(`Malformed postfix expression: ${stack.size} values remain.`);
    }

    const result = stack.pop();
    if (!Number.isFinite(result)) {
        throw new RangeError("Expression produced a non-finite result.");
    }
    return result;
}

function evaluateInfix(expression, variables = {}) {
    return evaluatePostfix(toPostfix(expression), variables);
}

class TransactionalEditor {
    #text;
    #undo = [];
    #redo = [];
    #historyLimit;

    constructor(initialText = "", historyLimit = 100) {
        if (!Number.isInteger(historyLimit) || historyLimit < 1) {
            throw new RangeError("History limit must be a positive integer.");
        }
        this.#text = initialText;
        this.#historyLimit = historyLimit;
    }

    get text() {
        return this.#text;
    }

    #saveBeforeMutation() {
        this.#undo.push(this.#text);

        // Bound memory use by discarding the oldest retained snapshot.
        if (this.#undo.length > this.#historyLimit) {
            this.#undo.shift();
        }

        // A new edit creates a new history branch and invalidates redo.
        this.#redo.length = 0;
    }

    insert(index, content) {
        if (!Number.isInteger(index) || index < 0 || index > this.#text.length) {
            throw new RangeError("Invalid insertion index.");
        }
        this.#saveBeforeMutation();
        this.#text = this.#text.slice(0, index) + content + this.#text.slice(index);
    }

    delete(start, end) {
        if (!Number.isInteger(start) || !Number.isInteger(end) ||
            start < 0 || start > end || end > this.#text.length) {
            throw new RangeError("Invalid deletion range.");
        }

        if (start === end) return "";
        const removed = this.#text.slice(start, end);
        this.#saveBeforeMutation();
        this.#text = this.#text.slice(0, start) + this.#text.slice(end);
        return removed;
    }

    undo() {
        if (this.#undo.length === 0) return false;
        this.#redo.push(this.#text);
        this.#text = this.#undo.pop();
        return true;
    }

    redo() {
        if (this.#redo.length === 0) return false;
        this.#undo.push(this.#text);
        this.#text = this.#redo.pop();
        return true;
    }
}

class ExpressionHistory {
    #history = [];
    #cursor = -1;

    record(expression, result) {
        if (typeof expression !== "string" || !Number.isFinite(result)) {
            throw new TypeError("History requires an expression and finite result.");
        }

        // Discard the forward history when a new result follows an undo.
        this.#history = this.#history.slice(0, this.#cursor + 1);
        this.#history.push(Object.freeze({
            expression,
            result,
            recordedAt: new Date().toISOString()
        }));
        this.#cursor = this.#history.length - 1;
    }

    previous() {
        if (this.#cursor <= 0) return null;
        this.#cursor -= 1;
        return this.#history[this.#cursor];
    }

    next() {
        if (this.#cursor >= this.#history.length - 1) return null;
        this.#cursor += 1;
        return this.#history[this.#cursor];
    }

    current() {
        return this.#cursor < 0 ? null : this.#history[this.#cursor];
    }
}

function runTests() {
    assert.deepEqual(reverseArray([1, 2, 3]), [3, 2, 1]);
    assert.equal(reverseStringByCodePoint("stack"), "kcats");
    assert.equal(matchBrackets("{a[(b)]}").balanced, true);
    assert.equal(matchBrackets("([)]").balanced, false);

    assert.equal(evaluateInfix("2 + 3 * 4"), 14);
    assert.equal(evaluateInfix("(2 + 3) * 4"), 20);
    assert.equal(evaluateInfix("2^3^2"), 512);
    assert.equal(evaluateInfix("-2^2"), -4);
    assert.equal(evaluateInfix("amount * rate", { amount: 5, rate: 1.2 }), 6);

    assert.throws(() => evaluateInfix("5 / 0"), RangeError);
    assert.throws(() => evaluateInfix("2 + missing"), ReferenceError);
    assert.throws(() => evaluateInfix("2 ** 3"), SyntaxError);
    assert.throws(() => evaluateInfix("1 2"), SyntaxError);

    const editor = new TransactionalEditor("Review");
    editor.insert(6, " approved");
    assert.equal(editor.text, "Review approved");
    assert.equal(editor.undo(), true);
    assert.equal(editor.text, "Review");
    assert.equal(editor.redo(), true);
    assert.equal(editor.text, "Review approved");
    editor.insert(0, "Pull Request: ");
    assert.equal(editor.redo(), false);

    const history = new ExpressionHistory();
    history.record("2 + 2", 4);
    history.record("3 * 3", 9);
    assert.equal(history.previous().result, 4);
    history.record("5 + 5", 10);
    assert.equal(history.next(), null);

    const stack = new Stack();
    assert.throws(() => stack.pop(), RangeError);

    console.log("All stack application tests passed.");
}

function demonstrate() {
    console.log("Bracket validation:", matchBrackets("config[{key: (value)}]"));
    console.log("Reverse:", reverseStringByCodePoint("repository"));

    for (const expression of ["2 + 3 * 4", "(2 + 3) * 4", "2^3^2", "-2^2"]) {
        console.log({
            expression,
            postfix: toPostfix(expression),
            result: evaluateInfix(expression)
        });
    }

    const editor = new TransactionalEditor("Branch protection");
    editor.insert(editor.text.length, " enabled");
    console.log("Edited:", editor.text);
    editor.undo();
    console.log("Undone:", editor.text);
    editor.redo();
    console.log("Redone:", editor.text);

    const history = new ExpressionHistory();
    history.record("8 / 2", 4);
    history.record("7 * 6", 42);
    console.log("Previous calculation:", history.previous());
}

demonstrate();
runTests();
