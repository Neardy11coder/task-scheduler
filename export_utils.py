import csv
import io
from supabase_db import supabase, get_analytics_data, get_user_stats

def generate_csv_payload(user_id: str = "default") -> str:
    """Fetches all raw tasks for the user and formats them into a standard CSV string."""
    result = supabase.table("tasks").select("*").eq("user_id", user_id).execute()
    tasks = result.data
    
    if not tasks:
        # Return empty skeleton if no data
        return "ID,Name,Category,Priority,Status,Deadline,Created At,Tags,Recurrence,Subtasks Status\n"
        
    output = io.StringIO()
    writer = csv.writer(output)
    
    headers = ["ID", "Name", "Category", "Priority", "Status", "Deadline", "Created At", "Tags", "Recurrence", "Subtasks Status"]
    writer.writerow(headers)
    
    for t in tasks:
        # Format subtasks
        sub = t.get("subtasks")
        sub_str = "0/0"
        if sub and isinstance(sub, list):
            sub_str = f"{len([s for s in sub if s.get('completed')])}/{len(sub)}"
            
        # Extract metadata correctly handling None types
        tags_str = ",".join(t.get("tags") or [])
        recur_str = (t.get("recurrence") or {}).get("type", "")
        status = "Completed" if t.get("completed") == 1 else "Pending"
        
        writer.writerow([
            t.get("id", ""),
            t.get("name", ""),
            t.get("category", ""),
            t.get("priority", ""),
            status,
            t.get("deadline", ""),
            t.get("created_at", ""),
            tags_str,
            recur_str,
            sub_str
        ])
        
    return output.getvalue()

def generate_markdown_report(user_id: str = "default", active_tasks: list = None) -> str:
    """Computes high level statistics and dynamically generates a rich-text report."""
    if active_tasks is None:
        active_tasks = []
        
    stats = get_analytics_data(user_id)
    user_param = get_user_stats(user_id)
    
    xp = user_param.get("xp", 0)
    level = user_param.get("level", 1)
    
    total = stats.get("total", 0)
    completed = stats.get("completed", 0)
    pending = stats.get("pending", 0)
    rate = stats.get("completion_rate", 0)
    
    lines = [
        f"# Productivity Report",
        f"> Automatically generated locally by your Task Scheduler.",
        f"",
        f"**User Level:** {level}",
        f"**Total XP:** {xp}",
        f"",
        f"### Global Statistics",
        f"- **Total Tasks Tracked:** {total}",
        f"- **Tasks Completed:** {completed}",
        f"- **Tasks Pending:** {pending}",
        f"- **Completion Rate:** {rate}%",
        f"",
        f"## Active Backlog ({len(active_tasks)} remaining)",
    ]
    
    if not active_tasks:
        lines.append("*All caught up! You have no active tasks left in the queue.*")
    else:
        for task in active_tasks:
            dl = f" (Due: {task.deadline})" if task.deadline else ""
            lines.append(f"- [ ] **{task.name}** (Priority {task.priority}){dl}")
            
    return "\n".join(lines)
