from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Callable, Sequence
import sys


class RecursionErrorBase(ValueError):
    """Raised when recursive input violates the supported domain."""


def require_integer(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RecursionErrorBase(f"{name} must be an integer")
    return value


def factorial(n: int) -> int:
    """Calculate n! using a base case and a recursive case."""
    require_integer(n, "n")
    if n < 0:
        raise RecursionErrorBase("Factorial requires n >= 0")
    if n > 900:
        raise RecursionErrorBase("Input exceeds the safe recursion demonstration limit")
    if n <= 1:
        return 1
    return n * factorial(n - 1)


@lru_cache(maxsize=None)
def fibonacci(n: int) -> int:
    """Return the nth Fibonacci number with memoized recursive state."""
    require_integer(n, "n")
    if n < 0:
        raise RecursionErrorBase("Fibonacci requires n >= 0")
    if n > 900:
        raise RecursionErrorBase("Input exceeds the safe recursion demonstration limit")
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def power(base: int, exponent: int) -> int:
    """Calculate integer powers using exponentiation by squaring."""
    require_integer(base, "base")
    require_integer(exponent, "exponent")
    if exponent < 0:
        raise RecursionErrorBase("Exponent must be non-negative")
    if exponent == 0:
        return 1
    half = power(base, exponent // 2)
    squared = half * half
    return squared if exponent % 2 == 0 else base * squared


def recursive_sum(n: int) -> int:
    """Calculate the sum of integers from zero through n."""
    require_integer(n, "n")
    if n < 0:
        raise RecursionErrorBase("n must be non-negative")
    if n > 900:
        raise RecursionErrorBase("Input exceeds the safe recursion demonstration limit")
    if n == 0:
        return 0
    return n + recursive_sum(n - 1)


def reverse_string(value: str) -> str:
    """Reverse a string by removing one leading character per call."""
    if not isinstance(value, str):
        raise RecursionErrorBase("value must be a string")
    if len(value) <= 1:
        return value
    return reverse_string(value[1:]) + value[0]


def reverse_list(values: Sequence[int]) -> list[int]:
    """Reverse a sequence recursively without mutating its input."""
    if not values:
        return []
    return [values[-1]] + reverse_list(values[:-1])


def recursive_sum_array(values: Sequence[int], index: int = 0) -> int:
    """Process an array with an explicit index as recursive state."""
    require_integer(index, "index")
    if index < 0 or index > len(values):
        raise RecursionErrorBase("index must be between zero and array length")
    if index == len(values):
        return 0
    return require_integer(values[index], "array element") + recursive_sum_array(
        values, index + 1
    )


def recursive_max(values: Sequence[int], index: int = 0) -> int:
    """Find a maximum by combining each element with the remaining suffix."""
    if not values:
        raise RecursionErrorBase("Cannot find a maximum of an empty sequence")
    require_integer(index, "index")
    if index < 0 or index >= len(values):
        raise RecursionErrorBase("index must identify an array element")
    if index == len(values) - 1:
        return require_integer(values[index], "array element")
    current = require_integer(values[index], "array element")
    return max(current, recursive_max(values, index + 1))


def binary_search(values: Sequence[int], target: int,
                  left: int = 0, right: int | None = None) -> int:
    """Return the index of target in a sorted sequence, or -1."""
    require_integer(target, "target")
    if right is None:
        right = len(values) - 1
    require_integer(left, "left")
    require_integer(right, "right")
    if left < 0 or right >= len(values):
        if not (left == 0 and right == -1 and not values):
            raise RecursionErrorBase("Search boundaries are outside the sequence")
    if left > right:
        return -1
    middle = left + (right - left) // 2
    value = require_integer(values[middle], "array element")
    if value == target:
        return middle
    if target < value:
        return binary_search(values, target, left, middle - 1)
    return binary_search(values, target, middle + 1, right)


@dataclass(frozen=True)
class CallFrame:
    function: str
    state: str
    depth: int


def factorial_trace(n: int, depth: int = 0) -> tuple[int, list[CallFrame]]:
    """Record conceptual stack frames to make recursive state observable."""
    if n < 0:
        raise RecursionErrorBase("Factorial requires n >= 0")
    frames = [CallFrame("factorial", f"n={n}", depth)]
    if n <= 1:
        return 1, frames
    result, child_frames = factorial_trace(n - 1, depth + 1)
    frames.extend(child_frames)
    return n * result, frames


def run_tests() -> None:
    assert factorial(0) == 1
    assert factorial(5) == 120
    assert fibonacci(0) == 0
    assert fibonacci(10) == 55
    assert power(2, 10) == 1024
    assert power(9, 0) == 1
    assert recursive_sum(5) == 15
    assert reverse_string("recursion") == "noisrucer"
    assert reverse_string("") == ""
    assert reverse_list([1, 2, 3]) == [3, 2, 1]
    assert recursive_sum_array([2, 4, 6]) == 12
    assert recursive_sum_array([]) == 0
    assert recursive_max([-4, 2, 9, 1]) == 9
    assert binary_search([1, 3, 5, 7], 5) == 2
    assert binary_search([], 5) == -1
    result, frames = factorial_trace(4)
    assert result == 24
    assert [frame.depth for frame in frames] == [0, 1, 2, 3]
    for operation in (
        lambda: factorial(-1),
        lambda: fibonacci(-1),
        lambda: power(2, -1),
        lambda: recursive_sum(-1),
        lambda: recursive_max([]),
        lambda: recursive_sum_array([1], 2),
    ):
        try:
            operation()
        except RecursionErrorBase:
            pass
        else:
            raise AssertionError("Invalid input was accepted")
    print("All recursion tests passed.")


def main() -> None:
    run_tests()
    print(f"factorial(5) = {factorial(5)}")
    print(f"fibonacci(10) = {fibonacci(10)}")
    print(f"power(2, 10) = {power(2, 10)}")
    print(f"recursive_sum(10) = {recursive_sum(10)}")
    print(f"reverse_string('stack') = {reverse_string('stack')}")
    values = [7, 2, 9, 4, 1]
    print(f"reverse_list({values}) = {reverse_list(values)}")
    print(f"recursive_sum_array({values}) = {recursive_sum_array(values)}")
    print(f"recursive_max({values}) = {recursive_max(values)}")
    print(f"binary_search([1, 3, 5, 7], 5) = {binary_search([1, 3, 5, 7], 5)}")
    _, frames = factorial_trace(4)
    print("Factorial call stack:")
    for frame in frames:
        print(f"{'  ' * frame.depth}{frame.function}({frame.state})")


if __name__ == "__main__":
    main()
