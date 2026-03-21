import json
import os
from task import Task

STORAGE_FILE = "tasks.json"


def save_tasks(heap: list):
    tasks_data = []
    for _, counter, task in heap:
        tasks_data.append({
            "name": task.name,
            "priority": task.priority,
            "deadline": task.deadline,
            "created_at": task.created_at,
            "counter": counter,
            "category": task.category
        })
    with open(STORAGE_FILE, "w") as f:
        json.dump(tasks_data, f, indent=2)


def load_tasks() -> list:
    if not os.path.exists(STORAGE_FILE):
        return []

    with open(STORAGE_FILE, "r") as f:
        tasks_data = json.load(f)

    heap = []
    for item in tasks_data:
        task = Task(
            priority=item["priority"],
            name=item["name"],
            deadline=item.get("deadline"),
            created_at=item["created_at"],
            category=item.get("category", "General")
        )
        heap.append((item["priority"], item["counter"], task))

    return heap


def clear_storage():
    if os.path.exists(STORAGE_FILE):
        os.remove(STORAGE_FILE)