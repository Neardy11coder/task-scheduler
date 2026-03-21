import heapq
from task import Task
from supabase_db import (
    save_task_to_db,
    load_tasks_from_db,
    mark_task_complete,
    delete_all_tasks,
    restore_task_in_db
)
from undo_stack import UndoStack, Action


class TaskScheduler:
    def __init__(self, user_id: str = "default"):
        self._heap = []
        self._counter = 0
        self._undo_stack = UndoStack()
        self._user_id = user_id
        self._load()

    def _load(self):
        self._heap = load_tasks_from_db(self._user_id)
        heapq.heapify(self._heap)
        if self._heap:
            self._counter = max(c for _, c, _ in self._heap) + 1

    def add_task(self, name: str, priority: int, deadline: str = None, category: str = "General"):
        task = Task(priority=priority, name=name, deadline=deadline, category=category)
        task_id = save_task_to_db(task, self._counter, self._user_id)
        heapq.heappush(self._heap, (priority, task_id, task))
        self._counter += 1
        self._undo_stack.push(Action(
            action_type="ADD",
            task_name=name,
            priority=priority,
            category=category,
            deadline=deadline,
            created_at=task.created_at
        ))

    def remove_top_task(self):
        if self._heap:
            _, _, task = heapq.heappop(self._heap)
            mark_task_complete(task.name, task.priority, self._user_id)
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
        if self._undo_stack.is_empty():
            return None

        action = self._undo_stack.pop()

        if action.action_type == "ADD":
            self._heap = [
                (p, c, t) for p, c, t in self._heap
                if not (t.name == action.task_name and t.priority == action.priority)
            ]
            heapq.heapify(self._heap)
            mark_task_complete(action.task_name, action.priority, self._user_id)
            return f"Undid ADD — removed '{action.task_name}'"

        elif action.action_type == "COMPLETE":
            task = Task(
                priority=action.priority,
                name=action.task_name,
                deadline=action.deadline,
                created_at=action.created_at,
                category=action.category
            )
            task_id = restore_task_in_db(
                action.task_name, action.priority, self._user_id
            )
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

    def can_undo(self):
        return not self._undo_stack.is_empty()

    def undo_peek(self):
        action = self._undo_stack.peek()
        if action:
            return f"{action.action_type} '{action.task_name}'"
        return None

    def get_undo_history(self):
        return self._undo_stack.get_history()

    def clear_all(self):
        self._heap = []
        self._counter = 0
        self._undo_stack.clear()
        delete_all_tasks(self._user_id)