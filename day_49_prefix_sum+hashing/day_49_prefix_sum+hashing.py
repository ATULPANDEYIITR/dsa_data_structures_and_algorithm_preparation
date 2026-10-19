from collections import defaultdict
from typing import Dict, List, Tuple


def subarray_sum_equals_k(values: List[int], target: int) -> Tuple[int, List[Tuple[int, int]]]:
    """
    Count contiguous subarrays whose sum equals target.

    If prefix[j] - prefix[i] == target, then values[i:j] has the
    requested sum. The frequency map lets us find previous prefixes
    in O(1) average time.
    """
    prefix = 0
    count = 0
    matches = []
    prefix_positions: Dict[int, List[int]] = defaultdict(list)
    prefix_positions[0].append(-1)

    for end, value in enumerate(values):
        prefix += value
        needed = prefix - target

        for start_prefix_index in prefix_positions.get(needed, []):
            count += 1
            matches.append((start_prefix_index + 1, end))

        prefix_positions[prefix].append(end)

    return count, matches


def longest_subarray_sum_equals_k(values: List[int], target: int) -> Tuple[int, Tuple[int, int] | None]:
    """
    Store only the earliest occurrence of every prefix sum.

    For a fixed ending position, the earliest matching prefix gives
    the longest possible subarray ending there.
    """
    prefix = 0
    first_seen: Dict[int, int] = {0: -1}
    best_length = 0
    best_range = None

    for index, value in enumerate(values):
        prefix += value
        needed = prefix - target

        if needed in first_seen:
            start = first_seen[needed] + 1
            length = index - first_seen[needed]
            if length > best_length:
                best_length = length
                best_range = (start, index)

        if prefix not in first_seen:
            first_seen[prefix] = index

    return best_length, best_range


def zero_sum_subarrays(values: List[int]) -> List[Tuple[int, int]]:
    """
    Equal prefix sums identify zero-sum subarrays.

    If prefix[j] == prefix[i], the elements between i and j sum to zero.
    Repeated prefix values therefore identify every zero-sum interval.
    """
    positions: Dict[int, List[int]] = defaultdict(list)
    positions[0].append(-1)

    prefix = 0
    result = []

    for index, value in enumerate(values):
        prefix += value
        for previous in positions[prefix]:
            result.append((previous + 1, index))
        positions[prefix].append(index)

    return result


def has_zero_sum_subarray(values: List[int]) -> bool:
    seen = {0}
    prefix = 0

    for value in values:
        prefix += value
        if prefix in seen:
            return True
        seen.add(prefix)

    return False


def count_zero_sum_subarrays(values: List[int]) -> int:
    """
    Instead of storing every position, a frequency count is enough when
    only the number of zero-sum subarrays is required.

    A prefix occurring f times contributes C(f, 2) pairs.
    """
    frequencies: Dict[int, int] = defaultdict(int)
    frequencies[0] = 1

    prefix = 0
    count = 0

    for value in values:
        prefix += value
        count += frequencies[prefix]
        frequencies[prefix] += 1

    return count


def count_equal_zero_one_subarrays(bits: List[int]) -> int:
    """
    Convert 0 to -1 and 1 to +1.

    An equal number of zeros and ones then becomes a zero-sum condition.
    This is a prefix-state transformation rather than a separate
    algorithm.
    """
    frequencies = defaultdict(int)
    frequencies[0] = 1

    balance = 0
    count = 0

    for bit in bits:
        if bit not in (0, 1):
            raise ValueError("Binary input must contain only 0 and 1.")

        balance += 1 if bit == 1 else -1
        count += frequencies[balance]
        frequencies[balance] += 1

    return count


def longest_equal_zero_one_subarray(bits: List[int]) -> Tuple[int, Tuple[int, int] | None]:
    first_balance = {0: -1}
    balance = 0
    best = 0
    best_range = None

    for index, bit in enumerate(bits):
        if bit not in (0, 1):
            raise ValueError("Binary input must contain only 0 and 1.")

        balance += 1 if bit == 1 else -1

        if balance in first_balance:
            length = index - first_balance[balance]
            if length > best:
                best = length
                best_range = (first_balance[balance] + 1, index)
        else:
            first_balance[balance] = index

    return best, best_range


