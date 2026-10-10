"""
Stack Fundamentals: Array-Based and Linked-List-Based Implementations

Demonstrates:
- LIFO behavior
- Push, pop, peek, and is_empty
- Array-backed stacks with configurable capacity
- Linked-list stacks with node-based storage
- Underflow, overflow, and input validation
- Iteration, snapshots, and safe state inspection
- Unit tests, randomized operations, and performance analysis

Run:
    python stack_fundamentals.py
"""

from __future__ import annotations

import random
import time
import unittest
from dataclasses import dataclass
from typing import Generic, Iterable, Iterator, Optional, TypeVar

T = TypeVar("T")


class StackError(Exception):
    """Base exception for stack-specific errors."""


class StackUnderflowError(StackError):
    """Raised when an operation requires an element from an empty stack."""


class StackOverflowError(StackError):
    """Raised when a bounded array stack has reached its capacity."""


class InvalidCapacityError(StackError):
    """Raised when a stack capacity is invalid."""


class Stack(Generic[T]):
    """Common interface for LIFO stack implementations."""

    def push(self, item: T) -> None:
        raise NotImplementedError

    def pop(self) -> T:
        raise NotImplementedError

    def peek(self) -> T:
        raise NotImplementedError

    def is_empty(self) -> bool:
        raise NotImplementedError

    def size(self) -> int:
        raise NotImplementedError

    def __len__(self) -> int:
        return self.size()

    def __bool__(self) -> bool:
        return not self.is_empty()

    def __iter__(self) -> Iterator[T]:
        raise NotImplementedError


class ArrayStack(Stack[T]):
    """
    A stack backed by a Python list.

    The final list element is the top of the stack. Appending and removing
    that element provide amortized O(1) push and O(1) pop operations.
    """

    def __init__(
        self,
        items: Optional[Iterable[T]] = None,
        capacity: Optional[int] = None,
    ) -> None:
        if capacity is not None and (
            not isinstance(capacity, int)
            or isinstance(capacity, bool)
            or capacity < 0
        ):
            raise InvalidCapacityError("Capacity must be a non-negative integer.")

        self._items: list[T] = []
        self._capacity = capacity

        if items is not None:
            for item in items:
                self.push(item)

    def push(self, item: T) -> None:
        if self._capacity is not None and len(self._items) >= self._capacity:
            raise StackOverflowError(
                f"Stack capacity of {self._capacity} has been reached."
            )
        self._items.append(item)

    def pop(self) -> T:
        if self.is_empty():
            raise StackUnderflowError("Cannot pop from an empty stack.")
        return self._items.pop()

    def peek(self) -> T:
        if self.is_empty():
            raise StackUnderflowError("Cannot peek at an empty stack.")
        return self._items[-1]

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def size(self) -> int:
        return len(self._items)

    def clear(self) -> None:
        self._items.clear()

    def snapshot(self) -> tuple[T, ...]:
        """Return an immutable view ordered from bottom to top."""
        return tuple(self._items)

    def __iter__(self) -> Iterator[T]:
        # Return a snapshot iterator so later mutations do not change
        # the sequence being traversed.
        return iter(tuple(reversed(self._items)))

    def __repr__(self) -> str:
        return f"ArrayStack(bottom_to_top={self._items!r})"


@dataclass(slots=True)
class Node(Generic[T]):
    """One linked-list element and its reference to the next node."""

    value: T
    next: Optional[Node[T]] = None


class LinkedListStack(Stack[T]):
    """
    A stack whose top is the head of a singly linked list.

    Push and pop update the head pointer without shifting existing elements.
    """

    def __init__(self, items: Optional[Iterable[T]] = None) -> None:
        self._top: Optional[Node[T]] = None
        self._size = 0

        if items is not None:
            for item in items:
                self.push(item)

    def push(self, item: T) -> None:
        # The new node points to the previous top before becoming the top.
        self._top = Node(item, self._top)
        self._size += 1

    def pop(self) -> T:
        if self.is_empty():
            raise StackUnderflowError("Cannot pop from an empty stack.")

        assert self._top is not None
        removed = self._top
        self._top = removed.next
        self._size -= 1

        # Detach the removed node to avoid retaining the rest of the chain
        # through an external reference to that node.
        removed.next = None
        return removed.value

    def peek(self) -> T:
        if self.is_empty():
            raise StackUnderflowError("Cannot peek at an empty stack.")

        assert self._top is not None
        return self._top.value

    def is_empty(self) -> bool:
        return self._size == 0

    def size(self) -> int:
        return self._size

    def clear(self) -> None:
        # Release links progressively so the entire chain is not retained
        # by the stack after clearing.
        current = self._top
        while current is not None:
            following = current.next
            current.next = None
            current = following

        self._top = None
        self._size = 0

    def snapshot(self) -> tuple[T, ...]:
        return tuple(self)

    def __iter__(self) -> Iterator[T]:
        current = self._top
        while current is not None:
            yield current.value
            current = current.next

    def __repr__(self) -> str:
        return f"LinkedListStack(top_to_bottom={list(self)!r})"


