"""
Day 27 — Linear Search
=======================

A standalone study and executable demonstration of linear search.

Topics covered:
- Sequential search
- Search conditions
- First occurrence
- Last occurrence
- Searching unsorted data
- Searching sorted data
- Exact and predicate-based searches
- Duplicates
- Missing values
- Empty and singleton collections
- Sentinel-style reasoning
- Linear search variants
- Complexity analysis
- Comparisons with binary search
- Practical applications
- Validation and testing
- Performance measurement
- Advanced reusable search abstractions
- Real-world record searching

The examples use only Python's standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Iterable, Optional, Sequence, TypeVar


T = TypeVar("T")


# ============================================================================
# 1. FUNDAMENTAL IDEA
# ============================================================================

def linear_search(items: Sequence[T], target: T) -> int:
    """
    Return the index of the first element equal to target.

    Linear search examines elements sequentially from left to right.

    Example:
        [17, 4, 9, 23], target=9
        checks 17 -> 4 -> 9
        returns 2

    If the target is absent, return -1.
    """
    for index, item in enumerate(items):
        if item == target:
            return index
    return -1


def demonstrate_basic_search() -> None:
    print("\n" + "=" * 72)
    print("1. BASIC LINEAR SEARCH")
    print("=" * 72)

    numbers = [17, 4, 9, 23, 11, 8]

    print("Data:", numbers)
    print("Search for 23:", linear_search(numbers, 23))
    print("Search for 99:", linear_search(numbers, 99))


# ============================================================================
# 2. STEP-BY-STEP SEQUENTIAL SEARCH
# ============================================================================

def linear_search_with_trace(items: Sequence[T], target: T) -> int:
    """
    Show every comparison made by a linear search.

    This is useful for understanding the algorithm rather than for production
    code, because printing every comparison adds substantial overhead.
    """
    for index, item in enumerate(items):
        print(f"  Compare index {index}: {item!r} == {target!r}?")
        if item == target:
            print(f"  Match found at index {index}.")
            return index

    print("  Target was not found.")
    return -1


def demonstrate_sequential_process() -> None:
    print("\n" + "=" * 72)
    print("2. SEQUENTIAL SEARCH PROCESS")
    print("=" * 72)

    values = [31, 12, 44, 7, 25]
    print("Data:", values)

    print("\nSearching for 44:")
    linear_search_with_trace(values, 44)

    print("\nSearching for 100:")
    linear_search_with_trace(values, 100)


# ============================================================================
# 3. SEARCH CONDITIONS
# ============================================================================

def find_first(
    items: Iterable[T],
    condition: Callable[[T], bool],
) -> Optional[T]:
    """
    Return the first element satisfying condition.

    This generalizes linear search beyond equality.

    Example:
        find_first([3, 8, 11, 14], lambda x: x > 10)
        -> 11
    """
    for item in items:
        if condition(item):
            return item
    return None


def find_first_index(
    items: Sequence[T],
    condition: Callable[[T], bool],
) -> int:
    """Return the first index satisfying condition, or -1."""
    for index, item in enumerate(items):
        if condition(item):
            return index
    return -1


def demonstrate_search_conditions() -> None:
    print("\n" + "=" * 72)
    print("3. SEARCH CONDITIONS")
    print("=" * 72)

    values = [4, 7, 12, 15, 22, 31]

    even_index = find_first_index(values, lambda value: value % 2 == 0)
    greater_than_20 = find_first(values, lambda value: value > 20)
    divisible_by_3 = find_first(values, lambda value: value % 3 == 0)

    print("Data:", values)
    print("First even value:", find_first(values, lambda value: value % 2 == 0))
    print("Index of first even value:", even_index)
    print("First value > 20:", greater_than_20)
    print("First value divisible by 3:", divisible_by_3)


# ============================================================================
# 4. FIRST OCCURRENCE
# ============================================================================

def first_occurrence(items: Sequence[T], target: T) -> int:
    """
    Return the first index containing target.

    Because the scan stops immediately after the first match, the algorithm
    does not inspect elements after that occurrence.
    """
    for index, item in enumerate(items):
        if item == target:
            return index
    return -1


def demonstrate_first_occurrence() -> None:
    print("\n" + "=" * 72)
    print("4. FIRST OCCURRENCE")
    print("=" * 72)

    values = [5, 8, 5, 2, 5, 9]

    print("Data:", values)
    print("First occurrence of 5:", first_occurrence(values, 5))
    print("First occurrence of 9:", first_occurrence(values, 9))
    print("First occurrence of 100:", first_occurrence(values, 100))


# ============================================================================
# 5. LAST OCCURRENCE
# ============================================================================

def last_occurrence(items: Sequence[T], target: T) -> int:
    """
    Return the last index containing target.

    Unlike ordinary first-match search, the complete collection may need to
    be scanned because a later occurrence could exist.
    """
    last_index = -1

    for index, item in enumerate(items):
        if item == target:
            last_index = index

    return last_index


def demonstrate_last_occurrence() -> None:
    print("\n" + "=" * 72)
    print("5. LAST OCCURRENCE")
    print("=" * 72)

    values = [5, 8, 5, 2, 5, 9, 5]

    print("Data:", values)
    print("Last occurrence of 5:", last_occurrence(values, 5))
    print("Last occurrence of 9:", last_occurrence(values, 9))
    print("Last occurrence of 100:", last_occurrence(values, 100))


# ============================================================================
# 6. ALL OCCURRENCES
# ============================================================================

def all_occurrences(items: Sequence[T], target: T) -> list[int]:
    """Return every index at which target occurs."""
    return [
        index
        for index, item in enumerate(items)
        if item == target
    ]


def demonstrate_all_occurrences() -> None:
    print("\n" + "=" * 72)
    print("6. ALL OCCURRENCES")
    print("=" * 72)

    values = [2, 7, 2, 9, 2, 4, 2]

    print("Data:", values)
    print("All occurrences of 2:", all_occurrences(values, 2))
    print("All occurrences of 10:", all_occurrences(values, 10))


# ============================================================================
# 7. SEARCH BY CONDITION AND RETURN INDEX
# ============================================================================

def first_index_where(
    items: Sequence[T],
    condition: Callable[[T], bool],
) -> Optional[int]:
    """
    Generic first-match search.

    None is used for absence rather than -1 because this function's result
    is conceptually an optional index.
    """
    for index, item in enumerate(items):
        if condition(item):
            return index
    return None


def last_index_where(
    items: Sequence[T],
    condition: Callable[[T], bool],
) -> Optional[int]:
    """Generic last-match search using a forward scan."""
    result: Optional[int] = None

    for index, item in enumerate(items):
        if condition(item):
            result = index

    return result


def demonstrate_predicate_search() -> None:
    print("\n" + "=" * 72)
    print("7. PREDICATE-BASED SEARCH")
    print("=" * 72)

    temperatures = [18.5, 21.2, 19.7, 27.3, 27.3, 16.8]

    hot = lambda temperature: temperature >= 25
    print("Temperatures:", temperatures)
    print("First temperature >= 25:", find_first(temperatures, hot))
    print("First hot index:", first_index_where(temperatures, hot))
    print("Last hot index:", last_index_where(temperatures, hot))


# ============================================================================
# 8. EDGE CASES
# ============================================================================

def demonstrate_edge_cases() -> None:
    print("\n" + "=" * 72)
    print("8. EDGE CASES")
    print("=" * 72)

    cases = [
        ("empty list", [], 10),
        ("single matching element", [10], 10),
        ("single non-matching element", [10], 20),
        ("target at beginning", [10, 20, 30], 10),
        ("target in middle", [10, 20, 30], 20),
        ("target at end", [10, 20, 30], 30),
        ("many duplicates", [7, 7, 7, 7], 7),
        ("negative values", [-5, -3, -1, 2], -3),
    ]

    for description, values, target in cases:
        print(
            f"{description:30} "
            f"data={values!r:20} target={target!r:4} "
            f"first={first_occurrence(values, target):2} "
            f"last={last_occurrence(values, target):2}"
        )


# ============================================================================
# 9. STRINGS
# ============================================================================

def demonstrate_string_search() -> None:
    print("\n" + "=" * 72)
    print("9. STRING SEARCH")
    print("=" * 72)

    words = ["database", "network", "python", "algorithm", "security"]

    print("Words:", words)
    print("Index of 'algorithm':", linear_search(words, "algorithm"))
    print("Index of 'PYTHON':", linear_search(words, "PYTHON"))

    # Equality is case-sensitive by default.
    case_insensitive_index = first_index_where(
        words,
        lambda word: word.lower() == "PYTHON".lower(),
    )
    print("Case-insensitive index of 'PYTHON':", case_insensitive_index)


# ============================================================================
# 10. SEARCHING OBJECTS
# ============================================================================

@dataclass(frozen=True)
class Student:
    student_id: int
    name: str
    score: float


def find_student_by_id(
    students: Sequence[Student],
    student_id: int,
) -> Optional[Student]:
    """Linear search through records using a selected field."""
    for student in students:
        if student.student_id == student_id:
            return student
    return None


def demonstrate_object_search() -> None:
    print("\n" + "=" * 72)
    print("10. SEARCHING OBJECTS")
    print("=" * 72)

    students = [
        Student(101, "Asha", 84.5),
        Student(102, "Rahul", 91.0),
        Student(103, "Meera", 76.5),
        Student(104, "Vikram", 88.0),
    ]

    student = find_student_by_id(students, 103)
    missing_student = find_student_by_id(students, 999)

    print("Student with ID 103:", student)
    print("Student with ID 999:", missing_student)


# ============================================================================
# 11. MULTIPLE SEARCH CONDITIONS
# ============================================================================

def find_first_student_above_score(
    students: Sequence[Student],
    minimum_score: float,
) -> Optional[Student]:
    """
    Search by a compound condition.

    A linear scan is appropriate when records are not indexed by score.
    """
    for student in students:
        if student.score >= minimum_score:
            return student
    return None


def demonstrate_compound_conditions() -> None:
    print("\n" + "=" * 72)
    print("11. COMPOUND SEARCH CONDITIONS")
    print("=" * 72)

    students = [
        Student(201, "Asha", 71),
        Student(202, "Rahul", 83),
        Student(203, "Meera", 95),
        Student(204, "Vikram", 88),
    ]

    result = find_first_student_above_score(students, 90)
    print("First student with score >= 90:", result)


# ============================================================================
# 12. SORTED DATA DOES NOT AUTOMATICALLY MAKE LINEAR SEARCH LOGARITHMIC
# ============================================================================

def linear_search_sorted(items: Sequence[T], target: T) -> int:
    """
    Linear search over sorted data.

    The sorted order permits early termination when item > target.

    This can reduce practical work, but the worst-case complexity remains O(n).
    """
    for index, item in enumerate(items):
        if item == target:
            return index

        if item > target:
            return -1

    return -1


def demonstrate_sorted_early_exit() -> None:
    print("\n" + "=" * 72)
    print("12. LINEAR SEARCH WITH SORTED-DATA EARLY EXIT")
    print("=" * 72)

    values = [4, 8, 13, 21, 29, 35]

    print("Sorted data:", values)
    print("Search for 21:", linear_search_sorted(values, 21))
    print("Search for 20:", linear_search_sorted(values, 20))
    print("Search for 40:", linear_search_sorted(values, 40))


# ============================================================================
# 13. REVERSE LINEAR SEARCH
# ============================================================================

def last_occurrence_reverse(items: Sequence[T], target: T) -> int:
    """
    Find the last occurrence by scanning from right to left.

    For an indexable sequence, this can stop as soon as the first match from
    the right is encountered.
    """
    for index in range(len(items) - 1, -1, -1):
        if items[index] == target:
            return index
    return -1


def demonstrate_reverse_search() -> None:
    print("\n" + "=" * 72)
    print("13. REVERSE LINEAR SEARCH")
    print("=" * 72)

    values = [3, 9, 3, 4, 8, 3, 10]

    print("Data:", values)
    print("Last occurrence using reverse scan:", last_occurrence_reverse(values, 3))


# ============================================================================
# 14. GENERATOR-BASED LINEAR SEARCH
# ============================================================================

def generate_numbers() -> Iterable[int]:
    """Produce values lazily to demonstrate that search need not require a list."""
    for number in range(1, 101):
        yield number


def find_first_in_iterable(
    items: Iterable[T],
    target: T,
) -> Optional[T]:
    """
    Search any iterable sequentially.

    This can work with generators and streams where random access is impossible.
    """
    for item in items:
        if item == target:
            return item
    return None


def demonstrate_iterable_search() -> None:
    print("\n" + "=" * 72)
    print("14. SEARCHING A LAZY ITERABLE")
    print("=" * 72)

    print("Searching generated values for 73:")
    print(find_first_in_iterable(generate_numbers(), 73))

    print("Searching generated values for 1000:")
    print(find_first_in_iterable(generate_numbers(), 1000))


# ============================================================================
# 15. SEARCHING WITH CUSTOM OBJECTS
# ============================================================================

@dataclass(frozen=True)
class Product:
    product_code: str
    name: str
    price: float
    stock: int


def find_product(
    products: Sequence[Product],
    product_code: str,
) -> Optional[Product]:
    """Find the first product having a matching product code."""
    for product in products:
        if product.product_code == product_code:
            return product
    return None


def find_first_in_stock(
    products: Sequence[Product],
) -> Optional[Product]:
    """Find the first product whose stock is greater than zero."""
    for product in products:
        if product.stock > 0:
            return product
    return None


def demonstrate_realistic_records() -> None:
    print("\n" + "=" * 72)
    print("15. REALISTIC RECORD SEARCH")
    print("=" * 72)

    products = [
        Product("P100", "Keyboard", 2499.00, 0),
        Product("P101", "Mouse", 899.00, 12),
        Product("P102", "Monitor", 14999.00, 4),
        Product("P103", "Webcam", 3999.00, 0),
    ]

    print("Product P102:", find_product(products, "P102"))
    print("First product in stock:", find_first_in_stock(products))


# ============================================================================
# 16. SEARCH RESULT AS A STRUCTURED OBJECT
# ============================================================================

@dataclass(frozen=True)
class SearchResult:
    found: bool
    index: Optional[int]
    comparisons: int


def search_with_statistics(
    items: Sequence[T],
    target: T,
) -> SearchResult:
    """
    Return both the result and the number of equality comparisons.

    This makes the relationship between algorithmic position and running work
    explicit.
    """
    comparisons = 0

    for index, item in enumerate(items):
        comparisons += 1

        if item == target:
            return SearchResult(True, index, comparisons)

    return SearchResult(False, None, comparisons)


def demonstrate_search_statistics() -> None:
    print("\n" + "=" * 72)
    print("16. COMPARISON COUNT")
    print("=" * 72)

    values = [11, 22, 33, 44, 55]

    for target in [11, 33, 55, 99]:
        result = search_with_statistics(values, target)
        print(
            f"target={target:2} -> found={result.found}, "
            f"index={result.index}, comparisons={result.comparisons}"
        )


# ============================================================================
# 17. COMPLEXITY ANALYSIS
# ============================================================================

def explain_complexity() -> None:
    print("\n" + "=" * 72)
    print("17. COMPLEXITY ANALYSIS")
    print("=" * 72)

    print(
        """
