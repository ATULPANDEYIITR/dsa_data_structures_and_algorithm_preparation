from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
import heapq
from typing import Iterable


class DependencyError(Exception):
    """Base exception for dependency graph errors."""


class CycleError(DependencyError):
    """Raised when a directed cycle prevents topological ordering."""

    def __init__(self, cycle: list[str]):
        self.cycle = cycle
        super().__init__("Dependency cycle detected: " + " -> ".join(cycle))


class TaskStatus(Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class Task:
    task_id: str
    description: str
    duration: int = 1
    status: TaskStatus = TaskStatus.PENDING

    def __post_init__(self):
        if not self.task_id.strip():
            raise ValueError("Task ID cannot be empty.")
        if not self.description.strip():
            raise ValueError("Task description cannot be empty.")
        if self.duration <= 0:
            raise ValueError("Task duration must be positive.")


class DependencyGraph:
    """
    Directed acyclic graph.

    An edge A -> B means B depends on A.
    """

    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self.adjacency: dict[str, set[str]] = defaultdict(set)
        self.reverse: dict[str, set[str]] = defaultdict(set)

    def add_task(self, task: Task) -> None:
        if task.task_id in self.tasks:
            raise DependencyError(f"Duplicate task: {task.task_id}")

        self.tasks[task.task_id] = task
        self.adjacency[task.task_id]
        self.reverse[task.task_id]

    def add_dependency(self, prerequisite: str, dependent: str) -> None:
        if prerequisite not in self.tasks:
            raise DependencyError(f"Unknown prerequisite: {prerequisite}")

        if dependent not in self.tasks:
            raise DependencyError(f"Unknown dependent: {dependent}")

        if prerequisite == dependent:
            raise CycleError([prerequisite, prerequisite])

        if dependent in self.adjacency[prerequisite]:
            return

        self.adjacency[prerequisite].add(dependent)
        self.reverse[dependent].add(prerequisite)

        # Reject an edge that introduces a cycle.
        try:
            self.find_cycle()
        except CycleError:
            self.adjacency[prerequisite].remove(dependent)
            self.reverse[dependent].remove(prerequisite)
            raise

    def find_cycle(self) -> list[str] | None:
        """DFS using white, gray, and black node states."""

        WHITE, GRAY, BLACK = 0, 1, 2
        colors = {node: WHITE for node in self.tasks}
        parent: dict[str, str | None] = {
            node: None for node in self.tasks
        }

        def visit(node: str) -> list[str] | None:
            colors[node] = GRAY

            for neighbor in sorted(self.adjacency[node]):
                if colors[neighbor] == WHITE:
                    parent[neighbor] = node
                    cycle = visit(neighbor)

                    if cycle:
                        return cycle

                elif colors[neighbor] == GRAY:
                    path = [node]

                    while path[-1] != neighbor:
                        previous = parent[path[-1]]
                        if previous is None:
                            break
                        path.append(previous)

                    path.reverse()
                    path.append(neighbor)
                    return path

            colors[node] = BLACK
            return None

        for node in sorted(self.tasks):
            if colors[node] == WHITE:
                cycle = visit(node)

                if cycle:
                    return cycle

        return None

    def topological_sort_dfs(self) -> list[str]:
        """
        DFS-based topological sorting.

        A node is appended after all its dependents have been visited.
        Reversing postorder produces a valid dependency order.
        """

        WHITE, GRAY, BLACK = 0, 1, 2
        colors = {node: WHITE for node in self.tasks}
        result: list[str] = []
        path: list[str] = []

        def visit(node: str) -> None:
            colors[node] = GRAY
            path.append(node)

            for neighbor in sorted(self.adjacency[node]):
                if colors[neighbor] == GRAY:
                    start = path.index(neighbor)
                    raise CycleError(path[start:] + [neighbor])

                if colors[neighbor] == WHITE:
                    visit(neighbor)

            path.pop()
            colors[node] = BLACK
            result.append(node)

        for node in sorted(self.tasks):
            if colors[node] == WHITE:
                visit(node)

        result.reverse()
        return result

    def topological_sort_kahn(self) -> list[str]:
        """
        Kahn's algorithm using indegree counts and a min-heap.

        The heap makes the output deterministic when multiple
        tasks are simultaneously available.
        """

        indegree = {
            node: len(self.reverse[node])
            for node in self.tasks
        }

        ready = [
            node
            for node, degree in indegree.items()
            if degree == 0
        ]

        heapq.heapify(ready)
        result: list[str] = []

        while ready:
            current = heapq.heappop(ready)
            result.append(current)

            for neighbor in sorted(self.adjacency[current]):
                indegree[neighbor] -= 1

                if indegree[neighbor] == 0:
                    heapq.heappush(ready, neighbor)

        if len(result) != len(self.tasks):
            cycle = self.find_cycle()
            raise CycleError(cycle or ["Unknown cycle"])

        return result

    def calculate_levels(self) -> dict[str, int]:
        """
        Calculate the earliest dependency level of each task.

        Level zero contains tasks without prerequisites.
        """

        order = self.topological_sort_kahn()
        levels = {node: 0 for node in self.tasks}

        for node in order:
            for neighbor in self.adjacency[node]:
                levels[neighbor] = max(
                    levels[neighbor],
                    levels[node] + 1
                )

        return levels

    def calculate_critical_path(self) -> tuple[int, list[str]]:
        """
        Calculate the longest weighted dependency path.

        Task duration is included in the total project duration.
        """

        order = self.topological_sort_kahn()
        earliest_finish: dict[str, int] = {}
        previous: dict[str, str | None] = {}

        for node in order:
            start = 0
            predecessor = None

            for parent in sorted(self.reverse[node]):
                candidate = earliest_finish[parent]

                if candidate > start:
                    start = candidate
                    predecessor = parent

            earliest_finish[node] = (
                start + self.tasks[node].duration
            )
            previous[node] = predecessor

        if not order:
            return 0, []

        endpoint = max(
            order,
            key=lambda node: earliest_finish[node]
        )

        path = []
        current: str | None = endpoint

        while current is not None:
            path.append(current)
            current = previous[current]

        path.reverse()

        return earliest_finish[endpoint], path

    def get_execution_schedule(self) -> dict[int, list[str]]:
        """Group tasks that can execute in parallel."""

        levels = self.calculate_levels()
        schedule: dict[int, list[str]] = defaultdict(list)

        for node, level in levels.items():
            schedule[level].append(node)

        return {
            level: sorted(nodes)
            for level, nodes in sorted(schedule.items())
        }

    def validate_order(self, order: Iterable[str]) -> bool:
        """Verify that every prerequisite precedes its dependent."""

        order = list(order)

        if len(order) != len(self.tasks):
            return False

        if len(set(order)) != len(order):
            return False

        if set(order) != set(self.tasks):
            return False

        positions = {
            node: index
            for index, node in enumerate(order)
        }

        return all(
            positions[parent] < positions[child]
            for parent in self.tasks
            for child in self.adjacency[parent]
        )

    def display_schedule(self) -> None:
        schedule = self.get_execution_schedule()

        print("\nPARALLEL EXECUTION SCHEDULE")

        for level, nodes in schedule.items():
            print(f"Stage {level}: {' | '.join(nodes)}")

            for node in nodes:
                task = self.tasks[node]
                print(
                    f"  {node}: {task.description} "
                    f"(duration={task.duration})"
                )


def build_project() -> DependencyGraph:
    graph = DependencyGraph()

    tasks = [
        Task("T1", "Gather requirements", 2),
        Task("T2", "Design architecture", 3),
        Task("T3", "Design database", 2),
        Task("T4", "Implement backend", 5),
        Task("T5", "Implement frontend", 4),
        Task("T6", "Integrate application", 2),
        Task("T7", "Execute testing", 3),
        Task("T8", "Security assessment", 2),
        Task("T9", "Production deployment", 1),
    ]

    for task in tasks:
        graph.add_task(task)

    dependencies = [
        ("T1", "T2"),
        ("T1", "T3"),
        ("T2", "T4"),
        ("T3", "T4"),
        ("T2", "T5"),
        ("T4", "T6"),
        ("T5", "T6"),
        ("T6", "T7"),
        ("T6", "T8"),
        ("T7", "T9"),
        ("T8", "T9"),
    ]

    for prerequisite, dependent in dependencies:
        graph.add_dependency(prerequisite, dependent)

    return graph


def demonstrate_cycle_detection() -> None:
    graph = DependencyGraph()

    for name in ("A", "B", "C"):
        graph.add_task(Task(name, f"Task {name}"))

    graph.add_dependency("A", "B")
    graph.add_dependency("B", "C")

    try:
        graph.add_dependency("C", "A")
    except CycleError as error:
        print("\nCYCLE DETECTION")
        print(error)

    print("Existing graph remains valid:")
    print(graph.topological_sort_kahn())


def run_tests(graph: DependencyGraph) -> None:
    dfs_order = graph.topological_sort_dfs()
    kahn_order = graph.topological_sort_kahn()

    assert graph.validate_order(dfs_order)
    assert graph.validate_order(kahn_order)

    assert set(dfs_order) == set(kahn_order)

    assert graph.calculate_levels()["T1"] == 0
    assert graph.calculate_levels()["T9"] == 4

    empty = DependencyGraph()
    assert empty.topological_sort_kahn() == []
    assert empty.topological_sort_dfs() == []

    print("\nVALIDATION")
    print("DFS ordering: PASS")
    print("Kahn ordering: PASS")
    print("Dependency constraints: PASS")
    print("Parallel execution levels: PASS")
    print("Empty graph: PASS")


def main() -> None:
    graph = build_project()

    print("TOPOLOGICAL SORTING AND DEPENDENCY SCHEDULING")
    print("=" * 52)

    print("\nDFS-BASED TOPOLOGICAL ORDER")
    print(" -> ".join(graph.topological_sort_dfs()))

    print("\nKAHN'S ALGORITHM")
    print(" -> ".join(graph.topological_sort_kahn()))

    graph.display_schedule()

    duration, critical_path = graph.calculate_critical_path()

    print("\nCRITICAL PATH")
    print(" -> ".join(critical_path))
    print(f"Minimum project duration: {duration} time units")

    run_tests(graph)
    demonstrate_cycle_detection()


if __name__ == "__main__":
    main()