def longest_equal_frequency_subarray(values: List[str], symbols: List[str]) -> Tuple[int, Tuple[int, int] | None]:
    """
    Find the longest interval in which every requested symbol occurs
    equally often.

    For two symbols, one balance is sufficient. For several symbols,
    use a vector of differences relative to one reference symbol.

    Example for A, B, C:
        state = (count(A)-count(C), count(B)-count(C))

    Equal states at two prefix positions imply equal counts of all
    symbols inside the interval.
    """
    if not symbols:
        raise ValueError("At least one symbol is required.")

    allowed = set(symbols)
    if len(allowed) != len(symbols):
        raise ValueError("Symbols must be unique.")

    reference = symbols[-1]
    dimensions = symbols[:-1]

    state = [0] * len(dimensions)
    first_seen = {tuple(state): -1}
    best = 0
    best_range = None

    for index, value in enumerate(values):
        if value not in allowed:
            raise ValueError(f"Unexpected symbol: {value!r}")

        if value == reference:
            for dimension in range(len(state)):
                state[dimension] -= 1
        else:
            state[dimensions.index(value)] += 1

        key = tuple(state)

        if key in first_seen:
            length = index - first_seen[key]
            if length > best:
                best = length
                best_range = (first_seen[key] + 1, index)
        else:
            first_seen[key] = index

    return best, best_range


def longest_same_frequency_binary_subarray(values: List[int]) -> Tuple[int, Tuple[int, int] | None]:
    return longest_equal_frequency_subarray(
        [str(value) for value in values],
        ["0", "1"],
    )


def count_subarrays_with_all_symbols_equal_frequency(values: List[str], symbols: List[str]) -> int:
    """
    Count intervals whose frequencies of all requested symbols are equal.

    The prefix state is a tuple of relative frequency differences.
    Equal states form valid endpoint pairs.
    """
    if len(symbols) < 2:
        raise ValueError("At least two symbols are required.")

    allowed = set(symbols)
    if len(allowed) != len(symbols):
        raise ValueError("Symbols must be unique.")

    reference = symbols[-1]
    dimensions = symbols[:-1]
    state = [0] * len(dimensions)

    frequencies = defaultdict(int)
    frequencies[tuple(state)] = 1
    answer = 0

    for value in values:
        if value not in allowed:
            raise ValueError(f"Unexpected symbol: {value!r}")

        if value == reference:
            for i in range(len(state)):
                state[i] -= 1
        else:
            state[dimensions.index(value)] += 1

        key = tuple(state)
        answer += frequencies[key]
        frequencies[key] += 1

    return answer


def prefix_state_demo(values: List[int]) -> List[Tuple[int, int]]:
    """
    Return (index, prefix_sum) pairs to make the prefix-state concept
    directly observable.
    """
    result = []
    prefix = 0

    for index, value in enumerate(values):
        prefix += value
        result.append((index, prefix))

    return result


def demonstrate_edge_cases() -> None:
    cases = [
        ("all zero", [0, 0, 0], 0),
        ("negative values", [3, -2, -1, 4, -4], 0),
        ("target with negatives", [2, -1, 2, -2, 3], 1),
        ("empty", [], 0),
    ]

    for name, values, target in cases:
        count, matches = subarray_sum_equals_k(values, target)
        print(f"{name}: count={count}, matches={matches}")


def complexity_notes() -> None:
    print("\nComplexity:")
    print("Prefix-sum counting uses O(n) expected time and O(n) auxiliary space.")
    print("Storing every matching interval can require O(n^2) output space.")
    print("Earliest-prefix tracking finds longest matching intervals in O(n) expected time.")
    print("Tuple-based prefix states use O(n * d) state work for d frequency dimensions.")
    print("Hash-table performance depends on well-behaved hashing and available memory.")


def main() -> None:
    print("=== Prefix Sum + Hashing ===")

    numbers = [3, 4, -2, 1, -6, 5, 2]
    target = 5
    count, matches = subarray_sum_equals_k(numbers, target)
    print(f"\nSubarray sum target={target}")
    print(f"count={count}")
    print(f"ranges={matches}")

    length, interval = longest_subarray_sum_equals_k(numbers, target)
    print(f"longest length={length}, range={interval}")

    zero_data = [4, -1, -3, 2, -2, 5, -5]
    print("\nZero-sum subarrays")
    print(f"has zero-sum interval={has_zero_sum_subarray(zero_data)}")
    print(f"count={count_zero_sum_subarrays(zero_data)}")
    print(f"ranges={zero_sum_subarrays(zero_data)}")

    binary = [0, 1, 0, 0, 1, 1, 0]
    print("\nEqual number of zeros and ones")
    print(f"count={count_equal_zero_one_subarrays(binary)}")
    print(f"longest={longest_equal_zero_one_subarray(binary)}")

    symbols = list("AABCBACBCAB")
    print("\nEqual-frequency condition for A, B, C")
    print(f"longest={longest_equal_frequency_subarray(symbols, ['A', 'B', 'C'])}")
    print(
        "count=",
        count_subarrays_with_all_symbols_equal_frequency(
            symbols,
            ["A", "B", "C"],
        ),
    )

    print("\nPrefix states")
    print(prefix_state_demo([2, -2, 3, -3, 4]))

    demonstrate_edge_cases()
    complexity_notes()


if __name__ == "__main__":
    main()
