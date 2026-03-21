import heapq
from task import Task
from db_operations import (
    save_task_to_db,
    load_tasks_from_db,
    mark_task_complete,
    delete_all_tasks
)


class TaskScheduler:
    def __init__(self):
        self._heap = []
        self._counter = 0
        self._load()

    def _load(self):
        """Load tasks from SQLite into heap."""
        self._heap = load_tasks_from_db()
        heapq.heapify(self._heap)
        if self._heap:
            self._counter = max(c for _, c, _ in self._heap) + 1

    def add_task(self, name: str, priority: int, deadline: str = None, category: str = "General"):
        """Add task to heap AND database."""
        task = Task(priority=priority, name=name, deadline=deadline, category=category)
        task_id = save_task_to_db(task, self._counter)
        heapq.heappush(self._heap, (priority, task_id, task))
        self._counter += 1

    def remove_top_task(self):
        """Remove highest priority task from heap AND mark done in DB."""
        if self._heap:
            _, _, task = heapq.heappop(self._heap)
            mark_task_complete(task.name, task.priority)
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
        delete_all_tasks()