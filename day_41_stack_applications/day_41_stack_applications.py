"""Stack applications: parsing, evaluation, conversion, undo, and reversal.

Run with Python 3.10 or later:
    python stack_applications.py

The implementation uses only the Python standard library.
"""

from __future__ import annotations

import ast
import operator
import random
import unittest
from dataclasses import dataclass
from typing import Callable, Generic, Iterable, TypeVar

T = TypeVar("T")


class StackEmptyError(IndexError):
    """Raised when an operation requires an element from an empty stack."""


class Stack(Generic[T]):
    """A list-backed LIFO stack with explicit boundary checks."""

    def __init__(self, values: Iterable[T] = ()) -> None:
        self._items = list(values)

    def push(self, value: T) -> None:
        self._items.append(value)

    def pop(self) -> T:
        if not self._items:
            raise StackEmptyError("Cannot pop from an empty stack.")
        return self._items.pop()

    def peek(self) -> T:
        if not self._items:
            raise StackEmptyError("Cannot peek at an empty stack.")
        return self._items[-1]

    def is_empty(self) -> bool:
        return not self._items

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        # Iteration exposes a snapshot from top to bottom.
        return reversed(self._items)

    def __repr__(self) -> str:
        return f"Stack(bottom_to_top={self._items!r})"


def reverse_text(text: str) -> str:
    """Reverse Unicode code points using an explicit stack."""
    stack: Stack[str] = Stack()
    for character in text:
        stack.push(character)

    result = []
    while not stack.is_empty():
        result.append(stack.pop())
    return "".join(result)


def reverse_sequence(values: Iterable[T]) -> list[T]:
    """Reverse an iterable without relying on slicing."""
    stack: Stack[T] = Stack(values)
    reversed_values = []
    while not stack.is_empty():
        reversed_values.append(stack.pop())
    return reversed_values


OPEN_TO_CLOSE = {"(": ")", "[": "]", "{": "}"}
CLOSE_TO_OPEN = {closing: opening for opening, closing in OPEN_TO_CLOSE.items()}


@dataclass(frozen=True)
class BracketResult:
    balanced: bool
    message: str
    position: int | None = None


def check_brackets(source: str) -> BracketResult:
    """Validate bracket nesting and report useful failure positions."""
    stack: Stack[tuple[str, int]] = Stack()

    for position, character in enumerate(source):
        if character in OPEN_TO_CLOSE:
            stack.push((character, position))
        elif character in CLOSE_TO_OPEN:
            if stack.is_empty():
                return BracketResult(
                    False, f"Unexpected closing bracket {character!r}.", position
                )

            opening, opening_position = stack.pop()
            if opening != CLOSE_TO_OPEN[character]:
                return BracketResult(
                    False,
                    f"{character!r} does not match {opening!r} opened at "
                    f"position {opening_position}.",
                    position,
                )

    if not stack.is_empty():
        opening, position = stack.pop()
        return BracketResult(
            False, f"Unclosed bracket {opening!r} at position {position}.", position
        )

    return BracketResult(True, "All brackets are balanced.")


def balanced_parentheses(source: str) -> bool:
    """Check parentheses only, ignoring other characters."""
    depth = 0

    for character in source:
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth < 0:
                return False

    return depth == 0


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    position: int


OPERATORS = {
    "+": (1, "left"),
    "-": (1, "left"),
    "*": (2, "left"),
    "/": (2, "left"),
    "^": (4, "right"),
    "u+": (3, "right"),
    "u-": (3, "right"),
}

MAX_EXPRESSION_LENGTH = 10_000
MAX_INTEGER_DIGITS = 100
MAX_ABS_EXPONENT = 10_000


def tokenize(expression: str) -> list[Token]:
    """Tokenize arithmetic input while rejecting unknown characters."""
    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise ValueError("Expression exceeds the maximum permitted length.")

    tokens: list[Token] = []
    index = 0

    while index < len(expression):
        character = expression[index]

        if character.isspace():
            index += 1
            continue

        if character.isdigit() or (
            character == "."
            and index + 1 < len(expression)
            and expression[index + 1].isdigit()
        ):
            start = index
            dot_seen = False

            while index < len(expression):
                current = expression[index]
                if current == ".":
                    if dot_seen:
                        raise ValueError(
                            f"Malformed number at position {start}."
                        )
                    dot_seen = True
                    index += 1
                elif current.isdigit():
                    index += 1
                else:
                    break

            value = expression[start:index]
            if len(value.replace(".", "")) > MAX_INTEGER_DIGITS:
                raise ValueError("Numeric literal contains too many digits.")

            tokens.append(Token("NUMBER", value, start))
            continue

        if character.isalpha() or character == "_":
            start = index
            index += 1
            while index < len(expression) and (
                expression[index].isalnum() or expression[index] == "_"
            ):
                index += 1
            tokens.append(Token("IDENTIFIER", expression[start:index], start))
            continue

        if character in "+-*/^()":
            kind = "PAREN" if character in "()" else "OPERATOR"
            tokens.append(Token(kind, character, index))
            index += 1
            continue

        raise ValueError(
            f"Unsupported character {character!r} at position {index}."
        )

    return tokens


