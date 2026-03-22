from datetime import datetime

def generate_ics(tasks, exams) -> str:
    """
    Generate an iCalendar (.ics) format string containing pending tasks with deadlines
    and all upcoming exams.
    """
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Task Scheduler//EN",
        "CALSCALE:GREGORIAN"
    ]
    
    now_stamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    
    # Process Exams (All-day events on exam_date)
    for exam in exams:
        if not exam.get("exam_date"):
            continue
        try:
            dt = datetime.strptime(exam["exam_date"], "%Y-%m-%d")
            dt_str = dt.strftime("%Y%m%d")
            
            lines.append("BEGIN:VEVENT")
            lines.append(f"UID:exam_{exam['id']}@taskscheduler.app")
            lines.append(f"DTSTAMP:{now_stamp}")
            lines.append(f"DTSTART;VALUE=DATE:{dt_str}")
            lines.append(f"SUMMARY:📚 EXAM: {exam['subject']}")
            lines.append(f"DESCRIPTION:Upcoming exam for {exam['subject']}")
            lines.append("END:VEVENT")
        except Exception:
            pass
            
    # Process Tasks (All-day events on deadline)
    for task in tasks:
        if not getattr(task, "deadline", None):
            continue
            
        try:
            dt = datetime.strptime(task.deadline, "%Y-%m-%d")
            dt_str = dt.strftime("%Y%m%d")
            
            priority_label = ["Critical", "High", "Medium", "Low", "Minimal"][task.priority - 1]
            
            lines.append("BEGIN:VEVENT")
            lines.append(f"UID:task_{getattr(task, 'db_id', '0')}@taskscheduler.app")
            lines.append(f"DTSTAMP:{now_stamp}")
            lines.append(f"DTSTART;VALUE=DATE:{dt_str}")
            lines.append(f"SUMMARY:📋 TASK: {task.name}")
            
            desc = f"Category: {task.category}\\nPriority: {priority_label}"
            
            # Include subtasks in the calendar description if any exist
            if getattr(task, "subtasks", None):
                desc += "\\n\\nChecklist:\\n"
                for sub in task.subtasks:
                    mark = "[x]" if sub.get("completed") else "[ ]"
                    desc += f"{mark} {sub['text']}\\n"
                    
            lines.append(f"DESCRIPTION:{desc}")
            lines.append("END:VEVENT")
        except Exception:
            pass

    lines.append("END:VCALENDAR")
    return "\\r\\n".join(lines)
