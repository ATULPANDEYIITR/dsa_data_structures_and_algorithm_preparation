"""
Day 16 — Sliding Window
=======================

A comprehensive study program for the sliding-window technique.

Topics covered:
    - Fixed-size windows
    - Variable-size windows
    - Window expansion
    - Window contraction
    - Maximum sum subarray of size k
    - Minimum-size subarray
    - Longest valid subarray
    - Frequency-based windows
    - Distinct-element windows
    - Edge cases
    - Complexity analysis
    - Brute-force versus optimized solutions
    - Prefix-sum comparison
    - Monotonic deque for advanced window problems
    - Testing and validation

The program is intentionally self-contained and uses only the Python standard library.
"""

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from typing import Callable, Iterable, Optional


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def print_section(title: str) -> None:
    """Print a visually consistent section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def validate_non_empty_sequence(values: list[int], name: str = "values") -> None:
    """Validate that a sequence exists and is non-empty."""
    if not isinstance(values, list):
        raise TypeError(f"{name} must be a list.")
    if not values:
        raise ValueError(f"{name} must not be empty.")


def validate_positive_k(k: int) -> None:
    """Validate a positive window size."""
    if not isinstance(k, int):
        raise TypeError("k must be an integer.")
    if k <= 0:
        raise ValueError("k must be greater than zero.")


# ---------------------------------------------------------------------------
# Fundamental idea
# ---------------------------------------------------------------------------

def demonstrate_window_mechanics() -> None:
    """
    Demonstrate how a fixed-size window moves.

    Instead of rebuilding every window from scratch, remove the element that
    leaves the left side and add the element entering on the right.
    """
    print_section("1. Basic sliding-window mechanics")

    values = [2, 4, 1, 7, 3, 6]
    k = 3

    current_sum = sum(values[:k])
    print(f"Array: {values}")
    print(f"Window size: {k}")
    print(f"Initial window: {values[:k]}, sum={current_sum}")

    for right in range(k, len(values)):
        outgoing = values[right - k]
        incoming = values[right]

        current_sum -= outgoing
        current_sum += incoming

        left = right - k + 1
        window = values[left:right + 1]

        print(
            f"Move window -> {window}; "
            f"removed={outgoing}, added={incoming}, sum={current_sum}"
        )


# ---------------------------------------------------------------------------
# Fixed-size windows
# ---------------------------------------------------------------------------

def max_sum_subarray_bruteforce(values: list[int], k: int) -> int:
    """
    O(n*k) baseline solution.

    Each window is summed independently. This is useful for understanding why
    the sliding-window optimization is needed.
    """
    validate_non_empty_sequence(values)
    validate_positive_k(k)

    if k > len(values):
        raise ValueError("k cannot exceed the length of the array.")

    best = float("-inf")

    for left in range(len(values) - k + 1):
        current_sum = 0
        for index in range(left, left + k):
            current_sum += values[index]
        best = max(best, current_sum)

    return int(best)


def max_sum_subarray(values: list[int], k: int) -> int:
    """
    O(n) fixed-size sliding-window solution.

    Invariant:
        The window always contains exactly k elements.
    """
    validate_non_empty_sequence(values)
    validate_positive_k(k)

    if k > len(values):
        raise ValueError("k cannot exceed the length of the array.")

    window_sum = sum(values[:k])
    best = window_sum

    for right in range(k, len(values)):
        window_sum += values[right]
        window_sum -= values[right - k]
        best = max(best, window_sum)

    return best


def fixed_window_sums(values: list[int], k: int) -> list[int]:
    """Return the sum of every fixed-size window in O(n)."""
    validate_non_empty_sequence(values)
    validate_positive_k(k)

    if k > len(values):
        raise ValueError("k cannot exceed the length of the array.")

    result = []
    window_sum = sum(values[:k])
    result.append(window_sum)

    for right in range(k, len(values)):
        window_sum += values[right] - values[right - k]
        result.append(window_sum)

    return result


# ---------------------------------------------------------------------------
# Average, minimum, maximum and other fixed-window measurements
# ---------------------------------------------------------------------------

def minimum_sum_subarray(values: list[int], k: int) -> int:
    """Find the minimum sum among all windows of exactly k elements."""
    validate_non_empty_sequence(values)
    validate_positive_k(k)

    if k > len(values):
        raise ValueError("k cannot exceed the length of the array.")

    window_sum = sum(values[:k])
    best = window_sum

    for right in range(k, len(values)):
        window_sum += values[right] - values[right - k]
        best = min(best, window_sum)

    return best


def maximum_average_subarray(values: list[int], k: int) -> float:
    """Find the maximum average among all fixed-size windows."""
    return max_sum_subarray(values, k) / k


def count_windows_with_sum_at_least(
    values: list[int],
    k: int,
    threshold: int,
) -> int:
    """Count fixed-size windows whose sum is at least threshold."""
    return sum(
        window_sum >= threshold
        for window_sum in fixed_window_sums(values, k)
    )


# ---------------------------------------------------------------------------
# Variable-size windows
# ---------------------------------------------------------------------------

def minimum_size_subarray_sum(
    values: list[int],
    target: int,
) -> int:
    """
    Find the minimum length subarray whose sum is >= target.

    This classic shrinking-window solution requires non-negative values.
    With negative values, the monotonic relationship between expansion and
    sum no longer holds.
    """
    validate_non_empty_sequence(values)

    if target <= 0:
        raise ValueError("target must be positive.")

    if any(value < 0 for value in values):
        raise ValueError(
            "This sliding-window implementation requires non-negative values."
        )

    left = 0
    window_sum = 0
    best_length = float("inf")

    for right, value in enumerate(values):
        # Expansion: add the new right-side element.
        window_sum += value

        # Contraction: while the current window already satisfies the
        # requirement, try to remove elements from the left.
        while window_sum >= target:
            best_length = min(best_length, right - left + 1)
            window_sum -= values[left]
            left += 1

    return 0 if best_length == float("inf") else int(best_length)


def longest_subarray_sum_at_most(
    values: list[int],
    limit: int,
) -> int:
    """
    Find the longest subarray with sum <= limit.

    This implementation assumes non-negative values.
    """
    validate_non_empty_sequence(values)

    if limit < 0:
        return 0

    if any(value < 0 for value in values):
        raise ValueError(
            "This sliding-window implementation requires non-negative values."
        )

    left = 0
    window_sum = 0
    best_length = 0

    for right, value in enumerate(values):
        window_sum += value

        while left <= right and window_sum > limit:
            window_sum -= values[left]
            left += 1

        best_length = max(best_length, right - left + 1)

    return best_length


# ---------------------------------------------------------------------------
# Longest valid subarray
# ---------------------------------------------------------------------------

def longest_subarray_at_most_k_distinct(
    values: list[int],
    k: int,
) -> int:
    """
    Find the longest contiguous subarray containing at most k distinct values.

    Frequency counts make contraction efficient:
    - add values as the right pointer expands
    - remove values as the left pointer contracts
    - delete a key when its frequency reaches zero
    """
    validate_non_empty_sequence(values)
    validate_positive_k(k)

    counts: dict[int, int] = defaultdict(int)
    left = 0
    best = 0

    for right, value in enumerate(values):
        counts[value] += 1

        while len(counts) > k:
            outgoing = values[left]
            counts[outgoing] -= 1

            if counts[outgoing] == 0:
                del counts[outgoing]

            left += 1

        best = max(best, right - left + 1)

    return best


def longest_subarray_exactly_k_distinct(
    values: list[int],
    k: int,
) -> int:
    """
    Find the longest subarray containing exactly k distinct values.

    The easiest relationship is:

        exactly(k) = at_most(k) for length
                     constrained against
                     at_most(k - 1)

    For maximum length, a direct two-pointer implementation is also possible.
    """
    validate_non_empty_sequence(values)
    validate_positive_k(k)

    counts: dict[int, int] = defaultdict(int)
    left = 0
    best = 0

    for right, value in enumerate(values):
        counts[value] += 1

        while len(counts) > k:
            outgoing = values[left]
            counts[outgoing] -= 1
            if counts[outgoing] == 0:
                del counts[outgoing]
            left += 1

        if len(counts) == k:
            best = max(best, right - left + 1)

    return best


# ---------------------------------------------------------------------------
# Frequency-based windows
# ---------------------------------------------------------------------------

def longest_substring_without_repeating_characters(text: str) -> int:
    """
    Longest substring with no repeated character.

    The window invariant is:
        Every character inside [left, right] appears at most once.
    """
    last_seen: dict[str, int] = {}
    left = 0
    best = 0

    for right, character in enumerate(text):
        if character in last_seen and last_seen[character] >= left:
            # Jump left directly beyond the previous occurrence.
            left = last_seen[character] + 1

        last_seen[character] = right
        best = max(best, right - left + 1)

    return best


def longest_substring_with_at_most_k_distinct(
    text: str,
    k: int,
) -> int:
    """Find the longest substring containing at most k distinct characters."""
    if k <= 0:
        return 0

    counts: dict[str, int] = defaultdict(int)
    left = 0
    best = 0

    for right, character in enumerate(text):
        counts[character] += 1

        while len(counts) > k:
            outgoing = text[left]
            counts[outgoing] -= 1

            if counts[outgoing] == 0:
                del counts[outgoing]

            left += 1

        best = max(best, right - left + 1)

    return best


def permutation_in_string(pattern: str, text: str) -> bool:
    """
    Determine whether text contains a permutation/anagram of pattern.

    A fixed-size frequency window is used because every candidate window has
    exactly len(pattern) characters.
    """
    if not pattern:
        return True

    if len(pattern) > len(text):
        return False

    required = Counter(pattern)
    window = Counter(text[:len(pattern)])

    if window == required:
        return True

    k = len(pattern)

    for right in range(k, len(text)):
        incoming = text[right]
        outgoing = text[right - k]

        window[incoming] += 1
        window[outgoing] -= 1

        if window[outgoing] == 0:
            del window[outgoing]

        if window == required:
            return True

    return False


def find_all_anagram_starts(pattern: str, text: str) -> list[int]:
    """Return all starting indices where an anagram of pattern occurs."""
    if not pattern or len(pattern) > len(text):
        return []

    required = Counter(pattern)
    window = Counter(text[:len(pattern)])
    result = []

    if window == required:
        result.append(0)

    k = len(pattern)

    for right in range(k, len(text)):
        incoming = text[right]
        outgoing = text[right - k]

        window[incoming] += 1
        window[outgoing] -= 1

        if window[outgoing] == 0:
            del window[outgoing]

        left = right - k + 1

        if window == required:
            result.append(left)

    return result


# ---------------------------------------------------------------------------
# Distinct-element windows
# ---------------------------------------------------------------------------

def count_distinct_in_every_window(
    values: list[int],
    k: int,
) -> list[int]:
    """
    Return the number of distinct values in every fixed-size window.

    A frequency map allows O(1)-average insertion/removal.
    """
    validate_non_empty_sequence(values)
    validate_positive_k(k)

    if k > len(values):
        raise ValueError("k cannot exceed the length of the array.")

    counts = defaultdict(int)

    for value in values[:k]:
        counts[value] += 1

    result = [len(counts)]

    for right in range(k, len(values)):
        outgoing = values[right - k]
        incoming = values[right]

        counts[outgoing] -= 1
        if counts[outgoing] == 0:
            del counts[outgoing]

        counts[incoming] += 1
        result.append(len(counts))

    return result


def maximum_frequency_in_each_window(
    values: list[int],
    k: int,
) -> list[int]:
    """
    Return the maximum frequency of any value in each fixed-size window.

    The frequency map is updated incrementally. Because finding max(counts)
    directly costs O(number_of_distinct_values), this implementation favors
    clarity. A heap or frequency-of-frequency structure can be used when
    stronger performance guarantees are required.
    """
    validate_non_empty_sequence(values)
    validate_positive_k(k)

    if k > len(values):
        raise ValueError("k cannot exceed the length of the array.")

    counts = Counter(values[:k])
    result = [max(counts.values())]

    for right in range(k, len(values)):
        outgoing = values[right - k]
        incoming = values[right]

        counts[outgoing] -= 1
        if counts[outgoing] == 0:
            del counts[outgoing]

        counts[incoming] += 1
        result.append(max(counts.values()))

    return result


# ---------------------------------------------------------------------------
# Binary array examples
# ---------------------------------------------------------------------------

def longest_ones_after_flipping_at_most_k_zeros(
    values: list[int],
    k: int,
) -> int:
    """
    Longest subarray containing at most k zeros.

    Interpreting zeros as the resource that can be "spent" is a useful way to
    recognize many variable-window problems.
    """
    if k < 0:
        raise ValueError("k cannot be negative.")

    left = 0
    zero_count = 0
    best = 0

    for right, value in enumerate(values):
        if value not in (0, 1):
            raise ValueError("The array must contain only 0 and 1.")

        if value == 0:
            zero_count += 1

        while zero_count > k:
            if values[left] == 0:
                zero_count -= 1
            left += 1

        best = max(best, right - left + 1)

    return best


# ---------------------------------------------------------------------------
# Character replacement problem
# ---------------------------------------------------------------------------

def longest_repeating_character_replacement(
    text: str,
    k: int,
) -> int:
    """
    Longest substring that can be made of one repeated character after at
    most k replacements.

    For a window of length L:
        replacements_needed = L - highest_frequency

    The window is valid when replacements_needed <= k.
    """
    if k < 0:
        raise ValueError("k cannot be negative.")

    counts = defaultdict(int)
    left = 0
    highest_frequency = 0
    best = 0

    for right, character in enumerate(text):
        counts[character] += 1
        highest_frequency = max(highest_frequency, counts[character])

        while (right - left + 1) - highest_frequency > k:
            outgoing = text[left]
            counts[outgoing] -= 1
            left += 1

        best = max(best, right - left + 1)

    return best


# ---------------------------------------------------------------------------
# Subarray product
# ---------------------------------------------------------------------------

def minimum_size_subarray_product(
    values: list[int],
    target: int,
) -> int:
    """
    Minimum-length contiguous subarray with product >= target.

    This sliding-window formulation requires strictly positive values and a
    positive target.
    """
    if not values:
        return 0

    if target <= 0:
        raise ValueError("target must be positive.")

    if any(value <= 0 for value in values):
        raise ValueError(
            "This implementation requires strictly positive values."
        )

    product = 1
    left = 0
    best = float("inf")

    for right, value in enumerate(values):
        product *= value

        while product >= target:
            best = min(best, right - left + 1)
            product //= values[left]
            left += 1

    return 0 if best == float("inf") else int(best)


# ---------------------------------------------------------------------------
# Advanced: monotonic deque
# ---------------------------------------------------------------------------

def sliding_window_maximum(values: list[int], k: int) -> list[int]:
    """
    Find the maximum element in every fixed-size window in O(n).

    The deque stores indices, not values.

    Invariant:
        Values corresponding to indices in the deque are decreasing.

    Therefore, deque[0] always identifies the maximum element in the current
    window.
    """
    validate_non_empty_sequence(values)
    validate_positive_k(k)

    if k > len(values):
        raise ValueError("k cannot exceed the length of the array.")

    candidates: deque[int] = deque()
    result = []

    for right, value in enumerate(values):
        # Remove indices that are outside the current window.
        while candidates and candidates[0] <= right - k:
            candidates.popleft()

        # Any smaller value behind the new value can never become a future
        # maximum, so remove it.
        while candidates and values[candidates[-1]] <= value:
            candidates.pop()

        candidates.append(right)

        if right >= k - 1:
            result.append(values[candidates[0]])

    return result


def sliding_window_minimum(values: list[int], k: int) -> list[int]:
    """Find the minimum element in every fixed-size window in O(n)."""
    validate_non_empty_sequence(values)
    validate_positive_k(k)

    if k > len(values):
        raise ValueError("k cannot exceed the length of the array.")

    candidates: deque[int] = deque()
    result = []

    for right, value in enumerate(values):
        while candidates and candidates[0] <= right - k:
            candidates.popleft()

        while candidates and values[candidates[-1]] >= value:
            candidates.pop()

        candidates.append(right)

        if right >= k - 1:
            result.append(values[candidates[0]])

    return result


# ---------------------------------------------------------------------------
# Advanced: longest subarray with absolute difference <= limit
# ---------------------------------------------------------------------------

def longest_subarray_absolute_difference(
    values: list[int],
    limit: int,
) -> int:
    """
    Find the longest subarray where max(window) - min(window) <= limit.

    Two monotonic deques maintain the maximum and minimum simultaneously.
    """
    if not values:
        return 0

    if limit < 0:
        return 0

    maximums: deque[int] = deque()
    minimums: deque[int] = deque()

    left = 0
    best = 0

    for right, value in enumerate(values):
        while maximums and values[maximums[-1]] <= value:
            maximums.pop()
        maximums.append(right)

        while minimums and values[minimums[-1]] >= value:
            minimums.pop()
        minimums.append(right)

        while (
            values[maximums[0]] - values[minimums[0]]
            > limit
        ):
            if maximums[0] == left:
                maximums.popleft()

            if minimums[0] == left:
                minimums.popleft()

            left += 1

        best = max(best, right - left + 1)

    return best


# ---------------------------------------------------------------------------
# Prefix sums: related technique and distinction
# ---------------------------------------------------------------------------

def range_sum_with_prefix(
    values: list[int],
    left: int,
    right: int,
) -> int:
    """
    Compute an inclusive range sum using a prefix-sum array.

    This demonstrates that sliding windows and prefix sums solve different
    families of problems.

    Prefix sums are especially useful when many arbitrary range queries are
    required. Sliding windows are often better when the window moves
    incrementally under a validity rule.
    """
    if not values:
        raise ValueError("values must not be empty.")

    if not 0 <= left <= right < len(values):
        raise IndexError("Invalid inclusive range.")

    prefix = [0]

    for value in values:
        prefix.append(prefix[-1] + value)

    return prefix[right + 1] - prefix[left]


# ---------------------------------------------------------------------------
# Generic variable-window framework
# ---------------------------------------------------------------------------

def longest_valid_window(
    values: list[int],
    add: Callable[[int], None],
    remove: Callable[[int], None],
    is_valid: Callable[[], bool],
) -> tuple[int, int, int]:
    """
    Generic conceptual framework for a longest-valid-window problem.

    The state maintained by add/remove determines what "valid" means.

    Returns:
        (best_length, best_left, best_right)
    """
    left = 0
    best_length = 0
    best_left = 0
    best_right = -1

    for right, value in enumerate(values):
        add(value)

        while not is_valid():
            remove(values[left])
            left += 1

        current_length = right - left + 1

        if current_length > best_length:
            best_length = current_length
            best_left = left
            best_right = right

    return best_length, best_left, best_right


# ---------------------------------------------------------------------------
# Brute-force validation helpers
# ---------------------------------------------------------------------------

def brute_force_max_sum(values: list[int], k: int) -> int:
    """Reference implementation used to test the optimized solution."""
    validate_non_empty_sequence(values)
    validate_positive_k(k)

    if k > len(values):
        raise ValueError("k cannot exceed the length of the array.")

    return max(
        sum(values[left:left + k])
        for left in range(len(values) - k + 1)
    )


def run_randomized_validation() -> None:
    """
    Compare the optimized fixed-window algorithm against a brute-force
    reference implementation.

    Randomized differential testing is useful for detecting off-by-one
    errors in pointer movement.
    """
    import random

    print_section("2. Randomized differential testing")

    random.seed(42)

    for _ in range(250):
        length = random.randint(1, 20)
        values = [random.randint(-20, 20) for _ in range(length)]
        k = random.randint(1, length)

        expected = brute_force_max_sum(values, k)
        actual = max_sum_subarray(values, k)

        if expected != actual:
            raise AssertionError(
                f"Mismatch: values={values}, k={k}, "
                f"expected={expected}, actual={actual}"
            )

    print("250 randomized tests passed.")


# ---------------------------------------------------------------------------
# Complexity demonstration
# ---------------------------------------------------------------------------

def complexity_reference() -> None:
    """
    Print the conceptual complexity of major sliding-window patterns.
    """
    print_section("3. Complexity reference")

    rows = [
        ("Fixed-size sum", "O(n)", "O(1)"),
        ("Minimum-size sum window", "O(n)", "O(1)"),
        ("At-most-k distinct", "O(n) average", "O(k)"),
        ("No repeated characters", "O(n) average", "O(min(n, alphabet))"),
        ("Anagram detection", "O(n) average", "O(alphabet)"),
        ("Window maximum/deque", "O(n)", "O(k)"),
        ("Window minimum/deque", "O(n)", "O(k)"),
        ("Max-min constrained window", "O(n)", "O(k)"),
    ]

    print(f"{'Problem':<34} {'Time':<18} {'Space':<22}")
    print("-" * 74)

    for name, time_complexity, space_complexity in rows:
        print(
            f"{name:<34} "
            f"{time_complexity:<18} "
            f"{space_complexity:<22}"
        )


# ---------------------------------------------------------------------------
# Edge cases and exceptions
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    print_section("4. Edge cases")

    examples = [
        ("Single element", [7], 1),
        ("All negative values", [-8, -3, -5, -2], 2),
        ("Window equals array", [1, 2, 3], 3),
        ("Repeated values", [5, 5, 5, 5], 2),
        ("Zeros", [0, 0, 0, 0], 3),
    ]

    for name, values, k in examples:
        print(
            f"{name}: values={values}, k={k}, "
            f"max_sum={max_sum_subarray(values, k)}"
        )

    invalid_inputs = [
        ([], 2),
        ([1, 2, 3], 0),
        ([1, 2, 3], -1),
        ([1, 2, 3], 4),
    ]

    for values, k in invalid_inputs:
        try:
            max_sum_subarray(values, k)
        except (TypeError, ValueError) as error:
            print(
                f"Handled invalid input values={values}, k={k}: "
                f"{error}"
            )


# ---------------------------------------------------------------------------
# Practical case study: monitoring network traffic
# ---------------------------------------------------------------------------

@dataclass
class TrafficWindow:
    start_index: int
    end_index: int
    total_packets: int
    average_packets: float


def analyze_network_traffic(
    packet_counts: list[int],
    window_size: int,
    alert_threshold: int,
) -> list[TrafficWindow]:
    """
    Analyze a stream of packet counts using fixed-size sliding windows.

    Each value represents the number of packets observed in one time interval.
    A monitoring system can use the window total to detect sustained traffic
    spikes rather than reacting to a single isolated measurement.
    """
    validate_non_empty_sequence(packet_counts)
    validate_positive_k(window_size)

    if window_size > len(packet_counts):
        raise ValueError("window_size exceeds packet stream length.")

    results = []
    window_sum = sum(packet_counts[:window_size])

    for right in range(window_size - 1, len(packet_counts)):
        if right >= window_size:
            window_sum += packet_counts[right]
            window_sum -= packet_counts[right - window_size]

        left = right - window_size + 1

        if window_sum >= alert_threshold:
            results.append(
                TrafficWindow(
                    start_index=left,
                    end_index=right,
                    total_packets=window_sum,
                    average_packets=window_sum / window_size,
                )
            )

    return results


# ---------------------------------------------------------------------------
# Comprehensive demonstrations
# ---------------------------------------------------------------------------

def run_examples() -> None:
    print_section("5. Fixed-size window examples")

    numbers = [2, 1, 5, 1, 3, 2]
    k = 3

    print("Array:", numbers)
    print("Maximum sum:", max_sum_subarray(numbers, k))
    print("Minimum sum:", minimum_sum_subarray(numbers, k))
    print("All window sums:", fixed_window_sums(numbers, k))
    print("Maximum average:", maximum_average_subarray(numbers, k))
    print(
        "Windows with sum >= 7:",
        count_windows_with_sum_at_least(numbers, k, 7),
    )

    print_section("6. Variable-size windows")

    positive_numbers = [2, 3, 1, 2, 4, 3]
    target = 7

    print("Array:", positive_numbers)
    print(
        f"Minimum size with sum >= {target}:",
        minimum_size_subarray_sum(positive_numbers, target),
    )

    print(
        "Longest sum <= 8:",
        longest_subarray_sum_at_most(positive_numbers, 8),
    )

    print_section("7. Distinct-element windows")

    values = [1, 2, 1, 2, 3, 2, 2]
    print("Array:", values)
    print(
        "Longest subarray with at most 2 distinct:",
        longest_subarray_at_most_k_distinct(values, 2),
    )
    print(
        "Longest subarray with exactly 2 distinct:",
        longest_subarray_exactly_k_distinct(values, 2),
    )
    print(
        "Distinct count in every window of size 3:",
        count_distinct_in_every_window(values, 3),
    )

    print_section("8. Frequency-based string windows")

    text = "abcabcbb"
    print("Text:", text)
    print(
        "Longest substring without repetition:",
        longest_substring_without_repeating_characters(text),
    )
    print(
        "Longest substring with at most 2 distinct:",
        longest_substring_with_at_most_k_distinct(text, 2),
    )

    print_section("9. Anagram windows")

    pattern = "abc"
    source = "cbaebabacd"

    print("Pattern:", pattern)
    print("Source:", source)
    print("Contains permutation:", permutation_in_string(pattern, source))
    print("Anagram starting positions:", find_all_anagram_starts(pattern, source))

    print_section("10. Binary windows")

    binary_values = [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0]
    print("Array:", binary_values)
    print(
        "Longest sequence after flipping at most 2 zeros:",
        longest_ones_after_flipping_at_most_k_zeros(binary_values, 2),
    )

    print_section("11. Character replacement")

    text = "AABABBA"
    print("Text:", text)
    print(
        "Longest repeated-character window after 1 replacement:",
        longest_repeating_character_replacement(text, 1),
    )

    print_section("12. Product window")

    product_values = [10, 5, 2, 6]
    print("Array:", product_values)
    print(
        "Minimum length with product >= 100:",
        minimum_size_subarray_product(product_values, 100),
    )

    print_section("13. Monotonic deque")

    deque_values = [1, 3, -1, -3, 5, 3, 6, 7]
    print("Array:", deque_values)
    print(
        "Sliding maximum, k=3:",
        sliding_window_maximum(deque_values, 3),
    )
    print(
        "Sliding minimum, k=3:",
        sliding_window_minimum(deque_values, 3),
    )

    print_section("14. Maximum-minimum constrained window")

    constrained_values = [8, 2, 4, 7]
    print("Array:", constrained_values)
    print(
        "Longest window where max-min <= 4:",
        longest_subarray_absolute_difference(constrained_values, 4),
    )

    print_section("15. Prefix-sum comparison")

    prefix_values = [3, 1, 4, 1, 5, 9]
    print("Array:", prefix_values)
    print(
        "Sum from index 1 through 4:",
        range_sum_with_prefix(prefix_values, 1, 4),
    )

    print_section("16. Generic variable-window framework")

    values = [1, 2, 1, 3, 4, 2, 3]
    state = Counter()
    maximum_distinct = 2

    def add_value(value: int) -> None:
        state[value] += 1

    def remove_value(value: int) -> None:
        state[value] -= 1
        if state[value] == 0:
            del state[value]

    def valid_window() -> bool:
        return len(state) <= maximum_distinct

    best_length, best_left, best_right = longest_valid_window(
        values,
        add_value,
        remove_value,
        valid_window,
    )

    print(
        "Best window:",
        values[best_left:best_right + 1],
        "length=",
        best_length,
    )

    print_section("17. Network traffic case study")

    traffic = [120, 130, 145, 300, 280, 290, 150, 140, 135]
    alerts = analyze_network_traffic(
        packet_counts=traffic,
        window_size=3,
        alert_threshold=750,
    )

    for alert in alerts:
        print(
            f"Alert window {alert.start_index}-{alert.end_index}: "
            f"total={alert.total_packets}, "
            f"average={alert.average_packets:.2f}"
        )


# ---------------------------------------------------------------------------
# Testing
# ---------------------------------------------------------------------------

def run_assertions() -> None:
    print_section("18. Correctness assertions")

    assert max_sum_subarray([2, 1, 5, 1, 3, 2], 3) == 9
    assert max_sum_subarray([-5, -2, -8], 2) == -7
    assert minimum_sum_subarray([2, 1, 5, 1, 3, 2], 3) == 6

    assert minimum_size_subarray_sum(
        [2, 3, 1, 2, 4, 3],
        7,
    ) == 2

    assert longest_subarray_at_most_k_distinct(
        [1, 2, 1, 2, 3],
        2,
    ) == 4

    assert longest_subarray_exactly_k_distinct(
        [1, 2, 1, 2, 3],
        2,
    ) == 4

    assert longest_substring_without_repeating_characters(
        "abcabcbb"
    ) == 3

    assert permutation_in_string("ab", "eidbaooo")
    assert not permutation_in_string("ab", "eidboaoo")

    assert find_all_anagram_starts(
        "abc",
        "cbaebabacd",
    ) == [0, 6]

    assert count_distinct_in_every_window(
        [1, 2, 1, 3, 4, 2, 3],
        4,
    ) == [3, 4, 4, 4]

    assert longest_ones_after_flipping_at_most_k_zeros(
        [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0],
        2,
    ) == 6

    assert longest_repeating_character_replacement(
        "AABABBA",
        1,
    ) == 4

    assert minimum_size_subarray_product(
        [10, 5, 2, 6],
        100,
    ) == 3

    assert sliding_window_maximum(
        [1, 3, -1, -3, 5, 3, 6, 7],
        3,
    ) == [3, 3, 5, 5, 6, 7]

    assert sliding_window_minimum(
        [1, 3, -1, -3, 5, 3, 6, 7],
        3,
    ) == [-1, -3, -3, -3, 3, 3]

    assert longest_subarray_absolute_difference(
        [8, 2, 4, 7],
        4,
    ) == 2

    print("All deterministic assertions passed.")


# ---------------------------------------------------------------------------
# Main program
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Run the complete study demonstration.

    The examples are deliberately deterministic so that the script behaves
    consistently in different environments.
    """
    demonstrate_window_mechanics()
    run_examples()
    demonstrate_edge_cases()
    complexity_reference()
    run_assertions()
    run_randomized_validation()

    print_section("19. Study checkpoints")

    checkpoints = [
        "Fixed window: keep window length constant.",
        "Expansion: move the right pointer to include new data.",
        "Contraction: move the left pointer when the window becomes invalid.",
        "Frequency map: track counts when validity depends on occurrences.",
        "Distinct count: remove keys when their count reaches zero.",
        "Monotonic deque: maintain candidate extrema in O(n).",
        "Validity invariant: clearly define what every active window satisfies.",
        "Non-negative restriction: many sum/product windows rely on monotonicity.",
        "Pointer movement: each pointer normally moves only forward.",
        "Amortized analysis: repeated pointer operations can still total O(n).",
    ]

    for number, checkpoint in enumerate(checkpoints, start=1):
        print(f"{number:02d}. {checkpoint}")

    print("\nSliding-window study program completed successfully.")


if __name__ == "__main__":
    main()