Let n be the number of elements.

Best case:
    O(1)
    The target is at the first position.

Worst case:
    O(n)
    The target is at the last position or is absent.

Average case:
    O(n)
    Under the common assumption that a successful target is equally likely
    to occur at any position, approximately (n + 1) / 2 comparisons are made.

Space complexity:
    O(1)
    The basic iterative algorithm uses constant auxiliary space.

Important distinction:
    O(n) describes how work grows with input size. It does not mean that
    every search performs exactly n comparisons.
"""
    )


# ============================================================================
# 18. FORMAL COMPARISON COUNTS
# ============================================================================

def comparison_count_successful(n: int, position: int) -> int:
    """
    Return the exact number of comparisons for zero-based position.

    Position 0 -> 1 comparison
    Position n-1 -> n comparisons
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if not 0 <= position < n:
        raise ValueError("position must be within the sequence")
    return position + 1


def comparison_count_unsuccessful(n: int) -> int:
    """An unsuccessful search examines every element."""
    if n < 0:
        raise ValueError("n cannot be negative")
    return n


def demonstrate_exact_counts() -> None:
    print("\n" + "=" * 72)
    print("18. EXACT COMPARISON COUNTS")
    print("=" * 72)

    n = 8

    for position in [0, 2, 7]:
        print(
            f"n={n}, target position={position}: "
            f"{comparison_count_successful(n, position)} comparisons"
        )

    print(
        f"n={n}, unsuccessful search: "
        f"{comparison_count_unsuccessful(n)} comparisons"
    )