def demonstrate_basic_operations(stack: Stack[int]) -> None:
    print(f"\n{type(stack).__name__}")
    print("Initially empty:", stack.is_empty())

    for value in (10, 20, 30):
        stack.push(value)
        print(f"push({value}) -> size={stack.size()}")

    print("Top element:", stack.peek())
    print("Elements from top to bottom:", list(stack))
    print("Removed element:", stack.pop())
    print("New top:", stack.peek())
    print("Current size:", len(stack))

    while not stack.is_empty():
        print("pop() ->", stack.pop())

    print("Empty after removals:", stack.is_empty())


def reverse_text(text: str, stack_type: type[Stack[str]]) -> str:
    """Reverse text using only the stack's LIFO behavior."""
    stack = stack_type()
    for character in text:
        stack.push(character)

    reversed_characters: list[str] = []
    while not stack.is_empty():
        reversed_characters.append(stack.pop())

    return "".join(reversed_characters)


def is_balanced_delimiters(expression: str) -> bool:
    """
    Check brackets in source-like text.

    This simple demonstration checks (), [], and {} without interpreting
    quoted strings or comments as language syntax.
    """
    stack: ArrayStack[str] = ArrayStack()
    matching_open = {")": "(", "]": "[", "}": "{"}
    opening = set(matching_open.values())

    for character in expression:
        if character in opening:
            stack.push(character)
        elif character in matching_open:
            if stack.is_empty() or stack.pop() != matching_open[character]:
                return False

    return stack.is_empty()


def evaluate_postfix(expression: str) -> float:
    """
    Evaluate whitespace-separated reverse Polish notation.

    For an operator, the first pop is the right operand and the second
    pop is the left operand. Reversing this order breaks subtraction
    and division.
    """
    stack: ArrayStack[float] = ArrayStack()
    operators = {"+", "-", "*", "/"}

    for token in expression.split():
        if token not in operators:
            try:
                stack.push(float(token))
            except ValueError as exc:
                raise ValueError(f"Invalid token: {token!r}") from exc
            continue

        if stack.size() < 2:
            raise ValueError(f"Insufficient operands for operator {token!r}.")

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
                raise ZeroDivisionError("Division by zero in postfix expression.")
            result = left / right

        stack.push(result)

    if stack.size() != 1:
        raise ValueError("Expression must leave exactly one result.")

    return stack.pop()


class UndoHistory:
    """
    A small editor-history model.

    Each saved document state is pushed onto a stack. Undo removes the
    latest state and restores the previous one.
    """

    def __init__(self, initial_text: str = "") -> None:
        self._history: LinkedListStack[str] = LinkedListStack()
        self._history.push(initial_text)
        self._current = initial_text

    @property
    def current_text(self) -> str:
        return self._current

    def edit(self, new_text: str) -> None:
        self._history.push(new_text)
        self._current = new_text

    def undo(self) -> str:
        if self._history.size() <= 1:
            raise StackUnderflowError("No earlier document state is available.")

        self._history.pop()
        self._current = self._history.peek()
        return self._current

    def history_size(self) -> int:
        return self._history.size()


def verify_against_reference() -> None:
    """
    Apply the same randomized operations to both stacks and a Python list.

    The list is the reference model. Its final element represents the top.
    This checks observable behavior rather than internal representation.
    """
    rng = random.Random(20261010)
    stacks: list[Stack[int]] = [ArrayStack(), LinkedListStack()]
    reference: list[int] = []

    for _ in range(5000):
        operation = rng.choice(("push", "push", "pop", "peek", "empty"))

        if operation == "push":
            value = rng.randint(-1000, 1000)
            reference.append(value)
            for stack in stacks:
                stack.push(value)

        elif operation == "pop":
            if reference:
                expected = reference.pop()
                for stack in stacks:
                    assert stack.pop() == expected
            else:
                for stack in stacks:
                    try:
                        stack.pop()
                    except StackUnderflowError:
                        pass
                    else:
                        raise AssertionError("Empty pop should fail.")

        elif operation == "peek":
            if reference:
                for stack in stacks:
                    assert stack.peek() == reference[-1]
            else:
                for stack in stacks:
                    try:
                        stack.peek()
                    except StackUnderflowError:
                        pass
                    else:
                        raise AssertionError("Empty peek should fail.")

        else:
            for stack in stacks:
                assert stack.is_empty() == (len(reference) == 0)

        for stack in stacks:
            assert stack.size() == len(reference)
            assert list(stack) == list(reversed(reference))


