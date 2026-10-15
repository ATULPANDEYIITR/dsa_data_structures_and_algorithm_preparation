#!/usr/bin/env python3
"""Stack and queue assessment: executable problems from fundamentals to advanced patterns."""

from collections import deque
from dataclasses import dataclass
from typing import Iterable


def print_section(title: str) -> None:
    print(f"\n{'=' * 12} {title} {'=' * 12}")


class Stack:
    """A LIFO collection with explicit empty-stack errors."""

    def __init__(self) -> None:
        self._items: list[int] = []

    def push(self, value: int) -> None:
        self._items.append(value)

    def pop(self) -> int:
        if not self._items:
            raise IndexError("Cannot pop from an empty stack")
        return self._items.pop()

    def peek(self) -> int:
        if not self._items:
            raise IndexError("Cannot inspect an empty stack")
        return self._items[-1]

    def is_empty(self) -> bool:
        return not self._items

    def __len__(self) -> int:
        return len(self._items)


class Queue:
    """A FIFO collection implemented with collections.deque."""

    def __init__(self) -> None:
        self._items: deque[int] = deque()

    def enqueue(self, value: int) -> None:
        self._items.append(value)

    def dequeue(self) -> int:
        if not self._items:
            raise IndexError("Cannot dequeue from an empty queue")
        return self._items.popleft()

    def front(self) -> int:
        if not self._items:
            raise IndexError("Cannot inspect an empty queue")
        return self._items[0]

    def __len__(self) -> int:
        return len(self._items)


class TwoStackQueue:
    """A FIFO queue using two stacks with amortized O(1) operations."""

    def __init__(self) -> None:
        self._incoming: list[int] = []
        self._outgoing: list[int] = []

    def enqueue(self, value: int) -> None:
        self._incoming.append(value)

    def _transfer(self) -> None:
        if not self._outgoing:
            while self._incoming:
                self._outgoing.append(self._incoming.pop())

    def dequeue(self) -> int:
        self._transfer()
        if not self._outgoing:
            raise IndexError("Cannot dequeue from an empty queue")
        return self._outgoing.pop()

    def peek(self) -> int:
        self._transfer()
        if not self._outgoing:
            raise IndexError("Cannot inspect an empty queue")
        return self._outgoing[-1]


def is_valid_parentheses(expression: str) -> bool:
    """Validate nested (), [], and {} delimiters."""
    matching = {")": "(", "]": "[", "}": "{"}
    opening = set(matching.values())
    stack: list[str] = []

    for char in expression:
        if char in opening:
            stack.append(char)
        elif char in matching:
            if not stack or stack.pop() != matching[char]:
                return False

    return not stack


def minimum_parentheses_insertions(expression: str) -> int:
    """Minimum insertions to balance a string containing only parentheses."""
    if any(char not in "()" for char in expression):
        raise ValueError("Input must contain only '(' and ')'")

    unmatched_open = 0
    insertions = 0

    for char in expression:
        if char == "(":
            unmatched_open += 1
        elif unmatched_open:
            unmatched_open -= 1
        else:
            insertions += 1

    return insertions + unmatched_open


def evaluate_postfix(tokens: Iterable[str]) -> int:
    """Evaluate integer postfix arithmetic with exact integer division."""
    stack: list[int] = []
    operators = {"+", "-", "*", "/"}

    for token in tokens:
        if token not in operators:
            try:
                stack.append(int(token))
            except ValueError as exc:
                raise ValueError(f"Invalid token: {token!r}") from exc
            continue

        if len(stack) < 2:
            raise ValueError("Insufficient operands")

        right = stack.pop()
        left = stack.pop()

        if token == "+":
            result = left + right
        elif token == "-":
            result = left - right
        elif token == "*":
            result = left * right
        else:
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            # Truncate toward zero, unlike Python's // for negative values.
            result = abs(left) // abs(right)
            if (left < 0) != (right < 0):
                result = -result

        stack.append(result)

    if len(stack) != 1:
        raise ValueError("Expression must leave exactly one result")
    return stack[0]


def next_greater_elements(values: list[int]) -> list[int]:
    """Return the first strictly greater value to the right, or -1."""
    result = [-1] * len(values)
    unresolved: list[int] = []

    for index, value in enumerate(values):
        while unresolved and values[unresolved[-1]] < value:
            result[unresolved.pop()] = value
        unresolved.append(index)

    return result


def daily_temperatures(temperatures: list[int]) -> list[int]:
    """Return days until a strictly warmer temperature."""
    result = [0] * len(temperatures)
    unresolved: list[int] = []

    for day, temperature in enumerate(temperatures):
        while unresolved and temperatures[unresolved[-1]] < temperature:
            previous_day = unresolved.pop()
            result[previous_day] = day - previous_day
        unresolved.append(day)

    return result


