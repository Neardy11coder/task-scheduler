import heapq
from task import Task
from db_operations import (
    save_task_to_db,
    load_tasks_from_db,
    mark_task_complete,
    delete_all_tasks,
    restore_task_in_db
)
from undo_stack import UndoStack, Action


class TaskScheduler:
    def __init__(self):
        self._heap = []
        self._counter = 0
        self._undo_stack = UndoStack()
        self._load()

    def _load(self):
        """Load tasks from SQLite into heap."""
        self._heap = load_tasks_from_db()
        heapq.heapify(self._heap)
        if self._heap:
            self._counter = max(c for _, c, _ in self._heap) + 1

    def add_task(self, name: str, priority: int, deadline: str = None, category: str = "General"):
        """Add task to heap + DB + push to undo stack."""
        task = Task(priority=priority, name=name, deadline=deadline, category=category)
        task_id = save_task_to_db(task, self._counter)
        heapq.heappush(self._heap, (priority, task_id, task))
        self._counter += 1

        # Push ADD action to undo stack
        self._undo_stack.push(Action(
            action_type="ADD",
            task_name=name,
            priority=priority,
            category=category,
            deadline=deadline,
            created_at=task.created_at
        ))

    def remove_top_task(self):
        """Remove highest priority task + push to undo stack."""
        if self._heap:
            _, _, task = heapq.heappop(self._heap)
            mark_task_complete(task.name, task.priority)

            # Push COMPLETE action to undo stack
            self._undo_stack.push(Action(
                action_type="COMPLETE",
                task_name=task.name,
                priority=task.priority,
                category=task.category,
                deadline=task.deadline,
                created_at=task.created_at
            ))
            return task
        return None

    def undo(self) -> str:
        """Undo the last action. Returns description of what was undone."""
        if self._undo_stack.is_empty():
            return None

        action = self._undo_stack.pop()

        if action.action_type == "ADD":
            # Undo ADD → remove the task from heap + DB
            self._heap = [
                (p, c, t) for p, c, t in self._heap
                if not (t.name == action.task_name and t.priority == action.priority)
            ]
            heapq.heapify(self._heap)
            mark_task_complete(action.task_name, action.priority)
            return f"Undid ADD — removed '{action.task_name}'"

        elif action.action_type == "COMPLETE":
            # Undo COMPLETE → restore task back to pending
            task = Task(
                priority=action.priority,
                name=action.task_name,
                deadline=action.deadline,
                created_at=action.created_at,
                category=action.category
            )
            task_id = restore_task_in_db(action.task_name, action.priority)
            if task_id:
                heapq.heappush(self._heap, (action.priority, task_id, task))
            return f"Undid COMPLETE — restored '{action.task_name}'"

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

    def can_undo(self) -> bool:
        return not self._undo_stack.is_empty()

    def undo_peek(self) -> str:
        """Show what the next undo will do."""
        action = self._undo_stack.peek()
        if action:
            return f"{action.action_type} '{action.task_name}'"
        return None

    def get_undo_history(self) -> list:
        return self._undo_stack.get_history()

    def clear_all(self):
        self._heap = []
        self._counter = 0
        self._undo_stack.clear()
        delete_all_tasks()