# ============================================================================
# 19. LINEAR SEARCH VERSUS BINARY SEARCH
# ============================================================================

def binary_search(items: Sequence[T], target: T) -> int:
    """
    Binary search for sorted data.

    It repeatedly halves the remaining search interval.

    Requirement:
        items must be sorted according to the same ordering used for target.

    Complexity:
        O(log n) time
        O(1) auxiliary space for this iterative implementation
    """
    left = 0
    right = len(items) - 1

    while left <= right:
        middle = left + (right - left) // 2

        if items[middle] == target:
            return middle
        if items[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


def compare_search_requirements() -> None:
    print("\n" + "=" * 72)
    print("19. LINEAR SEARCH VS BINARY SEARCH")
    print("=" * 72)

    sorted_values = [3, 8, 12, 17, 24, 31, 45, 51]

    print("Sorted data:", sorted_values)
    print("Linear search for 24:", linear_search(sorted_values, 24))
    print("Binary search for 24:", binary_search(sorted_values, 24))

    print(
        """
Linear search:
    - Does not require sorted data.
    - Works with arbitrary iterables.
    - Simple implementation.
    - Worst-case O(n).

Binary search:
    - Requires suitable sorted data.
    - Uses ordering rather than checking every element.
    - Worst-case O(log n).
    - Usually requires random access for efficient array implementation.

Choosing an algorithm depends on data organization, search frequency,
ordering guarantees, update cost, and access characteristics.
"""
    )


# ============================================================================
# 20. DUPLICATES AND SEARCH SEMANTICS
# ============================================================================

def demonstrate_duplicate_semantics() -> None:
    print("\n" + "=" * 72)
    print("20. DUPLICATE VALUES")
    print("=" * 72)

    values = [10, 20, 30, 20, 40, 20, 50]

    print("Data:", values)
    print("First occurrence of 20:", first_occurrence(values, 20))
    print("Last occurrence of 20:", last_occurrence(values, 20))
    print("All occurrences of 20:", all_occurrences(values, 20))

    print(
        """
A search function must define what "found" means.

Possible contracts include:
    - return whether a match exists
    - return the first matching index
    - return the last matching index
    - return every matching index
    - return the first matching object
    - return a count of matches
"""
    )


# ============================================================================
# 21. COUNTING OCCURRENCES
# ============================================================================

def count_occurrences(items: Iterable[T], target: T) -> int:
    """Count matches using one sequential pass."""
    count = 0

    for item in items:
        if item == target:
            count += 1

    return count


def demonstrate_counting() -> None:
    print("\n" + "=" * 72)
    print("21. COUNTING MATCHES")
    print("=" * 72)

    values = [4, 4, 1, 9, 4, 7, 4]
    print("Data:", values)
    print("Number of occurrences of 4:", count_occurrences(values, 4))


# ============================================================================
# 22. EARLY EXIT VERSUS FULL SCAN
# ============================================================================

def exists(items: Iterable[T], target: T) -> bool:
    """Return immediately after the first match."""
    for item in items:
        if item == target:
            return True
    return False


def demonstrate_early_exit() -> None:
    print("\n" + "=" * 72)
    print("22. EARLY EXIT")
    print("=" * 72)

    values = [99, 12, 45, 72, 18, 30]

    print("Data:", values)
    print("Does 99 exist?", exists(values, 99))
    print("Does 30 exist?", exists(values, 30))
    print("Does 100 exist?", exists(values, 100))

    print(
        """
Early exit is a major practical property of linear search.

For a boolean existence query:
    target at first position -> one comparison
    target near beginning -> few comparisons
    target at end -> n comparisons
    target absent -> n comparisons
"""
    )


# ============================================================================
# 23. VALIDATION
# ============================================================================

def validate_search_input(items: Sequence[T]) -> None:
    """
    Validate an input sequence when a sequence is required.

    The function accepts empty sequences because an empty collection is a
    legitimate search input.
    """
    if items is None:
        raise TypeError("items cannot be None")


def safe_linear_search(
    items: Sequence[T],
    target: T,
) -> int:
    """Validated public-facing wrapper."""
    validate_search_input(items)
    return linear_search(items, target)


def demonstrate_validation() -> None:
    print("\n" + "=" * 72)
    print("23. VALIDATION")
    print("=" * 72)

    print("Valid search:", safe_linear_search([1, 2, 3], 2))

    try:
        safe_linear_search(None, 2)  # type: ignore[arg-type]
    except TypeError as error:
        print("Expected validation error:", error)


# ============================================================================
# 24. COMMON MISTAKES
# ============================================================================

def demonstrate_common_mistakes() -> None:
    print("\n" + "=" * 72)
    print("24. COMMON MISTAKES")
    print("=" * 72)

    print(
        """
1. Returning after comparing only the first element.
2. Forgetting to return immediately for a first-occurrence search.
3. Forgetting to update the result for a last-occurrence search.
4. Returning an arbitrary duplicate rather than defining search semantics.
5. Assuming sorted input when the algorithm does not require it.
6. Using binary search on unsorted data.
7. Off-by-one errors when iterating with indices.
8. Confusing an absent result with a valid index.
   Index -1 is useful because normal Python sequence indices are >= 0.
9. Modifying the collection unexpectedly during a search.
10. Performing expensive work inside the comparison condition.
11. Claiming linear search is always slow without considering n, access cost,
    data ordering, or the number of searches.
12. Ignoring the cost of maintaining a separate index or dictionary when
    repeated queries could justify one.
"""
    )


# ============================================================================
# 25. PERFORMANCE CONSIDERATIONS
# ============================================================================

def benchmark_search(
    size: int,
    target_position: int,
) -> tuple[float, int]:
    """
    Measure one search while also returning the number of comparisons.

    Timing values vary by computer and should be treated as demonstrations,
    not universal performance measurements.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    if not 0 <= target_position < size:
        raise ValueError("target_position must be within the data")

    values = list(range(size))
    target = values[target_position]

    start = perf_counter()
    result = search_with_statistics(values, target)
    elapsed = perf_counter() - start

    assert result.index == target_position
    return elapsed, result.comparisons


def demonstrate_performance() -> None:
    print("\n" + "=" * 72)
    print("25. PERFORMANCE")
    print("=" * 72)

    for size in [100, 10_000, 100_000]:
        position = size - 1
        elapsed, comparisons = benchmark_search(size, position)

        print(
            f"n={size:>7}: comparisons={comparisons:>7}, "
            f"time={elapsed:.8f} seconds"
        )

    print(
        """
Benchmarking observations:
    - Runtime depends on hardware, interpreter/runtime, memory hierarchy,
      compiler optimizations, and implementation details.
    - Comparison count is a more stable algorithmic measure.
    - Big-O describes growth, not an exact execution time.
"""
    )


# ============================================================================
# 26. WHEN LINEAR SEARCH IS A GOOD CHOICE
# ============================================================================

def demonstrate_use_cases() -> None:
    print("\n" + "=" * 72)
    print("26. PRACTICAL USE CASES")
    print("=" * 72)

    use_cases = [
        "Searching a small list",
        "Checking a stream until a matching event appears",
        "Searching unsorted records",
        "Finding the first item satisfying a business rule",
        "Scanning log entries sequentially",
        "Searching a short configuration collection",
        "Finding the first available resource",
        "Finding a matching record in an in-memory collection",
    ]

    for number, use_case in enumerate(use_cases, start=1):
        print(f"{number}. {use_case}")


# ============================================================================
# 27. STREAMING EXAMPLE
# ============================================================================

@dataclass(frozen=True)
class Event:
    event_id: int
    event_type: str
    severity: str


def find_first_critical_event(
    events: Iterable[Event],
) -> Optional[Event]:
    """
    Search a stream for the first critical event.

    A generator or external stream could be used instead of a list. The search
    stops as soon as a matching event is observed.
    """
    for event in events:
        if event.severity.lower() == "critical":
            return event
    return None


def demonstrate_stream_search() -> None:
    print("\n" + "=" * 72)
    print("27. STREAM-LIKE SEARCH")
    print("=" * 72)

    events = (
        Event(1, "LOGIN", "INFO"),
        Event(2, "READ", "LOW"),
        Event(3, "FAILED_LOGIN", "HIGH"),
        Event(4, "DATABASE", "CRITICAL"),
        Event(5, "LOGOUT", "INFO"),
    )

    critical = find_first_critical_event(events)
    print("First critical event:", critical)


# ============================================================================
# 28. SEARCHING WITH NORMALIZED CONDITIONS
# ============================================================================

def first_email_match(
    emails: Sequence[str],
    target_email: str,
) -> Optional[str]:
    """
    Case-insensitive email search.

    The comparison condition is normalized rather than relying on exact
    string equality.
    """
    normalized_target = target_email.strip().casefold()

    for email in emails:
        if email.strip().casefold() == normalized_target:
            return email

    return None


def demonstrate_normalized_search() -> None:
    print("\n" + "=" * 72)
    print("28. NORMALIZED SEARCH")
    print("=" * 72)

    emails = [
        "admin@example.com",
        " Alice@example.com ",
        "support@example.com",
    ]

    print(
        "Search result:",
        first_email_match(emails, "alice@EXAMPLE.com"),
    )


# ============================================================================
# 29. SEARCHING WITH A KEY FUNCTION
# ============================================================================

def find_first_by_key(
    items: Iterable[T],
    target_key,
    key: Callable[[T], object],
) -> Optional[T]:
    """
    Search objects according to a derived key.

    This separates:
        item representation
    from:
        the property used for searching.
    """
    for item in items:
        if key(item) == target_key:
            return item
    return None


def demonstrate_key_search() -> None:
    print("\n" + "=" * 72)
    print("29. KEY-BASED SEARCH")
    print("=" * 72)

    students = [
        Student(301, "Asha", 89),
        Student(302, "Rahul", 92),
        Student(303, "Meera", 86),
    ]

    result = find_first_by_key(
        students,
        "Rahul",
        key=lambda student: student.name.casefold(),
    )

    print("Student found by name:", result)


# ============================================================================
# 30. MULTIPLE MATCHING RECORDS
# ============================================================================

def filter_by_condition(
    items: Iterable[T],
    condition: Callable[[T], bool],
) -> list[T]:
    """Return every item satisfying a predicate."""
    return [item for item in items if condition(item)]


def demonstrate_filtering() -> None:
    print("\n" + "=" * 72)
    print("30. SEARCH VERSUS FILTERING")
    print("=" * 72)

    students = [
        Student(401, "Asha", 72),
        Student(402, "Rahul", 91),
        Student(403, "Meera", 95),
        Student(404, "Vikram", 68),
    ]

    first_high = find_first(students, lambda student: student.score >= 90)
    all_high = filter_by_condition(
        students,
        lambda student: student.score >= 90,
    )

    print("First score >= 90:", first_high)
    print("All scores >= 90:", all_high)

    print(
        """
A first-match search can stop early.
A filtering operation must inspect the complete input if it needs all matches.

Both can use linear traversal, but their output contracts differ.
"""
    )


# ============================================================================
# 31. SECURITY-RELEVANT SEARCH CONSIDERATIONS
# ============================================================================

def demonstrate_security_considerations() -> None:
    print("\n" + "=" * 72)
    print("31. SECURITY CONSIDERATIONS")
    print("=" * 72)

    print(
        """
Linear search itself is not a security boundary.

When searching sensitive records:
    - Validate input before using it in application logic.
    - Normalize values consistently when the domain requires it.
    - Avoid exposing whether sensitive records exist when that information
      should remain private.
    - Avoid logging confidential search terms or records unnecessarily.
    - Be aware that repeated linear scans can become a denial-of-service
      concern when an attacker can trigger very large or numerous searches.
    - Use proper indexing and access control for persistent databases.
    - Do not assume an in-memory search provides authorization.

For password verification and authentication, generic linear search is not a
substitute for a secure password-hashing and verification design.
"""
    )


# ============================================================================
# 32. TESTS
# ============================================================================

def run_tests() -> None:
    """Small built-in test suite using assertions."""
    assert linear_search([], 1) == -1
    assert linear_search([10], 10) == 0
    assert linear_search([10], 20) == -1

    assert first_occurrence([1, 2, 1, 3, 1], 1) == 0
    assert last_occurrence([1, 2, 1, 3, 1], 1) == 4
    assert all_occurrences([1, 2, 1, 3, 1], 1) == [0, 2, 4]

    assert find_first_index([1, 3, 4, 7], lambda x: x % 2 == 0) == 2
    assert find_first_index([1, 3, 7], lambda x: x % 2 == 0) == -1

    assert last_index_where(
        [1, 4, 7, 10, 13],
        lambda x: x % 2 == 0,
    ) == 3

    assert count_occurrences([1, 1, 2, 1], 1) == 3
    assert exists([1, 2, 3], 3)
    assert not exists([1, 2, 3], 4)

    assert linear_search_sorted([1, 4, 7, 9], 7) == 2
    assert linear_search_sorted([1, 4, 7, 9], 6) == -1

    assert last_occurrence_reverse([2, 5, 2, 8], 2) == 2
    assert binary_search([1, 4, 7, 9, 12], 9) == 3
    assert binary_search([1, 4, 7, 9, 12], 10) == -1

    result = search_with_statistics([10, 20, 30], 30)
    assert result == SearchResult(True, 2, 3)

    missing = search_with_statistics([10, 20, 30], 40)
    assert missing == SearchResult(False, None, 3)

    assert first_email_match(
        ["Alice@example.com", "bob@example.com"],
        " alice@EXAMPLE.COM ",
    ) == "Alice@example.com"

    print("\nAll built-in tests passed.")


# ============================================================================
# 33. STUDY EXERCISES AS EXECUTABLE FUNCTIONS
# ============================================================================

def exercise_find_maximum(items: Sequence[float]) -> Optional[float]:
    """
    Find the maximum using one linear scan.

    This demonstrates that linear traversal is not limited to equality search.
    """
    if not items:
        return None

    maximum = items[0]

    for item in items[1:]:
        if item > maximum:
            maximum = item

    return maximum


def exercise_find_minimum(items: Sequence[float]) -> Optional[float]:
    """Find the minimum using one linear scan."""
    if not items:
        return None

    minimum = items[0]

    for item in items[1:]:
        if item < minimum:
            minimum = item

    return minimum


def exercise_first_negative(items: Sequence[int]) -> Optional[int]:
    """Return the first negative value."""
    for item in items:
        if item < 0:
            return item
    return None


def demonstrate_linear_scan_patterns() -> None:
    print("\n" + "=" * 72)
    print("33. OTHER LINEAR SCAN PATTERNS")
    print("=" * 72)

    values = [18, 4, 27, -3, 12, 31]

    print("Data:", values)
    print("Maximum:", exercise_find_maximum(values))
    print("Minimum:", exercise_find_minimum(values))
    print("First negative:", exercise_first_negative(values))


# ============================================================================
# 34. ALGORITHM DESIGN TEMPLATE
# ============================================================================

def linear_search_template(items: Sequence[T], target: T) -> int:
    """
    Canonical iterative template.

    1. Start at the first element.
    2. Compare the current element with the target.
    3. Return immediately if the search condition succeeds.
    4. Move to the next element.
    5. If the scan ends, report absence.
    """
    for index in range(len(items)):
        if items[index] == target:
            return index

    return -1


# ============================================================================
# 35. COMPLEXITY TABLE
# ============================================================================

def print_complexity_table() -> None:
    print("\n" + "=" * 72)
    print("35. COMPLEXITY TABLE")
    print("=" * 72)

    rows = [
        ("First match, best case", "O(1)", "O(1)", "First item matches"),
        ("First match, worst case", "O(n)", "O(1)", "Last item or absent"),
        ("Last occurrence", "O(n)", "O(1)", "Full scan required"),
        ("All occurrences", "O(n)", "O(k)", "k matching indices stored"),
        ("Existence check", "O(1) to O(n)", "O(1)", "Stops at first match"),
        ("Sorted early-exit linear", "O(1) to O(n)", "O(1)", "Still O(n) worst case"),
        ("Binary search", "O(log n)", "O(1)", "Requires suitable sorted data"),
    ]

    print(f"{'Operation':35} {'Time':15} {'Extra Space':15} Condition")
    print("-" * 85)

    for operation, time, space, condition in rows:
        print(f"{operation:35} {time:15} {space:15} {condition}")


# ============================================================================
# 36. MAIN PROGRAM
# ============================================================================

def main() -> None:
    print("=" * 72)
    print("DAY 27 — LINEAR SEARCH")
    print("=" * 72)
    print(
        "Sequential search, search conditions, first occurrence, "
        "last occurrence, and complexity analysis."
    )

    demonstrate_basic_search()
    demonstrate_sequential_process()
    demonstrate_search_conditions()
    demonstrate_first_occurrence()
    demonstrate_last_occurrence()
    demonstrate_all_occurrences()
    demonstrate_predicate_search()
    demonstrate_edge_cases()
    demonstrate_string_search()
    demonstrate_object_search()
    demonstrate_compound_conditions()
    demonstrate_sorted_early_exit()
    demonstrate_reverse_search()
    demonstrate_iterable_search()
    demonstrate_realistic_records()
    demonstrate_search_statistics()
    explain_complexity()
    demonstrate_exact_counts()
    compare_search_requirements()
    demonstrate_duplicate_semantics()
    demonstrate_counting()
    demonstrate_early_exit()
    demonstrate_validation()
    demonstrate_common_mistakes()
    demonstrate_performance()
    demonstrate_use_cases()
    demonstrate_stream_search()
    demonstrate_normalized_search()
    demonstrate_key_search()
    demonstrate_filtering()
    demonstrate_security_considerations()
    demonstrate_linear_scan_patterns()
    print_complexity_table()

    run_tests()


if __name__ == "__main__":
    main()