def sliding_window_maximum(values: list[int], window: int) -> list[int]:
    """Compute window maxima with an index-based monotonic deque."""
    if window <= 0 or window > len(values):
        raise ValueError("Window must be between 1 and the input length")

    candidates: deque[int] = deque()
    maxima: list[int] = []

    for index, value in enumerate(values):
        # Discard indices that have left the active window.
        while candidates and candidates[0] <= index - window:
            candidates.popleft()

        # Smaller values cannot become a future maximum while this
        # newer, larger value remains in the window.
        while candidates and values[candidates[-1]] <= value:
            candidates.pop()

        candidates.append(index)

        if index >= window - 1:
            maxima.append(values[candidates[0]])

    return maxima


def largest_histogram_rectangle(heights: list[int]) -> int:
    """Find the largest rectangle under a histogram in O(n) time."""
    if any(height < 0 for height in heights):
        raise ValueError("Histogram heights cannot be negative")

    stack: list[int] = []
    maximum_area = 0

    # A zero-height sentinel forces all remaining positive bars to close.
    for index, height in enumerate([*heights, 0]):
        while stack and heights[stack[-1]] > height:
            bar_height = heights[stack.pop()]
            left_boundary = stack[-1] if stack else -1
            width = index - left_boundary - 1
            maximum_area = max(maximum_area, bar_height * width)

        stack.append(index)

    return maximum_area


def circular_next_greater(values: list[int]) -> list[int]:
    """Solve next-greater element when the array wraps around."""
    n = len(values)
    result = [-1] * n
    unresolved: list[int] = []

    for index in range(2 * n):
        current_index = index % n
        while unresolved and values[unresolved[-1]] < values[current_index]:
            result[unresolved.pop()] = values[current_index]

        # Each original position is pushed only during the first pass.
        if index < n:
            unresolved.append(index)

    return result


@dataclass(frozen=True)
class AssessmentCase:
    name: str
    operation: object
    expected: object


def run_assessment() -> None:
    print_section("Stack and queue fundamentals")

    stack = Stack()
    for value in (10, 20, 30):
        stack.push(value)
    print("Stack top:", stack.peek())
    print("Stack pop:", stack.pop())

    queue = Queue()
    for value in (10, 20, 30):
        queue.enqueue(value)
    print("Queue front:", queue.front())
    print("Queue dequeue:", queue.dequeue())

    two_stack_queue = TwoStackQueue()
    for value in (4, 8, 12):
        two_stack_queue.enqueue(value)
    print("Two-stack queue:", [
        two_stack_queue.dequeue(),
        two_stack_queue.dequeue(),
        two_stack_queue.dequeue(),
    ])

    print_section("Assessment problems")

    cases = [
        AssessmentCase(
            "Balanced delimiters",
            lambda: is_valid_parentheses("{[()]}"),
            True,
        ),
        AssessmentCase(
            "Mismatched delimiters",
            lambda: is_valid_parentheses("([)]"),
            False,
        ),
        AssessmentCase(
            "Minimum insertions",
            lambda: minimum_parentheses_insertions("(()))("),
            2,
        ),
        AssessmentCase(
            "Postfix evaluation",
            lambda: evaluate_postfix(["5", "2", "-", "3", "*"]),
            9,
        ),
        AssessmentCase(
            "Next greater element",
            lambda: next_greater_elements([2, 1, 2, 4, 3]),
            [4, 2, 4, -1, -1],
        ),
        AssessmentCase(
            "Daily temperatures",
            lambda: daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]),
            [1, 1, 4, 2, 1, 1, 0, 0],
        ),
        AssessmentCase(
            "Sliding window maximum",
            lambda: sliding_window_maximum([1, 3, -1, -3, 5, 3, 6, 7], 3),
            [3, 3, 5, 5, 6, 7],
        ),
        AssessmentCase(
            "Largest histogram rectangle",
            lambda: largest_histogram_rectangle([2, 1, 5, 6, 2, 3]),
            10,
        ),
        AssessmentCase(
            "Circular next greater",
            lambda: circular_next_greater([1, 2, 1]),
            [2, -1, 2],
        ),
    ]

    for case in cases:
        actual = case.operation()
        assert actual == case.expected, (
            f"{case.name}: expected {case.expected!r}, got {actual!r}"
        )
        print(f"PASS | {case.name}: {actual}")

    print_section("Failure conditions")

    try:
        Stack().pop()
    except IndexError as error:
        print("Empty stack handled:", error)

    try:
        sliding_window_maximum([1, 2], 3)
    except ValueError as error:
        print("Invalid window handled:", error)

    try:
        evaluate_postfix(["8", "0", "/"])
    except ZeroDivisionError as error:
        print("Division by zero handled:", error)

    print("\nAll assessment cases passed.")


if __name__ == "__main__":
    run_assessment()
