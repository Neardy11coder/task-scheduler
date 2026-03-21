from dataclasses import dataclass, field
from typing import Any


@dataclass
class Action:
    """Represents a reversible action."""
    action_type: str        # "ADD", "COMPLETE", "CLEAR"
    task_name: str
    priority: int
    category: str = "General"
    deadline: str = None
    created_at: str = None


class UndoStack:
    """
    Stack-based undo system.
    Uses LIFO (Last In First Out) — most recent action undone first.
    Max size prevents memory bloat on long sessions.
    """

    MAX_SIZE = 20

    def __init__(self):
        self._stack = []        # Python list as stack (append = push, pop = pop)

    def push(self, action: Action):
        """Push a new action onto the stack."""
        if len(self._stack) >= self.MAX_SIZE:
            self._stack.pop(0)      # Remove oldest if at capacity
        self._stack.append(action)

    def pop(self) -> Action:
        """Pop the most recent action (LIFO)."""
        if self._stack:
            return self._stack.pop()
        return None

    def peek(self) -> Action:
        """See the top action without removing it."""
        if self._stack:
            return self._stack[-1]
        return None

    def is_empty(self) -> bool:
        return len(self._stack) == 0

    def size(self) -> int:
        return len(self._stack)

    def get_history(self) -> list:
        """Return all actions newest-first for display."""
        return list(reversed(self._stack))

    def clear(self):
        self._stack = []