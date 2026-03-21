import heapq
from task import Task
from storage import save_tasks, load_tasks, clear_storage


class TaskScheduler:
    def __init__(self):
        self._heap = []
        self._counter = 0
        self._load()          # Auto-load on startup

    def _load(self):
        """Load saved tasks from disk."""
        self._heap = load_tasks()
        heapq.heapify(self._heap)
        if self._heap:
            self._counter = max(c for _, c, _ in self._heap) + 1

    def _save(self):
        """Save current tasks to disk."""
        save_tasks(self._heap)

    def add_task(self, name: str, priority: int, deadline: str = None, category: str = "General"):
        task = Task(priority=priority, name=name, deadline=deadline, category=category)
        heapq.heappush(self._heap, (priority, self._counter, task))
        self._counter += 1
        self._save()          # Auto-save after every change

    def remove_top_task(self):
        if self._heap:
            _, _, task = heapq.heappop(self._heap)
            self._save()
            return task
        return None

    def peek_top_task(self):
        if self._heap:
            return self._heap[0][2]
        return None

    def get_all_tasks(self):
        sorted_tasks = sorted(self._heap)
        return [task for _, _, task in sorted_tasks]

    def is_empty(self):
        return len(self._heap) == 0

    def task_count(self):
        return len(self._heap)

    def clear_all(self):
        self._heap = []
        self._counter = 0
        clear_storage()