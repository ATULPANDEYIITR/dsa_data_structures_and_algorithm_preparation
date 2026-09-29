"""
Binary Search on Answer
=======================

A standalone study program covering binary search over an answer space rather
than over an explicitly sorted array.

Core pattern:

    Find the smallest x such that feasible(x) is True
    or
    Find the largest x such that feasible(x) is True

The central requirement is monotonic feasibility. The individual input values
do not necessarily need to be sorted. Instead, as the candidate answer moves
in one direction, feasibility must change only once:

    False False False True True True
    or
    True True True False False False

The examples progress from fundamentals to allocation, capacity, speed,
shipping, partitioning, and advanced generic implementations.

The program uses only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Callable, Iterable, Sequence


# ---------------------------------------------------------------------------
# 1. FUNDAMENTALS
# ---------------------------------------------------------------------------

def print_section(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def binary_search_first_true(
    low: int,
    high: int,
    feasible: Callable[[int], bool],
) -> int:
    """
    Return the smallest integer x in [low, high] for which feasible(x) is True.

    Precondition:
        feasible(x) is False before the transition and True from the transition
        onward, or low/high have already been narrowed to a valid search range.

    This is the most common form of binary search on answer.
    """
    if low > high:
        raise ValueError("low must not be greater than high")

    while low < high:
        mid = low + (high - low) // 2

        if feasible(mid):
            # mid works, but there may be a smaller feasible answer.
            high = mid
        else:
            # mid does not work, so every smaller value also fails.
            low = mid + 1

    return low


def binary_search_last_true(
    low: int,
    high: int,
    feasible: Callable[[int], bool],
) -> int:
    """
    Return the largest integer x in [low, high] for which feasible(x) is True.

    Expected pattern:

        True True True True False False

    The upper-midpoint avoids an infinite loop when low + 1 == high.
    """
    if low > high:
        raise ValueError("low must not be greater than high")

    while low < high:
        mid = low + (high - low + 1) // 2

        if feasible(mid):
            # mid works, and we want the largest feasible value.
            low = mid
        else:
            # mid fails, so every larger value also fails.
            high = mid - 1

    return low


def demonstrate_monotonicity() -> None:
    print_section("1. Monotonic Feasibility")

    threshold = 37
    values = list(range(30, 45))
    statuses = ["T" if value >= threshold else "F" for value in values]

    print("Candidate values :", values)
    print("Feasible pattern :", statuses)
    print("Transition occurs at:", threshold)

    answer = binary_search_first_true(
        min(values),
        max(values),
        lambda value: value >= threshold,
    )
    print("First feasible value:", answer)

    maximum = binary_search_last_true(
        min(values),
        max(values),
        lambda value: value <= threshold,
    )
    print("Last feasible value:", maximum)


# ---------------------------------------------------------------------------
# 2. MINIMUM FEASIBLE VALUE
# ---------------------------------------------------------------------------

def minimum_integer_with_square_at_least(target: int) -> int:
    """
    Find the smallest non-negative integer x for which x*x >= target.

    The array is never constructed. The answer space is [0, target].
    """
    if target < 0:
        raise ValueError("target must be non-negative")

    if target <= 1:
        return target

    return binary_search_first_true(
        0,
        target,
        lambda x: x * x >= target,
    )


def demonstrate_minimum_feasible() -> None:
    print_section("2. Minimum Feasible Value")

    for target in [0, 1, 2, 9, 10, 24, 100, 101]:
        answer = minimum_integer_with_square_at_least(target)
        print(
            f"target={target:3d} -> minimum x={answer:3d}, "
            f"x²={answer * answer}"
        )


# ---------------------------------------------------------------------------
# 3. MAXIMUM FEASIBLE VALUE
# ---------------------------------------------------------------------------

def maximum_uniform_production(
    machines: Sequence[int],
    time_limit: int,
) -> int:
    """
    Each machine produces one item every `machines[i]` time units.

    Find the maximum number of items that can be produced within the time
    limit.

    For a candidate production count x, calculate how much time is required.
    This is a maximum-answer problem transformed into a feasibility test.

    Feasibility pattern with respect to x:

        True True True ... False False
    """
    if time_limit < 0:
        raise ValueError("time_limit must be non-negative")
    if not machines or any(speed <= 0 for speed in machines):
        raise ValueError("machines must contain positive production times")

    upper_bound = time_limit * len(machines) // min(machines)

    def feasible(items: int) -> bool:
        required_time = 0

        for production_time in machines:
            required_time += items * production_time

            # This example represents a different model than parallel
            # production: each machine would process a share. Keep the
            # explicit implementation below for the actual parallel model.
            break

        # Correct parallel-production calculation:
        produced = sum(time_limit // production_time for production_time in machines)
        return produced >= items

    return binary_search_last_true(0, upper_bound, feasible)


def demonstrate_maximum_feasible() -> None:
    print_section("3. Maximum Feasible Value")

    machines = [2, 3, 5]
    time_limit = 10
    result = maximum_uniform_production(machines, time_limit)

    print("Machine times:", machines)
    print("Available time:", time_limit)
    print("Maximum items:", result)


# ---------------------------------------------------------------------------
# 4. CAPACITY PROBLEM: SHIP PACKAGES WITHIN D DAYS
# ---------------------------------------------------------------------------

def minimum_shipping_capacity(
    weights: Sequence[int],
    days: int,
) -> int:
    """
    Find the minimum ship capacity required to ship packages in order within
    a fixed number of days.

    Important observation:
        capacity < max(weights) is impossible.
        capacity = sum(weights) is always sufficient.

    Therefore:

        low  = max(weights)
        high = sum(weights)

    Feasibility is monotonic:

        small capacities -> impossible
        sufficiently large capacities -> possible
    """
    if not weights or any(weight <= 0 for weight in weights):
        raise ValueError("weights must contain positive integers")
    if days <= 0:
        raise ValueError("days must be positive")

    low = max(weights)
    high = sum(weights)

    def feasible(capacity: int) -> bool:
        required_days = 1
        current_load = 0

        for weight in weights:
            if current_load + weight <= capacity:
                current_load += weight
            else:
                required_days += 1
                current_load = weight

        return required_days <= days

    return binary_search_first_true(low, high, feasible)


def demonstrate_shipping() -> None:
    print_section("4. Minimum Shipping Capacity")

    cases = [
        ([1, 2, 3, 1, 1], 4),
        ([3, 2, 2, 4, 1, 4], 3),
        ([5, 5, 5, 5], 2),
        ([10], 1),
    ]

    for weights, days in cases:
        capacity = minimum_shipping_capacity(weights, days)
        print(
            f"weights={weights}, days={days} -> "
            f"minimum capacity={capacity}"
        )


# ---------------------------------------------------------------------------
# 5. MINIMUM SPEED PROBLEM: KOKO-STYLE
# ---------------------------------------------------------------------------

def minimum_speed_for_deadline(
    workloads: Sequence[int],
    hours: int,
) -> int:
    """
    Find the minimum integer processing speed that finishes every workload
    within the deadline.

    For speed s:

        hours_required = sum(ceil(workload / s))

    If speed s works, every speed greater than s also works.

    This gives the monotonic pattern:

        False False False True True True
    """
    if not workloads or any(workload <= 0 for workload in workloads):
        raise ValueError("workloads must contain positive integers")
    if hours <= 0:
        raise ValueError("hours must be positive")

    low = 1
    high = max(workloads)

    def feasible(speed: int) -> bool:
        hours_required = 0

        for workload in workloads:
            # Integer ceiling without floating-point arithmetic:
            hours_required += (workload + speed - 1) // speed

            if hours_required > hours:
                return False

        return True

    return binary_search_first_true(low, high, feasible)


def demonstrate_minimum_speed() -> None:
    print_section("5. Minimum Speed")

    cases = [
        ([3, 6, 7, 11], 8),
        ([30, 11, 23, 4, 20], 5),
        ([30, 11, 23, 4, 20], 6),
        ([1], 1),
    ]

    for workloads, hours in cases:
        speed = minimum_speed_for_deadline(workloads, hours)
        print(
            f"workloads={workloads}, hours={hours} -> "
            f"minimum speed={speed}"
        )


# ---------------------------------------------------------------------------
# 6. ALLOCATION: SPLIT ARRAY INTO K CONTIGUOUS GROUPS
# ---------------------------------------------------------------------------

def minimum_largest_partition_sum(
    values: Sequence[int],
    groups: int,
) -> int:
    """
    Split a sequence into at most `groups` contiguous non-empty partitions so
    that the largest partition sum is minimized.

    Answer-space bounds:

        low  = max(values)
        high = sum(values)

    Feasibility:
        Can the values be partitioned into at most `groups` pieces if no piece
        may exceed `limit`?

    Greedy construction is sufficient because values are non-negative.
    """
    if not values or any(value < 0 for value in values):
        raise ValueError("values must be non-negative and non-empty")
    if groups <= 0:
        raise ValueError("groups must be positive")
    if groups > len(values):
        groups = len(values)

    low = max(values)
    high = sum(values)

    def feasible(limit: int) -> bool:
        partition_count = 1
        current_sum = 0

        for value in values:
            if current_sum + value <= limit:
                current_sum += value
            else:
                partition_count += 1
                current_sum = value

                if partition_count > groups:
                    return False

        return True

    return binary_search_first_true(low, high, feasible)


def demonstrate_allocation() -> None:
    print_section("6. Allocation / Partitioning")

    cases = [
        ([7, 2, 5, 10, 8], 2),
        ([1, 2, 3, 4, 5], 2),
        ([10, 20, 30], 3),
        ([10, 20, 30], 1),
        ([0, 0, 5, 0], 2),
    ]

    for values, groups in cases:
        answer = minimum_largest_partition_sum(values, groups)
        print(
            f"values={values}, groups={groups} -> "
            f"minimum largest sum={answer}"
        )


# ---------------------------------------------------------------------------
# 7. MAXIMUM MINIMUM DISTANCE
# ---------------------------------------------------------------------------

def maximum_minimum_distance(
    positions: Sequence[int],
    objects: int,
) -> int:
    """
    Place `objects` items at distinct sorted positions so that the minimum
    distance between any two selected positions is as large as possible.

    This is a maximum-answer binary search.

    Candidate distance d is feasible if a greedy placement can select enough
    positions while maintaining at least d between consecutive selections.

    Feasibility pattern:

        small d -> True
        large d -> False
    """
    if not positions:
        raise ValueError("positions must not be empty")
    if objects <= 0 or objects > len(positions):
        raise ValueError("objects must be between 1 and len(positions)")

    sorted_positions = sorted(set(positions))

    if objects > len(sorted_positions):
        raise ValueError("objects require distinct positions")

    low = 0
    high = sorted_positions[-1] - sorted_positions[0]

    def feasible(distance: int) -> bool:
        selected = 1
        last_position = sorted_positions[0]

        for position in sorted_positions[1:]:
            if position - last_position >= distance:
                selected += 1
                last_position = position

                if selected >= objects:
                    return True

        return selected >= objects

    return binary_search_last_true(low, high, feasible)


def demonstrate_distance() -> None:
    print_section("7. Maximum Minimum Distance")

    positions = [1, 2, 4, 8, 9]
    objects = 3

    answer = maximum_minimum_distance(positions, objects)
    print("Positions:", positions)
    print("Objects:", objects)
    print("Maximum possible minimum distance:", answer)


# ---------------------------------------------------------------------------
# 8. PAINTER / WORK ALLOCATION
# ---------------------------------------------------------------------------

def minimum_time_for_workers(
    jobs: Sequence[int],
    workers: int,
) -> int:
    """
    Assign contiguous jobs to workers while minimizing the maximum workload.

    This is mathematically the same answer-space pattern as shipping capacity
    and contiguous partitioning.

    Jobs must remain in order. A worker can receive a contiguous segment.
    """
    if not jobs or any(job < 0 for job in jobs):
        raise ValueError("jobs must be non-negative and non-empty")
    if workers <= 0:
        raise ValueError("workers must be positive")

    workers = min(workers, len(jobs))
    low = max(jobs)
    high = sum(jobs)

    def feasible(max_work: int) -> bool:
        worker_count = 1
        current_work = 0

        for job in jobs:
            if current_work + job <= max_work:
                current_work += job
            else:
                worker_count += 1
                current_work = job

                if worker_count > workers:
                    return False

        return True

    return binary_search_first_true(low, high, feasible)


# ---------------------------------------------------------------------------
# 9. EDGE CASES AND FAILURE CONDITIONS
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    print_section("8. Edge Cases")

    print("Single element:", minimum_shipping_capacity([42], 1))
    print("Many days:", minimum_shipping_capacity([4, 5, 6], 10))
    print("One day:", minimum_shipping_capacity([4, 5, 6], 1))
    print("Single workload:", minimum_speed_for_deadline([100], 100))
    print(
        "One partition:",
        minimum_largest_partition_sum([3, 1, 8, 2], 1),
    )
    print(
        "Every element can be separate:",
        minimum_largest_partition_sum([3, 1, 8, 2], 4),
    )

    invalid_calls = [
        lambda: minimum_shipping_capacity([], 3),
        lambda: minimum_shipping_capacity([1, 2], 0),
        lambda: minimum_speed_for_deadline([], 3),
        lambda: maximum_minimum_distance([1, 2], 3),
    ]

    for index, call in enumerate(invalid_calls, start=1):
        try:
            call()
        except ValueError as error:
            print(f"Expected validation error {index}: {error}")


# ---------------------------------------------------------------------------
# 10. BRUTE FORCE VALIDATION
# ---------------------------------------------------------------------------

def brute_force_shipping_capacity(
    weights: Sequence[int],
    days: int,
) -> int:
    """Small-input reference implementation used to validate binary search."""
    for capacity in range(max(weights), sum(weights) + 1):
        current_load = 0
        required_days = 1

        for weight in weights:
            if current_load + weight <= capacity:
                current_load += weight
            else:
                required_days += 1
                current_load = weight

        if required_days <= days:
            return capacity

    raise RuntimeError("A feasible capacity must exist")


def validate_shipping_algorithm() -> None:
    print_section("9. Algorithm Validation")

    test_cases = [
        ([1, 2, 3], 2),
        ([2, 2, 2, 2], 2),
        ([5, 1, 1, 1], 3),
        ([7, 3, 4, 2], 2),
        ([9, 2, 8], 2),
    ]

    for weights, days in test_cases:
        optimized = minimum_shipping_capacity(weights, days)
        reference = brute_force_shipping_capacity(weights, days)

        assert optimized == reference, (
            f"Mismatch for {weights}, days={days}: "
            f"{optimized} != {reference}"
        )

        print(
            f"Validated weights={weights}, days={days}: "
            f"answer={optimized}"
        )


# ---------------------------------------------------------------------------
# 11. COMPLEXITY DISCUSSION THROUGH CODE
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Complexity:
    name: str
    feasibility_cost: str
    binary_search_cost: str
    total: str


def complexity_examples() -> list[Complexity]:
    """
    Binary search needs O(log R) feasibility checks, where R is the size of
    the numeric answer range.

    If each feasibility check scans n elements, total time is O(n log R).
    """
    return [
        Complexity(
            "Shipping capacity",
            "O(n)",
            "O(log(sum(weights) - max(weights) + 1))",
            "O(n log R)",
        ),
        Complexity(
            "Minimum processing speed",
            "O(n)",
            "O(log(max(workload)))",
            "O(n log R)",
        ),
        Complexity(
            "Contiguous allocation",
            "O(n)",
            "O(log(sum(values) - max(values) + 1))",
            "O(n log R)",
        ),
        Complexity(
            "Maximum minimum distance",
            "O(n)",
            "O(log(max_position - min_position + 1))",
            "O(n log R)",
        ),
    ]


def demonstrate_complexity() -> None:
    print_section("10. Complexity")

    for item in complexity_examples():
        print(f"{item.name}:")
        print(f"  Feasibility: {item.feasibility_cost}")
        print(f"  Search:      {item.binary_search_cost}")
        print(f"  Total:       {item.total}")


# ---------------------------------------------------------------------------
# 12. ADVANCED: GENERIC ANSWER-SPACE SEARCH WITH INTEGER DOMAIN
# ---------------------------------------------------------------------------

def first_true_with_iteration_trace(
    low: int,
    high: int,
    feasible: Callable[[int], bool],
) -> tuple[int, list[tuple[int, int, int, bool]]]:
    """
    Return both the first feasible answer and a trace.

    Each trace record is:
        (low_before, mid, high_before, result_of_feasible(mid))
    """
    trace: list[tuple[int, int, int, bool]] = []

    while low < high:
        old_low = low
        old_high = high
        mid = low + (high - low) // 2
        result = feasible(mid)

        trace.append((old_low, mid, old_high, result))

        if result:
            high = mid
        else:
            low = mid + 1

    return low, trace


def demonstrate_trace() -> None:
    print_section("11. Binary Search Trace")

    answer, trace = first_true_with_iteration_trace(
        1,
        100,
        lambda x: x >= 73,
    )

    for low, mid, high, result in trace:
        print(
            f"low={low:3d}, mid={mid:3d}, high={high:3d}, "
            f"feasible(mid)={result}"
        )

    print("Answer:", answer)


# ---------------------------------------------------------------------------
# 13. WHY BOUNDS MATTER
# ---------------------------------------------------------------------------

def explain_bounds_in_code() -> None:
    print_section("12. Choosing Search Bounds")

    examples = {
        "minimum capacity": {
            "lower_bound": "maximum individual item",
            "upper_bound": "sum of all items",
        },
        "minimum speed": {
            "lower_bound": "1",
            "upper_bound": "maximum workload",
        },
        "maximum distance": {
            "lower_bound": "0",
            "upper_bound": "last_position - first_position",
        },
        "minimum largest partition": {
            "lower_bound": "maximum element",
            "upper_bound": "sum of elements",
        },
    }

    for problem, bounds in examples.items():
        print(problem)
        print("  lower:", bounds["lower_bound"])
        print("  upper:", bounds["upper_bound"])


# ---------------------------------------------------------------------------
# 14. COMMON WRONG APPROACHES
# ---------------------------------------------------------------------------

def demonstrate_common_mistakes() -> None:
    print_section("13. Common Mistakes")

    print("Mistake 1: Searching an array when the answer itself is numeric.")
    print("Mistake 2: Forgetting that feasibility must be monotonic.")
    print("Mistake 3: Using low=0 when the answer cannot be zero.")
    print("Mistake 4: Using high too small, excluding the real answer.")
    print("Mistake 5: Using floating-point division where integer ceiling is enough.")
    print("Mistake 6: Overflow in low + high in fixed-width integer languages.")
    print("Mistake 7: Updating the wrong boundary after a feasible midpoint.")
    print("Mistake 8: Using lower-mid for last-true search and causing a loop.")
    print("Mistake 9: Ignoring ordering constraints in allocation problems.")
    print("Mistake 10: Assuming greedy feasibility works when the problem does not")
    print("          have the required structure.")


# ---------------------------------------------------------------------------
# 15. A COMPLETE MULTI-PROBLEM DEMONSTRATION
# ---------------------------------------------------------------------------

def run_case_study() -> None:
    print_section("14. Integrated Case Study")

    projects = [120, 80, 200, 150, 90, 60]
    engineers = 3

    workload_limit = minimum_time_for_workers(projects, engineers)

    print("Projects:", projects)
    print("Engineers:", engineers)
    print("Minimum possible maximum engineer workload:", workload_limit)

    packages = [10, 20, 30, 40, 50]
    delivery_days = 3
    capacity = minimum_shipping_capacity(packages, delivery_days)

    print("Packages:", packages)
    print("Delivery days:", delivery_days)
    print("Minimum required shipping capacity:", capacity)

    workloads = [50, 120, 80, 30]
    available_hours = 7
    speed = minimum_speed_for_deadline(workloads, available_hours)

    print("Workloads:", workloads)
    print("Available hours:", available_hours)
    print("Minimum processing speed:", speed)

    locations = [0, 4, 9, 15, 21, 30]
    units = 4
    spacing = maximum_minimum_distance(locations, units)

    print("Locations:", locations)
    print("Units:", units)
    print("Maximum minimum spacing:", spacing)


# ---------------------------------------------------------------------------
# 16. ASSERTION-BASED SELF TESTS
# ---------------------------------------------------------------------------

def run_self_tests() -> None:
    assert minimum_integer_with_square_at_least(0) == 0
    assert minimum_integer_with_square_at_least(1) == 1
    assert minimum_integer_with_square_at_least(2) == 2
    assert minimum_integer_with_square_at_least(8) == 3
    assert minimum_integer_with_square_at_least(9) == 3

    assert minimum_shipping_capacity([1, 2, 3, 1, 1], 4) == 3
    assert minimum_shipping_capacity([3, 2, 2, 4, 1, 4], 3) == 6

    assert minimum_speed_for_deadline([3, 6, 7, 11], 8) == 4
    assert minimum_speed_for_deadline([30, 11, 23, 4, 20], 5) == 30

    assert minimum_largest_partition_sum([7, 2, 5, 10, 8], 2) == 18
    assert minimum_largest_partition_sum([1, 2, 3, 4, 5], 2) == 9

    assert maximum_minimum_distance([1, 2, 4, 8, 9], 3) == 3

    assert minimum_time_for_workers([10, 20, 30], 2) == 30


# ---------------------------------------------------------------------------
# 17. PROGRAM ENTRY POINT
# ---------------------------------------------------------------------------

def main() -> None:
    print("BINARY SEARCH ON ANSWER")
    print("A complete executable study program")

    demonstrate_monotonicity()
    demonstrate_minimum_feasible()
    demonstrate_maximum_feasible()
    demonstrate_shipping()
    demonstrate_minimum_speed()
    demonstrate_allocation()
    demonstrate_distance()
    demonstrate_edge_cases()
    validate_shipping_algorithm()
    demonstrate_complexity()
    demonstrate_trace()
    explain_bounds_in_code()
    demonstrate_common_mistakes()
    run_case_study()

    run_self_tests()

    print_section("15. Self Tests")
    print("All assertion-based tests passed.")


if __name__ == "__main__":
    main()
