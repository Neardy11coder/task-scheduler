import os
import json
import streamlit as st
from typing import Any, Dict, List
from groq import Groq


def get_secret(key: str) -> str:
    """Read a secret from st.secrets (Streamlit Cloud) or os.getenv (local)."""
    try:
        return st.secrets[key]
    except Exception:
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv(key)


client = Groq(api_key=get_secret("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

_cache = {}


def suggest_priority_and_category(task_name: str) -> Dict[str, Any]:
    """Given a task name, suggest priority (1-5) and category."""

    if task_name in _cache:
        return _cache[task_name]

    prompt = f"""You are a smart task scheduler assistant.
Given this task: "{task_name}"

Respond ONLY with a valid JSON object, no explanation, no markdown, no backticks.
Use exactly this format:
{{"priority": <number 1-5>, "category": "<one of: Work, Study, Personal, Health, Other>", "reason": "<one short sentence explaining why>"}}

Priority guide:
1 = Critical (urgent deadlines, exams tomorrow, emergencies)
2 = High (due soon, important assignments)
3 = Medium (this week, regular tasks)
4 = Low (someday, no deadline)
5 = Minimal (nice to have, not important)"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=150
        )
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        if data["priority"] not in range(1, 6):
            data["priority"] = 3
        if data["category"] not in ["Work", "Study", "Personal", "Health", "Other"]:
            data["category"] = "Other"
        _cache[task_name] = data
        return data
    except Exception as e:
        print(f"Groq suggest error: {e}")
        return {
            "priority": 3,
            "category": "Other",
            "reason": "Could not analyze task — using defaults"
        }


def generate_weekly_plan(goals: str) -> List[str]:
    """Given weekly goals, generate a list of tasks."""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""You are a student productivity assistant.
Today is {today}.

The student's weekly goals:
"{goals}"

Break these goals into specific, actionable tasks for the week.
Respond ONLY with a valid JSON array, no explanation, no markdown, no backticks.
Each task must follow exactly this format:
{{"name": "<specific task name>", "priority": <1-5>, "category": "<Work, Study, Personal, Health, or Other>", "deadline": "<YYYY-MM-DD or null>"}}

Rules:
- Create 5 to 10 tasks maximum
- Be specific (not "study maths" but "solve 10 integration problems")
- Assign deadlines within the next 7 days where relevant
- Priority 1 = most urgent
- Return ONLY the JSON array, nothing else"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=800
        )
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        tasks = json.loads(text)
        valid_tasks = []
        for t in tasks:
            if "name" in t and "priority" in t:
                t["priority"] = max(1, min(5, int(t["priority"])))
                if t.get("category") not in ["Work", "Study", "Personal", "Health", "Other"]:
                    t["category"] = "Other"
                if t.get("deadline") == "null":
                    t["deadline"] = None
                valid_tasks.append(t)
        return valid_tasks[:10]
    except Exception as e:
        print(f"Groq weekly plan error: {e}")
        return []


def generate_exam_tasks(subject: str, exam_date: str, days_left: int) -> List[Dict[str, Any]]:
    """Generate study tasks for an upcoming exam."""
    from datetime import datetime, timedelta

    today = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""You are a student study planner.

Today is {today}. The student has an exam:
- Subject: "{subject}"
- Exam Date: {exam_date} ({days_left} days from now)

Create 3-5 specific study tasks to prepare for this exam.
Respond ONLY with a valid JSON array, no explanation, no markdown, no backticks.
Each task must follow exactly this format:
{{"name": "<specific study task>", "priority": <1-5>, "category": "Study", "deadline": "<YYYY-MM-DD or null>"}}

Rules:
- Be very specific (e.g. "Review Chapter 1-3 of {subject}" not "Study")
- Spread deadlines across the remaining days
- Higher priority for tasks closer to the exam
- If only 1-2 days left, make all tasks priority 1
- Return ONLY the JSON array"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=600
        )
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        tasks = json.loads(text)
        valid = []
        for t in tasks:
            if "name" in t and "priority" in t:
                t["priority"] = max(1, min(5, int(t["priority"])))
                t["category"] = "Study"
                if t.get("deadline") == "null":
                    t["deadline"] = None
                valid.append(t)
        return valid[:5]
    except Exception as e:
        print(f"Groq exam tasks error: {e}")
        return []