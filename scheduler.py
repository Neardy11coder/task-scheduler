import heapq
from task import Task


class TaskScheduler:
    def __init__(self):
        self._heap = []          # The actual min-heap (list under the hood)
        self._counter = 0        # Tiebreaker when two tasks have same priority

    def add_task(self, name: str, priority: int, deadline: str = None):
        """Add a new task into the heap."""
        task = Task(priority=priority, name=name, deadline=deadline)
        heapq.heappush(self._heap, (priority, self._counter, task))
        self._counter += 1

    def remove_top_task(self):
        """Remove and return the highest priority task (lowest number)."""
        if self._heap:
            _, _, task = heapq.heappop(self._heap)
            return task
        return None

    def peek_top_task(self):
        """See the top task without removing it."""
        if self._heap:
            return self._heap[0][2]
        return None

    def get_all_tasks(self):
        """Return all tasks sorted by priority (non-destructive)."""
        sorted_tasks = sorted(self._heap)
        return [task for _, _, task in sorted_tasks]

    def is_empty(self):
        """Check if scheduler has no tasks."""
        return len(self._heap) == 0

    def task_count(self):
        """Return total number of pending tasks."""
        return len(self._heap)