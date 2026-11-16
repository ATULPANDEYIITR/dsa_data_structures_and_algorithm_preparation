from __future__ import annotations

import heapq
import json
import random
import time
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Sequence


class MergeStrategy(Enum):
    HEAP = "heap"
    PAIRWISE = "pairwise"


@dataclass(frozen=True)
class MergeStatistics:
    input_lists: int
    total_elements: int
    output_elements: int
    comparisons_estimate: int
    elapsed_seconds: float


@dataclass
class MergeResult:
    values: list[int]
    statistics: MergeStatistics


class HeapAlgorithms:
    """Heap sort and multiway merging implementations."""

    @staticmethod
    def _sift_down(
        array: list[int],
        root: int,
        heap_size: int
    ) -> None:
        """Restore the max-heap property iteratively."""
        while True:
            largest = root
            left = 2 * root + 1
            right = 2 * root + 2

            if left < heap_size and array[left] > array[largest]:
                largest = left

            if right < heap_size and array[right] > array[largest]:
                largest = right

            if largest == root:
                break

            array[root], array[largest] = array[largest], array[root]
            root = largest

    @classmethod
    def heap_sort(
        cls,
        values: Iterable[int],
        reverse: bool = False
    ) -> list[int]:
        """
        Sort values using an in-place heap construction and extraction
        algorithm. The original iterable is not modified.
        """
        array = list(values)

        if not all(isinstance(x, int) and not isinstance(x, bool)
                   for x in array):
            raise TypeError("Heap sort accepts integers only.")

        n = len(array)

        if n < 2:
            return array

        # Bottom-up heap construction takes O(n) time.
        for root in range(n // 2 - 1, -1, -1):
            cls._sift_down(array, root, n)

        # Move the maximum element to its final position.
        for end in range(n - 1, 0, -1):
            array[0], array[end] = array[end], array[0]
            cls._sift_down(array, 0, end)

        if reverse:
            array.reverse()

        return array

    @staticmethod
    def validate_sorted_lists(
        sorted_lists: Sequence[Sequence[int]]
    ) -> None:
        """Validate that every input sequence is sorted."""
        for list_index, values in enumerate(sorted_lists):
            for index in range(1, len(values)):
                if values[index - 1] > values[index]:
                    raise ValueError(
                        f"Input list {list_index} is not sorted "
                        f"at index {index}."
                    )

    @staticmethod
    def merge_two_sorted(
        left: Sequence[int],
        right: Sequence[int]
    ) -> list[int]:
        """Merge two sorted sequences in linear time."""
        result: list[int] = []
        i = j = 0

        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

        result.extend(left[i:])
        result.extend(right[j:])

        return result

    @classmethod
    def merge_k_sorted_heap(
        cls,
        sorted_lists: Sequence[Sequence[int]]
    ) -> list[int]:
        """
        Merge K sorted sequences using a min-heap.

        Each heap entry contains:
        (value, source_list_index, element_index).

        Source indices provide deterministic tie-breaking.
        """
        cls.validate_sorted_lists(sorted_lists)

        min_heap: list[tuple[int, int, int]] = []

        total_elements = 0

        for list_index, values in enumerate(sorted_lists):
            total_elements += len(values)

            if values:
                heapq.heappush(
                    min_heap,
                    (values[0], list_index, 0)
                )

        result: list[int] = []

        while min_heap:
            value, list_index, element_index = heapq.heappop(
                min_heap
            )

            result.append(value)

            next_index = element_index + 1
            source = sorted_lists[list_index]

            if next_index < len(source):
                heapq.heappush(
                    min_heap,
                    (
                        source[next_index],
                        list_index,
                        next_index
                    )
                )

        if len(result) != total_elements:
            raise RuntimeError("Multiway merge lost input elements.")

        return result

    @classmethod
    def merge_k_sorted_pairwise(
        cls,
        sorted_lists: Sequence[Sequence[int]]
    ) -> list[int]:
        """
        Merge sequences using a balanced pairwise merge strategy.

        Each round approximately halves the number of active sequences.
        """
        cls.validate_sorted_lists(sorted_lists)

        current = [list(values) for values in sorted_lists]

        if not current:
            return []

        while len(current) > 1:
            next_round: list[list[int]] = []

            for index in range(0, len(current), 2):
                if index + 1 < len(current):
                    merged = cls.merge_two_sorted(
                        current[index],
                        current[index + 1]
                    )
                else:
                    merged = current[index]

                next_round.append(merged)

            current = next_round

        return current[0]

    @classmethod
    def merge(
        cls,
        sorted_lists: Sequence[Sequence[int]],
        strategy: MergeStrategy = MergeStrategy.HEAP
    ) -> MergeResult:
        """Execute a multiway merge and collect performance statistics."""
        cls.validate_sorted_lists(sorted_lists)

        total = sum(len(values) for values in sorted_lists)
        k = len(sorted_lists)

        start = time.perf_counter()

        if strategy == MergeStrategy.HEAP:
            values = cls.merge_k_sorted_heap(sorted_lists)
            comparisons = total * max(1, (k + 1).bit_length())
        elif strategy == MergeStrategy.PAIRWISE:
            values = cls.merge_k_sorted_pairwise(sorted_lists)
            comparisons = total * max(1, k.bit_length())
        else:
            raise ValueError("Unsupported merge strategy.")

        elapsed = time.perf_counter() - start

        statistics = MergeStatistics(
            input_lists=k,
            total_elements=total,
            output_elements=len(values),
            comparisons_estimate=comparisons,
            elapsed_seconds=elapsed
        )

        return MergeResult(values, statistics)

    @classmethod
    def external_merge_sort(
        cls,
        values: Iterable[int],
        chunk_size: int = 1000
    ) -> list[int]:
        """
        Demonstrate external-style sorting.

        Data is divided into bounded chunks, each chunk is sorted,
        and the sorted chunks are merged using a min-heap.
        """
        if chunk_size <= 0:
            raise ValueError("Chunk size must be positive.")

        chunks: list[list[int]] = []
        chunk: list[int] = []

        for value in values:
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError("External sorting accepts integers.")

            chunk.append(value)

            if len(chunk) == chunk_size:
                chunks.append(cls.heap_sort(chunk))
                chunk = []

        if chunk:
            chunks.append(cls.heap_sort(chunk))

        return cls.merge_k_sorted_heap(chunks)

    @staticmethod
    def save_result(
        filename: str,
        result: MergeResult
    ) -> None:
        """Persist results as JSON."""
        payload = {
            "values": result.values,
            "statistics": asdict(result.statistics)
        }

        path = Path(filename)

        # Write to a temporary file before replacing the destination.
        temporary = path.with_suffix(path.suffix + ".tmp")

        try:
            temporary.write_text(
                json.dumps(payload, indent=2),
                encoding="utf-8"
            )
            temporary.replace(path)
        except OSError:
            temporary.unlink(missing_ok=True)
            raise


def demonstrate_heap_sort() -> None:
    print("\nHEAP SORT")

    values = [45, 12, 89, 3, 67, 21, 90, 4, 45]

    print("Original:", values)
    print("Ascending:", HeapAlgorithms.heap_sort(values))
    print("Descending:", HeapAlgorithms.heap_sort(values, reverse=True))

    assert HeapAlgorithms.heap_sort(values) == sorted(values)
    assert HeapAlgorithms.heap_sort(values, True) == sorted(
        values,
        reverse=True
    )

    assert HeapAlgorithms.heap_sort([]) == []
    assert HeapAlgorithms.heap_sort([7]) == []
    assert HeapAlgorithms.heap_sort([5, 5, 5]) == [5, 5, 5]


def demonstrate_multiway_merge() -> MergeResult:
    print("\nMERGE K SORTED LISTS")

    sorted_lists = [
        [1, 4, 7, 10],
        [2, 5, 8, 11],
        [3, 6, 9, 12],
        [0, 13, 15]
    ]

    result = HeapAlgorithms.merge(
        sorted_lists,
        MergeStrategy.HEAP
    )

    print("Input lists:", sorted_lists)
    print("Merged:", result.values)
    print("Statistics:", result.statistics)

    assert result.values == sorted(
        value
        for source in sorted_lists
        for value in source
    )

    return result


def demonstrate_edge_cases() -> None:
    print("\nEDGE CASES")

    examples = [
        [],
        [[]],
        [[], [], []],
        [[1, 1, 1], [1, 1], [1]],
        [[-10, -5], [-8, 0], [2, 3]],
        [[1, 2, 3], []]
    ]

    for example in examples:
        result = HeapAlgorithms.merge_k_sorted_heap(example)
        print(f"{example} -> {result}")

    try:
        HeapAlgorithms.merge_k_sorted_heap([
            [1, 5, 3],
            [2, 4]
        ])
    except ValueError as error:
        print("Validation error:", error)

    try:
        HeapAlgorithms.heap_sort([1, "invalid", 3])
    except TypeError as error:
        print("Type error:", error)


def benchmark() -> None:
    print("\nPERFORMANCE COMPARISON")

    random.seed(42)

    values = [random.randint(-100000, 100000) for _ in range(20000)]

    start = time.perf_counter()
    heap_sorted = HeapAlgorithms.heap_sort(values)
    heap_time = time.perf_counter() - start

    start = time.perf_counter()
    builtin_sorted = sorted(values)
    builtin_time = time.perf_counter() - start

    assert heap_sorted == builtin_sorted

    print(f"Heap sort: {heap_time:.6f} seconds")
    print(f"Python sorted: {builtin_time:.6f} seconds")

    sequences = [
        sorted(values[index:index + 1000])
        for index in range(0, len(values), 1000)
    ]

    heap_result = HeapAlgorithms.merge(
        sequences,
        MergeStrategy.HEAP
    )

    pairwise_result = HeapAlgorithms.merge(
        sequences,
        MergeStrategy.PAIRWISE
    )

    assert heap_result.values == pairwise_result.values

    print("Heap merge:", heap_result.statistics)
    print("Pairwise merge:", pairwise_result.statistics)


def main() -> None:
    demonstrate_heap_sort()

    result = demonstrate_multiway_merge()

    demonstrate_edge_cases()

    external_input = [19, 4, 7, 2, 15, 1, 8, 3, 11, 6]

    external_result = HeapAlgorithms.external_merge_sort(
        external_input,
        chunk_size=3
    )

    print("\nEXTERNAL MERGE SORT")
    print("Original:", external_input)
    print("Sorted:", external_result)

    assert external_result == sorted(external_input)

    # Persistence is demonstrated using a local JSON artifact.
    HeapAlgorithms.save_result(
        "heap_merge_results.json",
        result
    )

    benchmark()

    print("\nAll algorithm checks passed.")


if __name__ == "__main__":
    main()
