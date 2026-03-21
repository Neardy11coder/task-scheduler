from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass(order=True)
class Task:
    priority: int
    name: str = field(compare=False)
    deadline: Optional[str] = field(default=None, compare=False)
    created_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"),
        compare=False
    )
    category: str = field(default="General", compare=False)

    def __str__(self):
        deadline_str = f" | Deadline: {self.deadline}" if self.deadline else ""
        return f"[Priority {self.priority}] [{self.category}] {self.name}{deadline_str}"