def to_postfix(expression: str) -> list[str]:
    """Convert infix arithmetic to postfix using the shunting-yard algorithm.

    Exponentiation is right-associative. Unary signs have lower precedence
    than exponentiation, so -2^2 becomes 2 2 ^ u-.
    """
    tokens = tokenize(expression)
    output: list[str] = []
    operators: Stack[str] = Stack()
    expecting_operand = True

    for token in tokens:
        if token.kind in {"NUMBER", "IDENTIFIER"}:
            if not expecting_operand:
                raise ValueError(
                    f"Missing operator before {token.value!r} "
                    f"at position {token.position}."
                )
            output.append(token.value)
            expecting_operand = False
            continue

        if token.value == "(":
            if not expecting_operand:
                raise ValueError(
                    f"Missing operator before '(' at position {token.position}."
                )
            operators.push("(")
            expecting_operand = True
            continue

        if token.value == ")":
            if expecting_operand:
                raise ValueError(
                    f"Unexpected ')' or empty parentheses at position "
                    f"{token.position}."
                )

            while not operators.is_empty() and operators.peek() != "(":
                output.append(operators.pop())

            if operators.is_empty():
                raise ValueError(f"Unmatched ')' at position {token.position}.")

            operators.pop()
            expecting_operand = False
            continue

        operator_symbol = token.value

        if expecting_operand:
            if operator_symbol not in "+-":
                raise ValueError(
                    f"Unexpected operator {operator_symbol!r} "
                    f"at position {token.position}."
                )
            operator_symbol = "u" + operator_symbol
        elif operator_symbol in "+-*/^":
            expecting_operand = True
        else:
            raise ValueError(f"Invalid operator at position {token.position}.")

        current_precedence, associativity = OPERATORS[operator_symbol]

        while not operators.is_empty() and operators.peek() != "(":
            top_precedence, _ = OPERATORS[operators.peek()]
            should_pop = (
                top_precedence > current_precedence
                or (
                    top_precedence == current_precedence
                    and associativity == "left"
                )
            )
            if not should_pop:
                break
            output.append(operators.pop())

        operators.push(operator_symbol)

    if not tokens:
        raise ValueError("Expression cannot be empty.")

    if expecting_operand:
        raise ValueError("Expression ends where an operand is required.")

    while not operators.is_empty():
        operator_symbol = operators.pop()
        if operator_symbol == "(":
            raise ValueError("Expression contains an unmatched '('.")
        output.append(operator_symbol)

    return output


BINARY_OPERATIONS: dict[str, Callable[[float, float], float]] = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "^": operator.pow,
}


def evaluate_postfix(
    postfix: Iterable[str],
    variables: dict[str, float] | None = None,
) -> float:
    """Evaluate postfix tokens without executing arbitrary source code."""
    environment = variables or {}
    stack: Stack[float] = Stack()

    for token in postfix:
        if token in {"u+", "u-"}:
            if len(stack) < 1:
                raise ValueError(f"Unary operator {token!r} lacks an operand.")
            operand_value = stack.pop()
            stack.push(+operand_value if token == "u+" else -operand_value)
            continue

        if token in BINARY_OPERATIONS:
            if len(stack) < 2:
                raise ValueError(f"Binary operator {token!r} lacks operands.")

            right = stack.pop()
            left = stack.pop()

            if token == "/" and right == 0:
                raise ZeroDivisionError("Division by zero.")

            if token == "^":
                if abs(right) > MAX_ABS_EXPONENT:
                    raise ValueError("Exponent exceeds the permitted limit.")
                if left == 0 and right < 0:
                    raise ZeroDivisionError("Zero cannot have a negative exponent.")
                if left < 0 and not float(right).is_integer():
                    raise ValueError("Complex results are not supported.")

            result = BINARY_OPERATIONS[token](left, right)

            if isinstance(result, complex):
                raise ValueError("Complex results are not supported.")

            stack.push(float(result))
            continue

        try:
            value = float(token)
        except ValueError:
            if token not in environment:
                raise ValueError(f"Unknown operand or variable {token!r}.")
            value = float(environment[token])

        stack.push(value)

    if len(stack) != 1:
        raise ValueError(
            f"Malformed postfix expression: {len(stack)} values remain."
        )

    result = stack.pop()
    if not result == result or result in (float("inf"), float("-inf")):
        raise ValueError("Expression produced a non-finite result.")
    return result


