"""Maps and sets: frequency counting, duplicate detection, uniqueness,
membership testing, intersections, unions, and practical data analysis.

Run with Python 3.10 or later. The implementation uses only the standard library.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from time import perf_counter
from typing import Hashable, Iterable, TypeVar

T = TypeVar("T", bound=Hashable)


def heading(title: str) -> None:
    print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")


def frequency_count(values: Iterable[T]) -> Counter[T]:
    """Count hashable values in expected O(n) time."""
    return Counter(values)


def frequency_count_manually(values: Iterable[T]) -> dict[T, int]:
    """Expose the map update mechanism explicitly."""
    frequencies: dict[T, int] = {}
    for value in values:
        frequencies[value] = frequencies.get(value, 0) + 1
    return frequencies


def find_duplicates(values: Iterable[T]) -> set[T]:
    """Return each duplicated value once."""
    seen: set[T] = set()
    duplicates: set[T] = set()

    for value in values:
        if value in seen:
            duplicates.add(value)
        else:
            seen.add(value)

    return duplicates


def find_duplicate_occurrences(values: Iterable[T]) -> list[T]:
    """Return every occurrence after the first occurrence."""
    seen: set[T] = set()
    repeated: list[T] = []

    for value in values:
        if value in seen:
            repeated.append(value)
        else:
            seen.add(value)

    return repeated


def unique_elements(values: Iterable[T]) -> list[T]:
    """Preserve first-occurrence order while removing duplicates."""
    return list(dict.fromkeys(values))


def elements_appearing_once(values: Iterable[T]) -> list[T]:
    """Return values whose total frequency is exactly one."""
    counts = Counter(values)
    return [value for value, count in counts.items() if count == 1]


def membership_report(
    requested: Iterable[T], available: Iterable[T]
) -> dict[T, bool]:
    """Build a set once instead of repeatedly scanning a list."""
    available_set = set(available)
    return {item: item in available_set for item in requested}


def set_operations(
    first: Iterable[T], second: Iterable[T]
) -> dict[str, set[T]]:
    left = set(first)
    right = set(second)

    return {
        "union": left | right,
        "intersection": left & right,
        "left_only": left - right,
        "right_only": right - left,
        "symmetric_difference": left ^ right,
    }


def common_to_all(groups: Iterable[Iterable[T]]) -> set[T]:
    """Find values present in every group, including correct empty handling."""
    iterator = iter(groups)
    try:
        result = set(next(iterator))
    except StopIteration:
        return set()

    for group in iterator:
        result.intersection_update(group)
        if not result:
            break

    return result


def group_by_frequency(values: Iterable[T]) -> dict[int, list[T]]:
    """Group distinct values by their occurrence count."""
    result: dict[int, list[T]] = defaultdict(list)
    for value, count in Counter(values).items():
        result[count].append(value)

    return dict(sorted(result.items()))


@dataclass(frozen=True)
class AccessEvent:
    employee_id: str
    resource: str
    outcome: str


class AccessAudit:
    """Analyze access events using maps and sets."""

    VALID_OUTCOMES = {"allowed", "denied"}

    def __init__(self) -> None:
        self.events: list[AccessEvent] = []
        self.by_employee: dict[str, Counter[str]] = defaultdict(Counter)
        self.denied_resources: set[str] = set()
        self.employees_by_resource: dict[str, set[str]] = defaultdict(set)

    def record(self, event: AccessEvent) -> None:
        if not event.employee_id.strip():
            raise ValueError("Employee ID cannot be empty.")
        if not event.resource.strip():
            raise ValueError("Resource cannot be empty.")
        if event.outcome not in self.VALID_OUTCOMES:
            raise ValueError(f"Invalid outcome: {event.outcome!r}")

        self.events.append(event)
        self.by_employee[event.employee_id][event.outcome] += 1
        self.employees_by_resource[event.resource].add(event.employee_id)

        if event.outcome == "denied":
            self.denied_resources.add(event.resource)

    def denied_count(self, employee_id: str) -> int:
        return self.by_employee.get(employee_id, Counter()).get("denied", 0)

    def repeated_denials(self, threshold: int = 2) -> dict[str, int]:
        if threshold < 1:
            raise ValueError("Threshold must be positive.")

        return {
            employee: counts["denied"]
            for employee, counts in self.by_employee.items()
            if counts["denied"] >= threshold
        }

    def employees_with_denials_on(
        self, resource: str
    ) -> set[str]:
        return {
            event.employee_id
            for event in self.events
            if event.resource == resource and event.outcome == "denied"
        }

    def shared_resource_users(
        self, first_resource: str, second_resource: str
    ) -> set[str]:
        return (
            self.employees_by_resource[first_resource]
            & self.employees_by_resource[second_resource]
        )


def benchmark_membership(size: int = 100_000) -> None:
    """Compare repeated list scans with hash-set membership."""
    if size < 1:
        raise ValueError("Size must be positive.")

    available = list(range(size))
    queries = list(range(size - 100, size + 100))
    available_set = set(available)

    start = perf_counter()
    list_results = [item in available for item in queries]
    list_seconds = perf_counter() - start

    start = perf_counter()
    set_results = [item in available_set for item in queries]
    set_seconds = perf_counter() - start

    assert list_results == set_results
    print(f"Queries: {len(queries):,}; stored elements: {size:,}")
    print(f"List membership: {list_seconds:.6f} seconds")
    print(f"Set membership:  {set_seconds:.6f} seconds")
    print("Timings depend on hardware, data distribution, and runtime state.")


def demonstrate_fundamentals() -> None:
    heading("Frequency counting")
    status_codes = [200, 404, 200, 500, 404, 200, 302, 500, 404]
    print("Counter:", frequency_count(status_codes))
    print("Manual map:", frequency_count_manually(status_codes))

    heading("Duplicate detection and uniqueness")
    serial_numbers = ["SN-10", "SN-11", "SN-10", "SN-12", "SN-11"]
    print("Duplicate values:", find_duplicates(serial_numbers))
    print("Repeated occurrences:", find_duplicate_occurrences(serial_numbers))
    print("Unique sequence:", unique_elements(serial_numbers))
    print("Elements appearing once:", elements_appearing_once(serial_numbers))

    heading("Membership testing")
    requested_permissions = {"read", "deploy", "audit"}
    granted_permissions = {"read", "audit", "monitor"}
    print(membership_report(requested_permissions, granted_permissions))

    heading("Set operations")
    print(set_operations(granted_permissions, requested_permissions))

    heading("Intersection across multiple groups")
    team_a = {"Python", "SQL", "Git"}
    team_b = {"SQL", "Git", "Docker"}
    team_c = {"SQL", "Git", "Linux"}
    print("Shared skills:", common_to_all([team_a, team_b, team_c]))
    print("Intersection of no groups:", common_to_all([]))
    print("Intersection containing an empty group:", common_to_all([team_a, set()]))

    heading("Frequency distribution")
    print(group_by_frequency(["api", "db", "api", "cache", "db", "api"]))


def demonstrate_access_audit() -> None:
    heading("Repository access audit")
    audit = AccessAudit()

    events = [
        AccessEvent("EMP-101", "production", "denied"),
        AccessEvent("EMP-101", "production", "denied"),
        AccessEvent("EMP-101", "staging", "allowed"),
        AccessEvent("EMP-102", "production", "allowed"),
        AccessEvent("EMP-102", "staging", "allowed"),
        AccessEvent("EMP-103", "production", "denied"),
        AccessEvent("EMP-103", "repository", "denied"),
        AccessEvent("EMP-104", "repository", "allowed"),
    ]

    for event in events:
        audit.record(event)

    print("Employees with repeated denials:", audit.repeated_denials())
    print("Employees denied production access:",
          audit.employees_with_denials_on("production"))
    print("Employees accessing both environments:",
          audit.shared_resource_users("production", "staging"))
    print("Resources with at least one denial:", audit.denied_resources)

    try:
        audit.record(AccessEvent("EMP-105", "production", "unknown"))
    except ValueError as error:
        print("Validation correctly rejected event:", error)


def demonstrate_edge_cases() -> None:
    heading("Edge cases and correctness")
    print("Empty frequency map:", frequency_count([]))
    print("Duplicates in empty input:", find_duplicates([]))
    print("Single element:", unique_elements(["only"]))
    print("Case-sensitive membership:", "Admin" in {"admin"})
    print("Empty-set union:", set() | {1, 2})
    print("Empty-set intersection:", set() & {1, 2})

    # Mutable objects cannot be set elements or dictionary keys.
    try:
        set([[1, 2], [1, 2]])
    except TypeError as error:
        print("Unhashable list rejected:", error)

    # Convert structured mutable values to immutable tuples when appropriate.
    records = [[1, "open"], [2, "closed"], [1, "open"]]
    normalized = {tuple(record) for record in records}
    print("Normalized structured records:", normalized)

    # Hashable custom objects must keep equality and hashing consistent.
    print("Boolean and integer equality:", {True, 1, 1.0})


def main() -> None:
    demonstrate_fundamentals()
    demonstrate_access_audit()
    demonstrate_edge_cases()

    heading("Membership performance experiment")
    benchmark_membership(20_000)


if __name__ == "__main__":
    main()
