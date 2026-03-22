import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ── Task operations ───────────────────────────────────────

def save_task_to_db(task, counter: int, user_id: str = "default") -> int:
    """Insert a new task into Supabase."""
    data = {
        "user_id":    user_id,
        "name":       task.name,
        "priority":   task.priority,
        "category":   task.category,
        "deadline":   task.deadline,
        "created_at": task.created_at,
        "completed":  0
    }
    result = supabase.table("tasks").insert(data).execute()
    return result.data[0]["id"]


def load_tasks_from_db(user_id: str = "default") -> list:
    """Load all pending tasks for a user as heap-ready tuples."""
    from task import Task
    result = supabase.table("tasks").select("*").eq(
        "user_id", user_id
    ).eq("completed", 0).execute()

    heap = []
    for row in result.data:
        task = Task(
            priority=row["priority"],
            name=row["name"],
            deadline=row.get("deadline"),
            created_at=row["created_at"],
            category=row.get("category", "General")
        )
        heap.append((row["priority"], row["id"], task))
    return heap


def mark_task_complete(task_name: str, priority: int, user_id: str = "default"):
    """Mark a task as completed in Supabase."""
    supabase.table("tasks").update(
        {"completed": 1}
    ).eq("name", task_name).eq(
        "priority", priority
    ).eq("user_id", user_id).eq("completed", 0).execute()


def restore_task_in_db(task_name: str, priority: int, user_id: str = "default") -> int:
    """Restore a completed task back to pending."""
    result = supabase.table("tasks").update(
        {"completed": 0}
    ).eq("name", task_name).eq(
        "priority", priority
    ).eq("user_id", user_id).eq("completed", 1).execute()

    if result.data:
        return result.data[0]["id"]
    return None


def get_completed_tasks(user_id: str = "default") -> list:
    """Fetch all completed tasks for history view."""
    result = supabase.table("tasks").select("*").eq(
        "user_id", user_id
    ).eq("completed", 1).order("id", desc=True).limit(10).execute()

    return [
        {
            "id":         row["id"],
            "name":       row["name"],
            "priority":   row["priority"],
            "category":   row.get("category", "General"),
            "deadline":   row.get("deadline"),
            "created_at": row["created_at"]
        }
        for row in result.data
    ]


def delete_all_tasks(user_id: str = "default"):
    """Delete all tasks for a user."""
    supabase.table("tasks").delete().eq("user_id", user_id).execute()


def get_task_stats(user_id: str = "default") -> dict:
    """Get pending and completed counts."""
    pending = supabase.table("tasks").select(
        "id", count="exact"
    ).eq("user_id", user_id).eq("completed", 0).execute()

    completed = supabase.table("tasks").select(
        "id", count="exact"
    ).eq("user_id", user_id).eq("completed", 1).execute()

    return {
        "pending":   pending.count or 0,
        "completed": completed.count or 0
    }


def get_analytics_data(user_id: str = "default") -> dict:
    """Fetch all data needed for analytics dashboard."""
    result = supabase.table("tasks").select("*").eq(
        "user_id", user_id
    ).execute()

    all_tasks       = result.data
    completed_tasks = [t for t in all_tasks if t["completed"] == 1]
    pending_tasks   = [t for t in all_tasks if t["completed"] == 0]

    category_counts = {}
    for t in all_tasks:
        cat = t.get("category") or "General"
        category_counts[cat] = category_counts.get(cat, 0) + 1

    priority_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for t in all_tasks:
        p = t.get("priority")
        if p in priority_counts:
            priority_counts[p] += 1

    daily_counts = {}
    for t in completed_tasks:
        if t.get("created_at"):
            day = t["created_at"][:10]
            daily_counts[day] = daily_counts.get(day, 0) + 1

    total           = len(all_tasks)
    completed_count = len(completed_tasks)
    rate = round((completed_count / total * 100), 1) if total > 0 else 0

    return {
        "total":           total,
        "completed":       completed_count,
        "pending":         len(pending_tasks),
        "completion_rate": rate,
        "category_counts": category_counts,
        "priority_counts": priority_counts,
        "daily_counts":    daily_counts,
    }


# ── Exam operations ──────────────────────────────────────

def save_exam(user_id: str, subject: str, exam_date: str) -> int:
    """Insert a new exam into Supabase."""
    data = {
        "user_id":    user_id,
        "subject":    subject,
        "exam_date":  exam_date,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    result = supabase.table("exams").insert(data).execute()
    return result.data[0]["id"]


def get_exams(user_id: str) -> list:
    """Fetch all exams for a user."""
    result = supabase.table("exams").select("*").eq(
        "user_id", user_id
    ).order("exam_date").execute()
    return result.data


def delete_exam(exam_id: int):
    """Delete an exam by ID."""
    supabase.table("exams").delete().eq("id", exam_id).execute()