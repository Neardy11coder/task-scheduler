from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from scheduler import TaskScheduler
from db_operations import get_completed_tasks, get_task_stats

# ── App setup ─────────────────────────────────────────────
app = FastAPI(
    title="Task Scheduler API",
    description="Priority-Based Task Scheduler powered by Min-Heap DSA",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Shared scheduler instance ─────────────────────────────
scheduler = TaskScheduler()

# ── Request/Response models ───────────────────────────────
class TaskCreate(BaseModel):
    name: str
    priority: int
    category: Optional[str] = "General"
    deadline: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Fix login bug",
                "priority": 1,
                "category": "Work",
                "deadline": "2026-03-30"
            }
        }

class TaskResponse(BaseModel):
    name: str
    priority: int
    category: str
    deadline: Optional[str]
    created_at: str
    priority_label: str

class StatsResponse(BaseModel):
    pending: int
    completed: int
    next_task: Optional[str]

# ── Helper ────────────────────────────────────────────────
PRIORITY_LABELS = {
    1: "Critical", 2: "High", 3: "Medium", 4: "Low", 5: "Minimal"
}

def task_to_response(task) -> TaskResponse:
    return TaskResponse(
        name=task.name,
        priority=task.priority,
        category=task.category or "General",
        deadline=task.deadline,
        created_at=task.created_at,
        priority_label=PRIORITY_LABELS.get(task.priority, "Unknown")
    )

# ── Routes ────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "app": "Priority-Based Task Scheduler",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/tasks", response_model=list[TaskResponse], tags=["Tasks"])
def get_all_tasks():
    """Get all pending tasks sorted by priority."""
    tasks = scheduler.get_all_tasks()
    return [task_to_response(t) for t in tasks]


@app.post("/tasks", response_model=TaskResponse, status_code=201, tags=["Tasks"])
def create_task(task: TaskCreate):
    """Add a new task to the scheduler."""
    if not task.name.strip():
        raise HTTPException(status_code=400, detail="Task name cannot be empty")
    if task.priority not in range(1, 6):
        raise HTTPException(status_code=400, detail="Priority must be between 1 and 5")

    scheduler.add_task(
        name=task.name.strip(),
        priority=task.priority,
        deadline=task.deadline,
        category=task.category
    )

    # Return the newly added top task matching our input
    all_tasks = scheduler.get_all_tasks()
    for t in all_tasks:
        if t.name == task.name.strip() and t.priority == task.priority:
            return task_to_response(t)

    raise HTTPException(status_code=500, detail="Task created but could not be retrieved")


@app.get("/tasks/next", response_model=TaskResponse, tags=["Tasks"])
def get_next_task():
    """Peek at the highest priority task without removing it."""
    top = scheduler.peek_top_task()
    if not top:
        raise HTTPException(status_code=404, detail="No tasks in scheduler")
    return task_to_response(top)


@app.delete("/tasks/complete", response_model=TaskResponse, tags=["Tasks"])
def complete_top_task():
    """Complete (remove) the highest priority task."""
    if scheduler.is_empty():
        raise HTTPException(status_code=404, detail="No tasks to complete")
    removed = scheduler.remove_top_task()
    return task_to_response(removed)


@app.delete("/tasks/undo", tags=["Tasks"])
def undo_last_action():
    """Undo the last add or complete action."""
    if not scheduler.can_undo():
        raise HTTPException(status_code=400, detail="Nothing to undo")
    result = scheduler.undo()
    return {"message": result}


@app.get("/tasks/completed", tags=["Tasks"])
def get_completed():
    """Get all completed tasks history."""
    completed = get_completed_tasks()
    return [
        {
            "name": t["name"],
            "priority": t["priority"],
            "priority_label": PRIORITY_LABELS.get(t["priority"], "Unknown"),
            "category": t["category"],
            "deadline": t["deadline"],
        }
        for t in completed
    ]


@app.get("/stats", response_model=StatsResponse, tags=["Stats"])
def get_stats():
    """Get scheduler statistics."""
    stats = get_task_stats()
    top = scheduler.peek_top_task()
    return StatsResponse(
        pending=stats["pending"],
        completed=stats["completed"],
        next_task=top.name if top else None
    )


@app.delete("/tasks/clear", tags=["Tasks"])
def clear_all():
    """Clear all tasks from the scheduler."""
    scheduler.clear_all()
    return {"message": "All tasks cleared"}