def benchmark_stack(stack_type: type[Stack[int]], count: int) -> float:
    """Measure a complete push-then-pop workload using a monotonic clock."""
    stack = stack_type()
    started = time.perf_counter()

    for value in range(count):
        stack.push(value)

    while not stack.is_empty():
        stack.pop()

    return time.perf_counter() - started


class StackTests(unittest.TestCase):
    def test_lifo_order(self) -> None:
        for stack_type in (ArrayStack, LinkedListStack):
            stack = stack_type()
            for value in (1, 2, 3):
                stack.push(value)
            self.assertEqual([stack.pop(), stack.pop(), stack.pop()], [3, 2, 1])

    def test_empty_operations(self) -> None:
        for stack_type in (ArrayStack, LinkedListStack):
            stack = stack_type()
            self.assertTrue(stack.is_empty())
            with self.assertRaises(StackUnderflowError):
                stack.pop()
            with self.assertRaises(StackUnderflowError):
                stack.peek()

    def test_capacity(self) -> None:
        stack: ArrayStack[int] = ArrayStack(capacity=2)
        stack.push(1)
        stack.push(2)
        with self.assertRaises(StackOverflowError):
            stack.push(3)
        self.assertEqual(stack.pop(), 2)

    def test_zero_capacity(self) -> None:
        stack: ArrayStack[int] = ArrayStack(capacity=0)
        with self.assertRaises(StackOverflowError):
            stack.push(1)

    def test_none_is_a_valid_element(self) -> None:
        stack: LinkedListStack[Optional[int]] = LinkedListStack()
        stack.push(None)
        self.assertFalse(stack.is_empty())
        self.assertIsNone(stack.peek())
        self.assertIsNone(stack.pop())
        self.assertTrue(stack.is_empty())

    def test_delimiter_matching(self) -> None:
        self.assertTrue(is_balanced_delimiters("({[]})"))
        self.assertFalse(is_balanced_delimiters("([)]"))
        self.assertFalse(is_balanced_delimiters("((("))

    def test_postfix_evaluation(self) -> None:
        self.assertEqual(evaluate_postfix("5 2 -"), 3.0)
        self.assertEqual(evaluate_postfix("5 2 /"), 2.5)
        self.assertEqual(evaluate_postfix("3 4 + 2 *"), 14.0)

    def test_postfix_errors(self) -> None:
        with self.assertRaises(ZeroDivisionError):
            evaluate_postfix("4 0 /")
        with self.assertRaises(ValueError):
            evaluate_postfix("4 +")
        with self.assertRaises(ValueError):
            evaluate_postfix("1 2")

    def test_undo_history(self) -> None:
        history = UndoHistory("draft")
        history.edit("review")
        history.edit("approved")
        self.assertEqual(history.undo(), "review")
        self.assertEqual(history.undo(), "draft")
        with self.assertRaises(StackUnderflowError):
            history.undo()

    def test_snapshot_iterator(self) -> None:
        stack: ArrayStack[int] = ArrayStack([1, 2, 3])
        iterator = iter(stack)
        stack.push(4)
        self.assertEqual(list(iterator), [3, 2, 1])


def main() -> None:
    print("STACK FUNDAMENTALS")
    print("A stack follows LIFO: last in, first out.")

    demonstrate_basic_operations(ArrayStack[int]())
    demonstrate_basic_operations(LinkedListStack[int]())

    print("\nTEXT REVERSAL")
    print("Original: STACK")
    print("Reversed:", reverse_text("STACK", ArrayStack))

    print("\nDELIMITER VALIDATION")
    for expression in ("(a + b) * [c]", "{[()]}", "([)]", "((x)"):
        print(f"{expression!r}: {is_balanced_delimiters(expression)}")

    print("\nPOSTFIX CALCULATION")
    for expression in ("5 2 -", "3 4 + 2 *", "20 5 /"):
        print(f"{expression} = {evaluate_postfix(expression)}")

    print("\nUNDO HISTORY")
    editor = UndoHistory("Initial draft")
    editor.edit("Added implementation")
    editor.edit("Added tests")
    print("Current:", editor.current_text)
    print("Undo:", editor.undo())
    print("Undo:", editor.undo())

    print("\nRANDOMIZED VERIFICATION")
    verify_against_reference()
    print("Both implementations passed 5,000 reference-model operations.")

    print("\nUNIT TESTS")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(StackTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)

    print("\nBENCHMARK")
    print("Illustrative local timings; results depend on hardware and runtime.")
    for stack_type in (ArrayStack, LinkedListStack):
        elapsed = benchmark_stack(stack_type, 100_000)
        print(f"{stack_type.__name__}: {elapsed:.4f} seconds")


if __name__ == "__main__":
    main()
