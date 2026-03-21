from database import get_db, TaskModel, init_db
from task import Task
from datetime import datetime

init_db()


def save_task_to_db(task: Task, counter: int):
    """Insert a new task into the database."""
    db = get_db()
    db_task = TaskModel(
        name=task.name,
        priority=task.priority,
        category=task.category,
        deadline=task.deadline,
        created_at=task.created_at,
        completed=0
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    db.close()
    return db_task.id


def load_tasks_from_db() -> list:
    """Load all pending tasks from database as heap-ready tuples."""
    db = get_db()
    rows = db.query(TaskModel).filter(TaskModel.completed == 0).all()
    db.close()

    heap = []
    for i, row in enumerate(rows):
        task = Task(
            priority=row.priority,
            name=row.name,
            deadline=row.deadline,
            created_at=row.created_at,
            category=row.category or "General"
        )
        heap.append((row.priority, row.id, task))
    return heap


def mark_task_complete(task_name: str, priority: int):
    """Mark a task as completed in the database."""
    db = get_db()
    db_task = db.query(TaskModel).filter(
        TaskModel.name == task_name,
        TaskModel.priority == priority,
        TaskModel.completed == 0
    ).first()
    if db_task:
        db_task.completed = 1
        db.commit()
    db.close()


def get_completed_tasks() -> list:
    """Fetch all completed tasks for history view."""
    db = get_db()
    try:
        rows = db.query(TaskModel).filter(
            TaskModel.completed == 1
        ).order_by(TaskModel.id.desc()).all()
        result = []
        for row in rows:
            result.append({
                "id": row.id,
                "name": row.name,
                "priority": row.priority,
                "category": row.category,
                "deadline": row.deadline,
                "created_at": row.created_at
            })
        return result
    finally:
        db.close()


def delete_all_tasks():
    """Hard delete all tasks from database."""
    db = get_db()
    db.query(TaskModel).delete()
    db.commit()
    db.close()


def restore_task_in_db(task_name: str, priority: int) -> int:
    """Restore a completed task back to pending (undo complete)."""
    db = get_db()
    db_task = db.query(TaskModel).filter(
        TaskModel.name == task_name,
        TaskModel.priority == priority,
        TaskModel.completed == 1
    ).order_by(TaskModel.id.desc()).first()

    if db_task:
        db_task.completed = 0
        db.commit()
        task_id = db_task.id
        db.close()
        return task_id

    db.close()
    return None


def get_task_stats() -> dict:
    """Get basic stats for sidebar display."""
    db = get_db()
    total_pending   = db.query(TaskModel).filter(TaskModel.completed == 0).count()
    total_completed = db.query(TaskModel).filter(TaskModel.completed == 1).count()
    db.close()
    return {
        "pending": total_pending,
        "completed": total_completed
    }