def evaluate_infix(
    expression: str,
    variables: dict[str, float] | None = None,
) -> float:
    return evaluate_postfix(to_postfix(expression), variables)


def infix_to_prefix(expression: str) -> list[str]:
    """Convert infix to prefix using a binary-expression syntax tree.

    Building the tree preserves the precedence and associativity rules,
    including unary signs, without relying on fragile token reversal.
    """
    postfix = to_postfix(expression)
    tree_stack: Stack[tuple[str, object, object]] = Stack()

    for token in postfix:
        if token in {"u+", "u-"}:
            if len(tree_stack) < 1:
                raise ValueError("Malformed unary expression.")
            operand_node = tree_stack.pop()
            tree_stack.push((token, operand_node, None))
        elif token in BINARY_OPERATIONS:
            if len(tree_stack) < 2:
                raise ValueError("Malformed binary expression.")
            right_node = tree_stack.pop()
            left_node = tree_stack.pop()
            tree_stack.push((token, left_node, right_node))
        else:
            tree_stack.push(("operand:" + token, None, None))

    if len(tree_stack) != 1:
        raise ValueError("Cannot construct expression tree.")

    result: list[str] = []

    def preorder(node: tuple[str, object, object]) -> None:
        operator_or_operand, left, right = node
        if operator_or_operand.startswith("operand:"):
            result.append(operator_or_operand.removeprefix("operand:"))
            return

        result.append(operator_or_operand)
        if left is not None:
            preorder(left)  # type: ignore[arg-type]
        if right is not None:
            preorder(right)  # type: ignore[arg-type]

    preorder(tree_stack.pop())
    return result


@dataclass
class TextEditor:
    """A small editor with stack-based undo and redo history."""

    text: str = ""
    _undo_stack: Stack[str] | None = None
    _redo_stack: Stack[str] | None = None

    def __post_init__(self) -> None:
        self._undo_stack = Stack()
        self._redo_stack = Stack()

    def _save_state(self) -> None:
        assert self._undo_stack is not None
        assert self._redo_stack is not None
        self._undo_stack.push(self.text)
        # A new edit invalidates the previous redo path.
        self._redo_stack = Stack()

    def insert(self, position: int, content: str) -> None:
        if not 0 <= position <= len(self.text):
            raise IndexError("Insertion position is outside the document.")
        self._save_state()
        self.text = self.text[:position] + content + self.text[position:]

    def delete(self, start: int, end: int) -> str:
        if not 0 <= start <= end <= len(self.text):
            raise IndexError("Deletion range is outside the document.")
        removed = self.text[start:end]
        if start == end:
            return ""
        self._save_state()
        self.text = self.text[:start] + self.text[end:]
        return removed

    def replace(self, start: int, end: int, replacement: str) -> None:
        if not 0 <= start <= end <= len(self.text):
            raise IndexError("Replacement range is outside the document.")
        self._save_state()
        self.text = self.text[:start] + replacement + self.text[end:]

    def undo(self) -> bool:
        assert self._undo_stack is not None
        assert self._redo_stack is not None
        if self._undo_stack.is_empty():
            return False
        self._redo_stack.push(self.text)
        self.text = self._undo_stack.pop()
        return True

    def redo(self) -> bool:
        assert self._undo_stack is not None
        assert self._redo_stack is not None
        if self._redo_stack.is_empty():
            return False
        self._undo_stack.push(self.text)
        self.text = self._redo_stack.pop()
        return True


class MinStack:
    """A stack that retrieves its minimum in constant time."""

    def __init__(self) -> None:
        self._values: Stack[int] = Stack()
        self._minimums: Stack[int] = Stack()

    def push(self, value: int) -> None:
        self._values.push(value)
        if self._minimums.is_empty() or value <= self._minimums.peek():
            self._minimums.push(value)

    def pop(self) -> int:
        value = self._values.pop()
        if value == self._minimums.peek():
            self._minimums.pop()
        return value

    def minimum(self) -> int:
        return self._minimums.peek()

    def is_empty(self) -> bool:
        return self._values.is_empty()


class StackApplicationTests(unittest.TestCase):
    def test_balanced_parentheses(self) -> None:
        self.assertTrue(balanced_parentheses("f((x + y) * z)"))
        self.assertFalse(balanced_parentheses("(()"))
        self.assertFalse(balanced_parentheses("())"))

    def test_matching_brackets(self) -> None:
        self.assertTrue(check_brackets("data[{key: (value)}]").balanced)
        self.assertFalse(check_brackets("([)]").balanced)
        self.assertFalse(check_brackets("]").balanced)

    def test_reversal(self) -> None:
        self.assertEqual(reverse_text("stack"), "kcats")
        self.assertEqual(reverse_sequence([1, 2, 3]), [3, 2, 1])
        self.assertEqual(reverse_text(""), "")

    def test_expression_evaluation(self) -> None:
        self.assertEqual(evaluate_infix("2 + 3 * 4"), 14.0)
        self.assertEqual(evaluate_infix("(2 + 3) * 4"), 20.0)
        self.assertEqual(evaluate_infix("2^3^2"), 512.0)
        self.assertEqual(evaluate_infix("-2^2"), -4.0)
        self.assertEqual(evaluate_infix("2*x + 1", {"x": 4}), 9.0)

    def test_expression_failures(self) -> None:
        with self.assertRaises(ZeroDivisionError):
            evaluate_infix("8 / (3 - 3)")
        with self.assertRaises(ValueError):
            evaluate_infix("2 + unknown")
        with self.assertRaises(ValueError):
            evaluate_infix("2 + * 3")
        with self.assertRaises(ValueError):
            evaluate_infix("1 2")
        with self.assertRaises(ValueError):
            evaluate_infix("2^10001")

    def test_conversion(self) -> None:
        self.assertEqual(to_postfix("a + b * c"), ["a", "b", "c", "*", "+"])
        self.assertEqual(
            infix_to_prefix("a + b * c"),
            ["+", "a", "*", "b", "c"],
        )

    def test_undo_redo(self) -> None:
        editor = TextEditor("stack")
        editor.insert(5, "s")
        self.assertEqual(editor.text, "stacks")
        self.assertTrue(editor.undo())
        self.assertEqual(editor.text, "stack")
        self.assertTrue(editor.redo())
        self.assertEqual(editor.text, "stacks")
        editor.insert(0, "A ")
        self.assertFalse(editor.redo())

    def test_min_stack(self) -> None:
        stack = MinStack()
        stack.push(5)
        stack.push(2)
        stack.push(2)
        stack.push(8)
        self.assertEqual(stack.minimum(), 2)
        stack.pop()
        stack.pop()
        self.assertEqual(stack.minimum(), 5)

    def test_empty_stack(self) -> None:
        stack: Stack[int] = Stack()
        with self.assertRaises(StackEmptyError):
            stack.pop()
        with self.assertRaises(StackEmptyError):
            stack.peek()


def demonstrate() -> None:
    print("Stack applications")

    print("\nBracket validation")
    for sample in ("{items[(0)]}", "([)]", "value]"):
        result = check_brackets(sample)
        print(f"{sample!r}: {result.message}")

    print("\nReversal")
    print(reverse_text("repository"))

    print("\nInfix, postfix, evaluation, and prefix")
    for expression in ("2 + 3 * 4", "(2 + 3) * 4", "2^3^2", "-2^2"):
        print(
            f"{expression} -> postfix {to_postfix(expression)}"
            f" -> result {evaluate_infix(expression)}"
            f" -> prefix {infix_to_prefix(expression)}"
        )

    print("\nUndo and redo")
    editor = TextEditor("Pull Request")
    editor.insert(len(editor.text), " approved")
    print("Edited:", editor.text)
    editor.undo()
    print("Undo:", editor.text)
    editor.redo()
    print("Redo:", editor.text)

    print("\nConstant-time minimum tracking")
    minimum_stack = MinStack()
    for value in (14, 6, 9, 2, 11):
        minimum_stack.push(value)
    print("Minimum:", minimum_stack.minimum())
    minimum_stack.pop()
    minimum_stack.pop()
    print("Minimum after two pops:", minimum_stack.minimum())


if __name__ == "__main__":
    demonstrate()
    print("\nAutomated tests")
    unittest.main(argv=["stack_applications.py"], exit=False)
