import streamlit as st
import plotly.graph_objects as go
from scheduler import TaskScheduler
from visualizer import generate_heap_html
from supabase_db import get_completed_tasks, get_task_stats, get_analytics_data, save_exam, get_exams, delete_exam, get_user_stats, update_user_stats, get_leaderboard_xp, get_leaderboard_streak, get_leaderboard_tasks
from auth_manager import sign_in, sign_up
from gamification import get_avatar, get_level_threshold, get_xp_for_priority, calculate_streak
import streamlit.components.v1 as components
from ai_helper import suggest_priority_and_category, generate_weekly_plan, generate_exam_tasks
from datetime import datetime, date

# ── Page config ───────────────────────────────────────────
# ── Session state & Theme ─────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

_dark = st.session_state.theme == "dark"
T = {
    "bg_base":    "#1e1e2e" if _dark else "#eff1f5",
    "bg_surface": "#181825" if _dark else "#dce0e8",
    "bg_card":    "#1e1e2e" if _dark else "#ffffff",
    "text_main":  "#cdd6f4" if _dark else "#4c4f69",
    "text_muted": "#6c7086" if _dark else "#7c7f93",
    "text_sub":   "#9ca0b0" if _dark else "#9ca0b0",
    "accent":     "#cba6f7" if _dark else "#7287fd",
    "border":     "#313244" if _dark else "#ccd0da",
    "border_light": "#45475a" if _dark else "#bcc0cc",
    "success":    "#a6e3a1" if _dark else "#40a02b",
    "chart_bg":   "#1e1e2e" if _dark else "#ffffff",
}

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="Task Scheduler",
    page_icon="📋",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────
st.markdown(f"""
<style>
    /* ── Dynamic Theme Variables ── */
    :root {{
        --bg-base:      {T['bg_base']};
        --bg-surface:   {T['bg_surface']};
        --bg-card:      {T['bg_card']};
        --text-main:    {T['text_main']};
        --text-muted:   {T['text_muted']};
        --text-sub:     {T['text_sub']};
        --accent:       {T['accent']};
        --border:       {T['border']};
        --border-light: {T['border_light']};
        --success:      {T['success']};
        --chart-bg:     {T['chart_bg']};
    }}
    .task-card {{
        background: var(--bg-card);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        border-left: 5px solid var(--text-main);
    }}
    .priority-1 {{ border-left-color: #f38ba8; }}
    .priority-2 {{ border-left-color: #fab387; }}
    .priority-3 {{ border-left-color: #f9e2af; }}
    .priority-4 {{ border-left-color: #89b4fa; }}
    .priority-5 {{ border-left-color: #a6e3a1; }}
    .task-title {{ font-size: 1.1rem; font-weight: 700; color: var(--text-main); margin: 0; }}
    .task-meta {{ font-size: 0.8rem; color: var(--text-muted); margin-top: 4px; }}
    .badge {{
        display: inline-block; padding: 2px 10px;
        border-radius: 20px; font-size: 0.75rem;
        font-weight: 600; margin-right: 8px;
    }}
    .badge-1 {{ background: #f38ba822; color: #f38ba8; }}
    .badge-2 {{ background: #fab38722; color: #fab387; }}
    .badge-3 {{ background: #f9e2af22; color: #f9e2af; }}
    .badge-4 {{ background: #89b4fa22; color: #89b4fa; }}
    .badge-5 {{ background: #a6e3a122; color: #a6e3a1; }}
    .stat-box {{
        background: var(--bg-card); border-radius: 10px;
        padding: 16px; text-align: center; margin-bottom: 12px;
        border: 1px solid var(--border);
    }}
    .stat-number {{ font-size: 2rem; font-weight: 800; color: var(--accent); }}
    .stat-label {{ font-size: 0.8rem; color: var(--text-muted); }}
    div[data-testid="stSidebar"] {{ background: var(--bg-surface) !important; }}
    div[data-testid="stAppViewContainer"] {{ background: var(--bg-base) !important; }}
    div[data-testid="stHeader"] {{ background: var(--bg-base) !important; }}
    .completed-row {{
        padding: 8px 12px; border-radius: 8px; margin-bottom: 6px;
        background: var(--bg-card); border-left: 3px solid var(--success);
        color: var(--text-muted); font-size: 0.85rem;
    }}
    .auth-box {{
        max-width: 420px; margin: 60px auto;
        background: var(--bg-card); border-radius: 16px;
        padding: 40px; border: 1px solid var(--border);
    }}
    /* Force Streamlit elements to use our text colors */
    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp span, .stApp label, .stApp li {{
        color: var(--text-main) !important;
    }}
    .stMarkdown p {{ color: var(--text-main) !important; }}
    /* Theme transition */
    *, *::before, *::after {{ transition: background-color 0.25s ease, color 0.2s ease, border-color 0.2s ease; }}
</style>
""", unsafe_allow_html=True)

# ── Config helpers ────────────────────────────────────────
CATEGORY_CONFIG = {
    "Work":     {"icon": "💼", "color": "#89b4fa"},
    "Personal": {"icon": "🏠", "color": "#a6e3a1"},
    "Study":    {"icon": "📚", "color": "#f9e2af"},
    "Health":   {"icon": "💪", "color": "#f38ba8"},
    "Other":    {"icon": "🌀", "color": "#cba6f7"},
}

PRIORITY_LABELS = {
    1: ("🔴", "Critical"),
    2: ("🟠", "High"),
    3: ("🟡", "Medium"),
    4: ("🔵", "Low"),
    5: ("⚪", "Minimal")
}

# ── Session state ─────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "completed_count" not in st.session_state:
    st.session_state.completed_count = 0
if "pomodoro_count" not in st.session_state:
    st.session_state.pomodoro_count = 0

# ── Auth screen ───────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown("""
    <div style='text-align:center; padding-top: 40px;'>
        <h1>📋 Task Scheduler</h1>
        <p style='color:#6c7086'>Powered by Min-Heap DSA</p>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

    with tab_login:
        st.write("")
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        st.write("")
        if st.button("Login", use_container_width=True, type="primary"):
            if login_user and login_pass:
                result = sign_in(login_user, login_pass)
                if result["success"]:
                    st.session_state.logged_in  = True
                    st.session_state.username   = result["user"]["username"]
                    st.session_state.user_id    = str(result["user"]["id"])
                    st.session_state.scheduler  = TaskScheduler(
                        user_id=st.session_state.user_id
                    )
                    st.success(f"Welcome back, {login_user}!")
                    st.rerun()
                else:
                    st.error(result["error"])
            else:
                st.warning("Please fill in all fields")

    with tab_signup:
        st.write("")
        new_user  = st.text_input("Username", key="signup_user")
        new_email = st.text_input("Email", key="signup_email")
        new_pass  = st.text_input("Password", type="password", key="signup_pass")
        new_pass2 = st.text_input("Confirm Password", type="password", key="signup_pass2")
        st.write("")
        if st.button("Create Account", use_container_width=True, type="primary"):
            if new_user and new_email and new_pass and new_pass2:
                if new_pass != new_pass2:
                    st.error("Passwords don't match!")
                elif len(new_pass) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    result = sign_up(new_user, new_email, new_pass)
                    if result["success"]:
                        st.success("Account created! Please login.")
                    else:
                        st.error(result["error"])
            else:
                st.warning("Please fill in all fields")

    st.stop()

# ── App (only shown when logged in) ──────────────────────
if "scheduler" not in st.session_state:
    st.session_state.scheduler = TaskScheduler(user_id=st.session_state.user_id)

scheduler = st.session_state.scheduler
user_id   = st.session_state.user_id

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"## 📋 Task Scheduler")
    st.caption(f"Logged in as **{st.session_state.username}**")

    # ── Theme Toggle ──
    _is_dark = st.session_state.theme == "dark"
    _toggle_label = "☀️ Light Mode" if _is_dark else "🌙 Dark Mode"
    if st.button(_toggle_label, use_container_width=True):
        st.session_state.theme = "light" if _is_dark else "dark"
        st.rerun()

    st.divider()

    # ── Gamification Profile ──
    stats_g = get_user_stats(user_id)
    
    # Update daily streak if checked for the first time today
    today_str = date.today().strftime("%Y-%m-%d")
    if stats_g.get("last_active_date") != today_str:
        new_streak = calculate_streak(stats_g.get("current_streak", 0), stats_g.get("last_active_date"))
        stats_g["current_streak"] = new_streak
        stats_g["last_active_date"] = today_str
        if new_streak > stats_g.get("highest_streak", 0):
            stats_g["highest_streak"] = new_streak
        update_user_stats(user_id, stats_g)

    # UI display
    lvl = stats_g.get("level", 1)
    xp = stats_g.get("xp", 0)
    avatar = get_avatar(lvl)
    
    st.markdown(f"### {avatar} Level {lvl}")
    
    thresh = get_level_threshold(lvl)
    prev_thresh = get_level_threshold(lvl - 1) if lvl > 1 else 0
    xp_needed = thresh - prev_thresh
    xp_into_level = xp - prev_thresh
    progress = min(1.0, max(0.0, xp_into_level / xp_needed)) if xp_needed > 0 else 1.0
    
    st.progress(progress, text=f"{xp} / {thresh} XP")
    
    st.markdown(f"**🔥 Daily Streak:** {stats_g.get('current_streak', 0)} days")
    st.caption(f"Best: {stats_g.get('highest_streak', 0)} days")
    st.divider()

    stats = get_task_stats(user_id)
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">{stats['pending']}</div>
        <div class="stat-label">Pending Tasks</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">{stats['completed']}</div>
        <div class="stat-label">Completed Total</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("#### Priority Legend")
    for p, (emoji, label) in PRIORITY_LABELS.items():
        st.markdown(f"{emoji} **{label}** — Level {p}")

    st.divider()

    st.markdown("#### ⚡ Next Up")
    top = scheduler.peek_top_task()
    if top:
        emoji, label = PRIORITY_LABELS[top.priority]
        
        pending_ids = {t[1] for t in scheduler._heap if t[1] is not None}
        is_locked = any(dep_id in pending_ids for dep_id in getattr(top, "dependencies", []))
        lock_icon = " 🔒" if is_locked else ""
        
        st.markdown(f"{emoji} **{top.name}**{lock_icon}")
        st.caption(f"{label} priority")
        if is_locked:
            blocking_names = [t[1] for t in scheduler._heap if t[1] in getattr(top, "dependencies", [])]
            st.error(f"Waiting on: {', '.join(blocking_names)}")
        recur_str = ""
        top_recur = getattr(top, "recurrence", None)
        if top_recur:
            r_type = top_recur.get("type", "")
            if r_type == "daily": recur_str = " | 🔁 Daily"
            elif r_type == "weekly": recur_str = " | 🔁 Weekly"
            elif r_type == "interval": recur_str = f" | 🔁 Every {top_recur.get('days', 2)} days"

        if top.deadline:
            st.caption(f"📅 Due: {top.deadline}{recur_str}")
        elif recur_str:
            st.caption(recur_str.strip(" | "))
    else:
        st.caption("No tasks pending")

    st.divider()

    st.markdown("#### ↩️ Action History")
    history = scheduler.get_undo_history()
    if not history:
        st.caption("No actions yet")
    else:
        for action in history[:5]:
            icon = "➕" if action.action_type == "ADD" else "✅"
            st.caption(f"{icon} {action.action_type}: {action.task_name[:15]}")

    st.divider()

    st.markdown("#### 📅 Calendar Export")
    from calendar_export import generate_ics
    from supabase_db import get_exams
    all_exams = get_exams(user_id)
    ics_data = generate_ics(scheduler.get_all_tasks(), all_exams)
    
    st.download_button(
        label="📤 Download (.ics)",
        data=ics_data,
        file_name="task_scheduler.ics",
        mime="text/calendar",
        use_container_width=True,
        help="Import this file into Google Calendar or Apple Calendar!"
    )

    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ── Theme-aware Python color palette ─────────────────────
_dark = st.session_state.theme == "dark"
T = {
    "bg_base":    "#1e1e2e" if _dark else "#eff1f5",
    "bg_surface": "#181825" if _dark else "#dce0e8",
    "bg_card":    "#1e1e2e" if _dark else "#ffffff",
    "text_main":  "#cdd6f4" if _dark else "#4c4f69",
    "text_muted": "#6c7086" if _dark else "#7c7f93",
    "accent":     "#cba6f7" if _dark else "#7287fd",
    "border":     "#313244" if _dark else "#ccd0da",
    "grid":       "#313244" if _dark else "#e0e4ef",
    "success":    "#a6e3a1" if _dark else "#40a02b",
    "chart_bg":   "#1e1e2e" if _dark else "#ffffff",
}

# ── Main area ─────────────────────────────────────────────
st.title("📋 Priority-Based Task Scheduler")
st.caption("Tasks are automatically sorted by urgency using a Min-Heap")
st.divider()

# ── Active Tasks (Checklists) ─────────────────────────────
st.subheader("🔥 Active Tasks")
pending_tasks = scheduler.get_all_tasks()

if not pending_tasks:
    st.info("No active tasks! Add one below.")
else:
    for task in pending_tasks:
        emoji, label = PRIORITY_LABELS[task.priority]
        cat_icon = CATEGORY_CONFIG.get(task.category, {"icon": "🌀"})["icon"]
        deadline_str = f" | 📅 {task.deadline}" if task.deadline else ""
        
        recur_str = ""
        task_recur = getattr(task, "recurrence", None)
        if task_recur:
            r_type = task_recur.get("type", "")
            if r_type == "daily": recur_str = " | 🔁 Daily"
            elif r_type == "weekly": recur_str = " | 🔁 Weekly"
            elif r_type == "interval": recur_str = f" | 🔁 Every {task_recur.get('days', 2)} days"

        total_sub = len(task.subtasks)
        completed_sub = sum(1 for s in task.subtasks if s.get("completed", False))
        prog_text = f" — {completed_sub}/{total_sub} done" if total_sub > 0 else ""
        
        pending_ids = {t.db_id for t in pending_tasks if t.db_id is not None}
        is_blocked = any(dep_id in pending_ids for dep_id in getattr(task, "dependencies", []))
        lock_icon = "🔒 " if is_blocked else ""

        with st.expander(f"{lock_icon}{emoji} **{task.name}**{prog_text}", expanded=False):
            if is_blocked:
                blocking_names = [t.name for t in pending_tasks if t.db_id in getattr(task, "dependencies", [])]
                st.error(f"Requires: {', '.join(blocking_names)}")

            st.caption(f"{label} Priority | {cat_icon} {task.category}{deadline_str}{recur_str}")
            
            if total_sub > 0:
                for i, sub in enumerate(task.subtasks):
                    sub_key = f"sub_{task.db_id}_{i}"
                    is_checked = st.checkbox(sub["text"], value=sub.get("completed", False), key=sub_key)
                    
                    if is_checked != sub.get("completed", False):
                        task.subtasks[i]["completed"] = is_checked
                        # Use the actual update_task_subtasks to persist
                        from supabase_db import update_task_subtasks
                        update_task_subtasks(task.db_id, task.subtasks)
                        st.rerun()
            else:
                st.caption("No sub-tasks.")

st.divider()

# ── Add Task ──────────────────────────────────────────────
st.subheader("➕ Add New Task")

# ── AI Suggestion toggle ──────────────────────────────────
use_ai = st.toggle("🤖 AI Auto-Suggest Priority & Category", value=True)

col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

with col1:
    task_name = st.text_input("Task Name", placeholder="e.g. Finish DSA assignment")

# AI suggestion on task name
ai_suggestion = None
if use_ai and task_name.strip() and len(task_name.strip()) > 3:
    with st.spinner("🤖 AI analyzing..."):
        ai_suggestion = suggest_priority_and_category(task_name.strip())

with col2:
    default_priority = ai_suggestion["priority"] if ai_suggestion else 3
    priority = st.selectbox(
        "Priority",
        options=[1, 2, 3, 4, 5],
        index=default_priority - 1,
        format_func=lambda x: f"{PRIORITY_LABELS[x][0]} {PRIORITY_LABELS[x][1]}"
    )

with col3:
    default_category = ai_suggestion["category"] if ai_suggestion else "Other"
    cat_options = list(CATEGORY_CONFIG.keys())
    default_cat_idx = cat_options.index(default_category) if default_category in cat_options else 0
    category = st.selectbox(
        "Category",
        options=cat_options,
        index=default_cat_idx,
        format_func=lambda x: f"{CATEGORY_CONFIG[x]['icon']} {x}"
    )

with col4:
    deadline = st.text_input("Deadline (optional)", placeholder="e.g. 2026-03-30")

recur_col, dep_col = st.columns(2)

with recur_col:
    recur_type = st.selectbox("🔁 Recurrence (Optional)", ["Does not repeat", "Daily", "Weekly", "Custom Interval"])
    recur_days = 2
    if recur_type == "Custom Interval":
        recur_days = st.number_input("Repeat every X days", min_value=1, value=3)
        
    recurrence_dict = None
    if recur_type == "Daily": recurrence_dict = {"type": "daily"}
    elif recur_type == "Weekly": recurrence_dict = {"type": "weekly"}
    elif recur_type == "Custom Interval": recurrence_dict = {"type": "interval", "days": recur_days}

with dep_col:
    active_tasks_for_deps = [(t.db_id, t.name) for _, _, t in scheduler._heap if t.db_id is not None]
    dep_options = [t[0] for t in active_tasks_for_deps]
dep_names = {t[0]: t[1] for t in active_tasks_for_deps}

selected_deps = st.multiselect(
    "Depends On (Optional)",
    options=dep_options,
    format_func=lambda x: dep_names[x]
)

subtasks_text = st.text_area("Sub-tasks (Optional)", placeholder="Buy domain\nDesign logo", height=100)
add_btn = st.button("➕ Add Task", use_container_width=True, type="primary")

# Show AI reasoning
if ai_suggestion:
    st.caption(f"🤖 AI suggests: **Priority {ai_suggestion['priority']}** · **{ai_suggestion['category']}** — {ai_suggestion['reason']}")

if add_btn:
    if task_name.strip() == "":
        st.error("⚠️ Task name cannot be empty!")
    else:
        subtasks_list = []
        if subtasks_text.strip():
            for line in subtasks_text.split('\n'):
                if line.strip():
                    subtasks_list.append({"text": line.strip(), "completed": False})
                    
        scheduler.add_task(
            name=task_name.strip(),
            priority=priority,
            deadline=deadline.strip() if deadline.strip() else None,
            category=category,
            subtasks=subtasks_list,
            dependencies=selected_deps,
            recurrence=recurrence_dict
        )
        st.success(f"✅ **'{task_name}'** added as {PRIORITY_LABELS[priority][1]} priority!")
        st.rerun()

st.divider()

# ── AI Weekly Planner ─────────────────────────────────────
with st.expander("🗓️ AI Weekly Planner — Describe your week, AI creates your tasks"):
    st.caption("Tell the AI what you need to accomplish this week and it will create all your tasks automatically")

    weekly_goals = st.text_area(
        "What do you need to accomplish this week?",
        placeholder="""Example:
I have a DSA exam on Friday, need to submit my OS assignment by Wednesday,
want to exercise 3 times, and finish reading chapter 5 of DBMS.""",
        height=120
    )

    generate_btn = st.button("🤖 Generate My Weekly Plan", type="primary", use_container_width=True)

    if generate_btn:
        if not weekly_goals.strip():
            st.warning("Please describe your weekly goals first!")
        else:
            with st.spinner("🤖 AI is planning your week..."):
                tasks = generate_weekly_plan(weekly_goals.strip())

            if not tasks:
                st.error("AI couldn't generate tasks. Try again!")
            else:
                st.session_state.generated_tasks = tasks
                st.session_state.show_generated = True

if st.session_state.get("show_generated") and st.session_state.get("generated_tasks"):
    tasks = st.session_state.generated_tasks
    st.success(f"✅ AI generated {len(tasks)} tasks! Review and confirm:")
    st.write("")

    for task in tasks:
        emoji = ["🔴", "🟠", "🟡", "🔵", "⚪"][task["priority"] - 1]
        cat_icon = CATEGORY_CONFIG.get(task["category"], {"icon": "🌀"})["icon"]
        deadline_str = f" | 📅 {task['deadline']}" if task.get("deadline") else ""
        st.markdown(
            f"{emoji} **{task['name']}** — "
            f"{cat_icon} {task['category']}"
            f"{deadline_str}"
        )

    st.write("")
    col_confirm, col_cancel = st.columns(2)

    with col_confirm:
        if st.button("✅ Add All Tasks", use_container_width=True, type="primary"):
            for task in tasks:
                scheduler.add_task(
                    name=task["name"],
                    priority=task["priority"],
                    category=task["category"],
                    deadline=task.get("deadline")
                )
            st.session_state.generated_tasks = None
            st.session_state.show_generated = False
            # Force scheduler to reload from DB
            st.session_state.scheduler = TaskScheduler(user_id=st.session_state.user_id)
            st.success(f"🎉 Added {len(tasks)} tasks to your schedule!")
            st.rerun()

    with col_cancel:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.generated_tasks = None
            st.session_state.show_generated = False
            st.rerun()

st.divider()

# ── Pomodoro Timer ────────────────────────────────────────
st.subheader("🍅 Pomodoro Timer")
st.caption("Stay focused with timed work sessions. Pick a task and start the clock!")

# Task selector for Pomodoro
pomo_tasks = [(t.name, t.priority) for _, _, t in sorted(scheduler._heap)] if not scheduler.is_empty() else []
pomo_options = [f"{['🔴','🟠','🟡','🔵','⚪'][p-1]} {name}" for name, p in pomo_tasks]
pomo_options_raw = [name for name, _ in pomo_tasks]

col_task_sel, col_pomo_count = st.columns([3, 1])
with col_task_sel:
    selected_idx = st.selectbox(
        "🎯 Working on",
        options=range(len(pomo_options)),
        format_func=lambda i: pomo_options[i] if pomo_options else "No tasks — add one first!",
        disabled=len(pomo_options) == 0,
        label_visibility="collapsed"
    ) if pomo_options else None
    selected_task_name = pomo_options_raw[selected_idx] if (pomo_options and selected_idx is not None) else "No task selected"

with col_pomo_count:
    st.markdown(f"""
    <div class="stat-box" style="margin:0">
        <div class="stat-number" style="font-size:1.6rem">{st.session_state.pomodoro_count}</div>
        <div class="stat-label">🍅 Done today</div>
    </div>
    """, unsafe_allow_html=True)

# The JavaScript timer component
pomo_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: transparent;
    font-family: 'Segoe UI', system-ui, sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 320px;
  }}
  .pomo-wrap {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 18px;
    width: 100%;
    max-width: 480px;
  }}
  .mode-btns {{
    display: flex;
    gap: 8px;
  }}
  .mode-btn {{
    padding: 6px 18px;
    border-radius: 20px;
    border: 1.5px solid #45475a;
    background: transparent;
    color: #6c7086;
    font-size: 0.82rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }}
  .mode-btn.active {{
    border-color: #f38ba8;
    color: #f38ba8;
    background: #f38ba811;
  }}
  .mode-btn:hover:not(.active) {{
    border-color: #585b70;
    color: #cdd6f4;
  }}
  .ring-wrap {{
    position: relative;
    width: 200px;
    height: 200px;
  }}
  svg {{ transform: rotate(-90deg); }}
  .bg-ring {{ fill: none; stroke: #313244; stroke-width: 12; }}
  .prog-ring {{ fill: none; stroke: #f38ba8; stroke-width: 12;
    stroke-linecap: round;
    transition: stroke-dashoffset 1s linear, stroke 0.4s;
  }}
  .timer-label {{
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
  }}
  .timer-time {{
    font-size: 2.6rem;
    font-weight: 800;
    color: #cdd6f4;
    letter-spacing: 2px;
    line-height: 1;
  }}
  .timer-task {{
    font-size: 0.72rem;
    color: #6c7086;
    margin-top: 6px;
    max-width: 130px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }}
  .control-btns {{
    display: flex;
    gap: 12px;
  }}
  .ctrl-btn {{
    padding: 10px 28px;
    border-radius: 30px;
    border: none;
    font-size: 0.9rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
    letter-spacing: 0.5px;
  }}
  .btn-start {{
    background: #a6e3a1;
    color: #1e1e2e;
  }}
  .btn-start:hover {{ background: #94d4a0; transform: scale(1.04); }}
  .btn-pause {{
    background: #f9e2af;
    color: #1e1e2e;
  }}
  .btn-pause:hover {{ background: #e8d19e; transform: scale(1.04); }}
  .btn-reset {{
    background: #313244;
    color: #cdd6f4;
  }}
  .btn-reset:hover {{ background: #45475a; transform: scale(1.04); }}
  .session-done {{
    font-size: 0.8rem;
    color: #a6e3a1;
    opacity: 0;
    transition: opacity 0.5s;
    font-weight: 600;
  }}
  .session-done.show {{ opacity: 1; }}
</style>
</head>
<body>
<div class="pomo-wrap">
  <!-- Mode selector -->
  <div class="mode-btns">
    <button class="mode-btn active" id="btn-work"   onclick="setMode('work')">🍅 Work</button>
    <button class="mode-btn"        id="btn-short"  onclick="setMode('short')">☕ Short Break</button>
    <button class="mode-btn"        id="btn-long"   onclick="setMode('long')">🛋️ Long Break</button>
  </div>

  <!-- Ring -->
  <div class="ring-wrap">
    <svg width="200" height="200" viewBox="0 0 200 200">
      <circle class="bg-ring"   cx="100" cy="100" r="88"/>
      <circle class="prog-ring" cx="100" cy="100" r="88"
              id="progress-ring"
              stroke-dasharray="553"
              stroke-dashoffset="0"/>
    </svg>
    <div class="timer-label">
      <div class="timer-time" id="timer-display">25:00</div>
      <div class="timer-task" id="task-name-label">{selected_task_name}</div>
    </div>
  </div>

  <!-- Controls -->
  <div class="control-btns">
    <button class="ctrl-btn btn-start" id="btn-start-pause" onclick="toggleTimer()">▶ Start</button>
    <button class="ctrl-btn btn-reset" onclick="resetTimer()">↺ Reset</button>
  </div>

  <div class="session-done" id="session-done-msg">✅ Session complete! Great work!</div>
</div>

<script>
  const MODES = {{ work: 25*60, short: 5*60, long: 15*60 }};
  const COLORS = {{ work: '#f38ba8', short: '#a6e3a1', long: '#89b4fa' }};
  const CIRC = 2 * Math.PI * 88; // circumference

  let mode = 'work';
  let totalSecs = MODES[mode];
  let secsLeft  = totalSecs;
  let running   = false;
  let interval  = null;

  const ring    = document.getElementById('progress-ring');
  const display = document.getElementById('timer-display');
  const msgEl   = document.getElementById('session-done-msg');
  const startBtn = document.getElementById('btn-start-pause');

  function setMode(m) {{
    if (running) return;  // don't switch mid-session
    mode = m;
    totalSecs = MODES[m];
    secsLeft  = totalSecs;
    ring.style.stroke = COLORS[m];
    document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('btn-' + m).classList.add('active');
    updateDisplay();
    updateRing();
    msgEl.classList.remove('show');
  }}

  function fmt(s) {{
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return String(m).padStart(2,'0') + ':' + String(sec).padStart(2,'0');
  }}

  function updateDisplay() {{
    display.textContent = fmt(secsLeft);
  }}

  function updateRing() {{
    const pct = secsLeft / totalSecs;
    ring.style.strokeDashoffset = CIRC * (1 - pct);
  }}

  function toggleTimer() {{
    if (running) {{
      clearInterval(interval);
      running = false;
      startBtn.textContent = '▶ Resume';
      startBtn.className = 'ctrl-btn btn-start';
    }} else {{
      running = true;
      startBtn.textContent = '⏸ Pause';
      startBtn.className = 'ctrl-btn btn-pause';
      msgEl.classList.remove('show');
      interval = setInterval(tick, 1000);
    }}
  }}

  function tick() {{
    if (secsLeft <= 0) {{
      clearInterval(interval);
      running = false;
      startBtn.textContent = '▶ Start';
      startBtn.className = 'ctrl-btn btn-start';
      msgEl.classList.add('show');
      // Play a subtle beep if possible
      try {{
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain); gain.connect(ctx.destination);
        osc.frequency.value = 880;
        osc.type = 'sine';
        gain.gain.setValueAtTime(0.4, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.2);
        osc.start(); osc.stop(ctx.currentTime + 1.2);
      }} catch(e) {{}}
      return;
    }}
    secsLeft--;
    updateDisplay();
    updateRing();
  }}

  function resetTimer() {{
    clearInterval(interval);
    running = false;
    secsLeft = totalSecs;
    startBtn.textContent = '▶ Start';
    startBtn.className = 'ctrl-btn btn-start';
    msgEl.classList.remove('show');
    updateDisplay();
    updateRing();
  }}

  // Init
  ring.style.strokeDasharray = CIRC;
  ring.style.stroke = COLORS[mode];
  updateDisplay();
  updateRing();
</script>
</body>
</html>
"""

components.html(pomo_html, height=360, scrolling=False)
st.divider()

# ── Exam Countdown ────────────────────────────────────────
st.subheader("📅 Exam Countdown")
st.caption("Track your upcoming exams with live countdowns and auto-generate study tasks")

# Add Exam form
with st.expander("➕ Add an Exam", expanded=False):
    ex_col1, ex_col2 = st.columns([3, 1])
    with ex_col1:
        exam_subject = st.text_input("Subject", placeholder="e.g. Data Structures", key="exam_subject")
    with ex_col2:
        exam_date_input = st.date_input("Exam Date", min_value=date.today(), key="exam_date")

    if st.button("📅 Add Exam", use_container_width=True, type="primary"):
        if exam_subject.strip():
            save_exam(user_id, exam_subject.strip(), str(exam_date_input))
            st.success(f"✅ Added exam: **{exam_subject}** on {exam_date_input}")
            st.rerun()
        else:
            st.warning("Please enter a subject name!")

# Show existing exams
exams = get_exams(user_id)

if not exams:
    st.info("No exams added yet. Add one above to start the countdown!")
else:
    for exam in exams:
        exam_dt = datetime.strptime(exam["exam_date"], "%Y-%m-%d")
        now = datetime.now()
        delta = exam_dt - now
        days_left = max(0, delta.days)
        hours_left = max(0, int(delta.total_seconds() // 3600) % 24)

        # Urgency color
        if days_left <= 1:
            urgency_color = "#f38ba8"  # red
            urgency_label = "🚨 TOMORROW!" if days_left == 1 else "🔥 TODAY!"
        elif days_left <= 3:
            urgency_color = "#fab387"  # orange
            urgency_label = f"⚠️ {days_left} days left"
        elif days_left <= 7:
            urgency_color = "#f9e2af"  # yellow
            urgency_label = f"📅 {days_left} days left"
        else:
            urgency_color = "#a6e3a1"  # green
            urgency_label = f"✅ {days_left} days left"

        # Exam countdown card with live JS timer
        countdown_html = f"""
        <div style="background:{T['bg_card']}; border-radius:12px; padding:16px 20px;
                    border-left:5px solid {urgency_color}; margin-bottom:12px;
                    display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="font-size:1.15rem; font-weight:700; color:{T['text_main']};">📚 {exam['subject']}</div>
                <div style="font-size:0.8rem; color:{T['text_muted']}; margin-top:4px;">📅 {exam['exam_date']}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:1.4rem; font-weight:800; color:{urgency_color};" id="countdown-{exam['id']}">
                    {days_left}d {hours_left}h
                </div>
                <div style="font-size:0.75rem; color:{urgency_color}; font-weight:600;">{urgency_label}</div>
            </div>
        </div>
        """
        st.markdown(countdown_html, unsafe_allow_html=True)

        # Action buttons for each exam
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button(f"🤖 Generate Study Tasks", key=f"gen_{exam['id']}", use_container_width=True, type="primary"):
                if days_left == 0:
                    st.warning("Exam is today! Focus on reviewing what you know.")
                else:
                    with st.spinner(f"🤖 Generating study plan for {exam['subject']}..."):
                        study_tasks = generate_exam_tasks(
                            exam["subject"], exam["exam_date"], days_left
                        )
                    if study_tasks:
                        for task in study_tasks:
                            scheduler.add_task(
                                name=task["name"],
                                priority=task["priority"],
                                category=task.get("category", "Study"),
                                deadline=task.get("deadline")
                            )
                        st.session_state.scheduler = TaskScheduler(user_id=st.session_state.user_id)
                        st.success(f"📚 Added {len(study_tasks)} study tasks for {exam['subject']}!")
                        st.rerun()
                    else:
                        st.error("Couldn't generate tasks. Try again!")
        with btn_col2:
            if st.button(f"🗑️ Remove", key=f"del_{exam['id']}", use_container_width=True):
                delete_exam(exam["id"])
                st.toast(f"Removed {exam['subject']} exam")
                st.rerun()

st.divider()

# ── Heap Visualizer ───────────────────────────────────────
st.subheader("🌳 Live Heap Structure")
st.caption("Visual representation of the Min-Heap tree — root always has highest priority")

if scheduler.is_empty():
    st.info("Add tasks to see the heap tree!")
else:
    col_viz, col_info = st.columns([3, 1])
    with col_viz:
        heap_html = generate_heap_html(scheduler._heap)
        components.html(heap_html, height=500, scrolling=False)
    with col_info:
        st.markdown("#### How to read this")
        st.markdown("""
        - **Root node** = highest priority task
        - **Node index** = position in heap array
        - **Color** = priority level
        - **Children** always lower priority than parent
        """)
        st.divider()
        st.markdown("#### Heap Array")
        st.caption("Raw heap internal order:")
        for i, (p, _, t) in enumerate(sorted(scheduler._heap)):
            st.caption(f"`[{i}]` P{p} — {t.name[:15]}")

st.divider()

# ── Quick Complete + Undo + Clear ─────────────────────────
col_quick, col_undo, col_clear = st.columns(3)

with col_quick:
    top_task = scheduler.peek_top_task()
    pending_ids = {t[1] for t in scheduler._heap if t[1] is not None}
    is_top_locked = False
    if top_task:
        is_top_locked = any(dep_id in pending_ids for dep_id in getattr(top_task, "dependencies", []))

    if is_top_locked:
        st.button("🔒 Top Task is Locked", use_container_width=True, disabled=True)
        st.caption("Complete its dependencies first!")
    else:
        if st.button("⚡ Complete Top Task", use_container_width=True, type="primary"):
            if scheduler.is_empty():
                st.warning("No tasks to complete!")
            else:
                removed = scheduler.remove_top_task()
                st.session_state.completed_count += 1
                
                # --- Recurrence Logic ---
                recur_rule = getattr(removed, "recurrence", None)
                if recur_rule:
                    from datetime import date, timedelta
                    today = date.today()
                    r_type = recur_rule.get("type")
                    if r_type == "daily":
                        next_date = today + timedelta(days=1)
                    elif r_type == "weekly":
                        next_date = today + timedelta(days=7)
                    elif r_type == "interval":
                        next_date = today + timedelta(days=recur_rule.get("days", 1))
                    else:
                        next_date = today

                    reset_subtasks = [{"text": s["text"], "completed": False} for s in removed.subtasks]
                    
                    scheduler.add_task(
                        name=removed.name,
                        priority=removed.priority,
                        deadline=str(next_date),
                        category=removed.category,
                        subtasks=reset_subtasks,
                        dependencies=getattr(removed, "dependencies", []),
                        recurrence=recur_rule
                    )
                    st.toast(f"🔁 Rescheduled '{removed.name}' for {next_date}!")
            
            # --- Gamification Hook ---
            stats_g = get_user_stats(user_id)
            gained_xp = get_xp_for_priority(removed.priority)
            stats_g["xp"] = stats_g.get("xp", 0) + gained_xp
            
            leveled_up = False
            while stats_g["xp"] >= get_level_threshold(stats_g.get("level", 1)):
                stats_g["level"] = stats_g.get("level", 1) + 1
                leveled_up = True
            
            update_user_stats(user_id, stats_g)
            
            if leveled_up:
                st.balloons()
                st.success(f"🎉 LEVEL UP! You are now Level {stats_g['level']}!")
                
            st.toast(f"✅ Completed: {removed.name} (+{gained_xp} XP)")
            st.rerun()

with col_undo:
    undo_label = f"↩️ Undo: {scheduler.undo_peek()}" if scheduler.can_undo() else "↩️ Nothing to Undo"
    if st.button(undo_label, use_container_width=True, disabled=not scheduler.can_undo()):
        result = scheduler.undo()
        if result:
            st.toast(f"↩️ {result}")
            st.rerun()

with col_clear:
    if st.button("🗑️ Clear All Tasks", use_container_width=True):
        scheduler.clear_all()
        st.session_state.completed_count = 0
        st.toast("All tasks cleared!")
        st.rerun()

st.divider()

# ── Completed Task History ────────────────────────────────
st.subheader("✅ Completed Tasks")
completed_tasks = get_completed_tasks(user_id)

if not completed_tasks:
    st.caption("No completed tasks yet!")
else:
    st.caption(f"{len(completed_tasks)} task(s) completed total")
    st.write("")
    for row in completed_tasks:
        emoji = ["🔴", "🟠", "🟡", "🔵", "⚪"][row["priority"] - 1]
        deadline_str = f" | 📅 {row['deadline']}" if row["deadline"] else ""
        cat = row["category"] if row["category"] else "General"
        cat_icon = CATEGORY_CONFIG.get(cat, {"icon": "🌀"})["icon"]
        st.markdown(f"""
        <div class="completed-row">
            {emoji} <s>{row["name"]}</s> &nbsp;|&nbsp;
            Priority {row["priority"]} &nbsp;|&nbsp;
            {cat_icon} {cat}{deadline_str}
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Analytics Dashboard ───────────────────────────────────
st.subheader("📈 Analytics Dashboard")
st.caption("Productivity insights powered by your task history")

data = get_analytics_data(user_id)

if data["total"] == 0:
    st.info("Add and complete some tasks to see analytics!")
else:
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="stat-box">
            <div class="stat-number">{data['total']}</div>
            <div class="stat-label">Total Tasks</div></div>""",
            unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="stat-box">
            <div class="stat-number">{data['completed']}</div>
            <div class="stat-label">Completed</div></div>""",
            unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="stat-box">
            <div class="stat-number">{data['pending']}</div>
            <div class="stat-label">Pending</div></div>""",
            unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="stat-box">
            <div class="stat-number">{data['completion_rate']}%</div>
            <div class="stat-label">Completion Rate</div></div>""",
            unsafe_allow_html=True)

    st.write("")
    chart1, chart2 = st.columns(2)

    with chart1:
        if data["category_counts"]:
            cats   = list(data["category_counts"].keys())
            counts = list(data["category_counts"].values())
            colors = ["#89b4fa", "#a6e3a1", "#f9e2af", "#f38ba8", "#cba6f7"]
            fig_pie = go.Figure(data=[go.Pie(
                labels=cats, values=counts, hole=0.5,
                marker=dict(colors=colors[:len(cats)]),
                textinfo="label+percent",
                textfont=dict(color=T["text_main"], size=12),
            )])
            fig_pie.update_layout(
                title=dict(text="Tasks by Category", font=dict(color=T["text_main"], size=14)),
                paper_bgcolor=T["chart_bg"], plot_bgcolor=T["chart_bg"],
                font=dict(color=T["text_main"]), showlegend=False,
                margin=dict(t=40, b=20, l=20, r=20), height=300,
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with chart2:
        priority_labels = ["P1 Critical", "P2 High", "P3 Medium", "P4 Low", "P5 Minimal"]
        priority_colors = ["#f38ba8", "#fab387", "#f9e2af", "#89b4fa", "#a6e3a1"]
        priority_values = [data["priority_counts"].get(i, 0) for i in range(1, 6)]
        fig_bar = go.Figure(data=[go.Bar(
            x=priority_labels, y=priority_values,
            marker_color=priority_colors,
            text=priority_values, textposition="outside",
            textfont=dict(color=T["text_main"]),
        )])
        fig_bar.update_layout(
            title=dict(text="Tasks by Priority", font=dict(color=T["text_main"], size=14)),
            paper_bgcolor=T["chart_bg"], plot_bgcolor=T["chart_bg"],
            font=dict(color=T["text_main"]),
            xaxis=dict(tickfont=dict(color=T["text_main"]), gridcolor=T["grid"]),
            yaxis=dict(tickfont=dict(color=T["text_main"]), gridcolor=T["grid"]),
            margin=dict(t=40, b=20, l=20, r=20), height=300,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    if data["daily_counts"]:
        days   = sorted(data["daily_counts"].keys())
        counts = [data["daily_counts"][d] for d in days]
        fig_line = go.Figure(data=[go.Bar(
            x=days, y=counts, marker_color=T["accent"],
            text=counts, textposition="outside",
            textfont=dict(color=T["text_main"]),
        )])
        fig_line.update_layout(
            title=dict(text="Tasks Completed Per Day", font=dict(color=T["text_main"], size=14)),
            paper_bgcolor=T["chart_bg"], plot_bgcolor=T["chart_bg"],
            font=dict(color=T["text_main"]),
            xaxis=dict(tickfont=dict(color=T["text_main"]), gridcolor=T["grid"]),
            yaxis=dict(
                tickfont=dict(color=T["text_main"]), gridcolor=T["grid"],
                title=dict(text="Tasks Completed", font=dict(color=T["text_muted"]))
            ),
            margin=dict(t=40, b=20, l=20, r=20), height=280,
        )
        st.plotly_chart(fig_line, use_container_width=True)

    st.write("")
    score_col, tip_col = st.columns([1, 2])

    with score_col:
        rate = data["completion_rate"]
        if rate >= 80:
            score_color = "#a6e3a1"
            score_label = "Excellent 🔥"
        elif rate >= 50:
            score_color = "#f9e2af"
            score_label = "Good 👍"
        elif rate >= 25:
            score_color = "#fab387"
            score_label = "Improving 📈"
        else:
            score_color = "#f38ba8"
            score_label = "Just Starting 🌱"

        st.markdown(f"""
        <div style="background:{T['bg_card']}; border-radius:12px; padding:20px;
                    text-align:center; border: 2px solid {score_color};">
            <div style="font-size:2.5rem; font-weight:800; color:{score_color}">{rate}%</div>
            <div style="font-size:1rem; color:{score_color}; margin-top:4px;">{score_label}</div>
            <div style="font-size:0.75rem; color:{T['text_muted']}; margin-top:8px;">Completion Rate</div>
        </div>
        """, unsafe_allow_html=True)

    with tip_col:
        st.markdown("#### 💡 Productivity Insights")
        if data["pending"] > 5:
            st.warning(f"⚠️ You have {data['pending']} pending tasks!")
        if data["priority_counts"].get(1, 0) > 3:
            st.error(f"🔴 {data['priority_counts'][1]} Critical tasks — focus here first!")
        if rate >= 80:
            st.success("🔥 Outstanding completion rate!")
        elif rate >= 50:
            st.info("👍 Good progress! Keep completing high priority tasks.")
        else:
            st.info("🌱 Just getting started! Complete your top priority task first.")
        top = scheduler.peek_top_task()
        if top:
            st.markdown(f"**Next recommended task:** {top.name} (Priority {top.priority})")

st.divider()

# ── Leaderboard ───────────────────────────────────────────

st.subheader("🏆 Leaderboard")
st.caption("compete with others — usernames are anonymized for privacy")

lb_mode = st.radio(
    "Rank by:",
    options=["🏅 Top XP", "🔥 Top Streaks", "✅ Most Tasks Completed"],
    horizontal=True,
    label_visibility="collapsed"
)

MEDAL = {0: "🥇", 1: "🥈", 2: "🥉"}

def mask_username(uid: str) -> str:
    if uid == user_id:
        return f"⭐ {uid[:8]} (You)"
    return uid[:3] + "***"

if lb_mode == "🏅 Top XP":
    rows = get_leaderboard_xp(10)
    for i, row in enumerate(rows):
        name = mask_username(row["user_id"])
        medal = MEDAL.get(i, f"#{i+1}")
        avatar = get_avatar(row.get("level", 1))
        score = row.get("xp", 0)
        is_me = row["user_id"] == user_id
        border = T["success"] if is_me else T["border"]
        st.markdown(f"""
        <div style="background:{T['bg_card']}; border-radius:10px; padding:12px 20px;
                    border:2px solid {border}; margin-bottom:8px;
                    display:flex; align-items:center; justify-content:space-between">
            <span style="font-size:1.3rem">{medal}</span>
            <span style="flex:1; margin-left:14px; color:{T['text_main']}; font-weight:600">{avatar} {name}</span>
            <span style="color:#f9e2af; font-weight:800; font-size:1.1rem">{score:,} XP</span>
        </div>
        """, unsafe_allow_html=True)

elif lb_mode == "🔥 Top Streaks":
    rows = get_leaderboard_streak(10)
    for i, row in enumerate(rows):
        name = mask_username(row["user_id"])
        medal = MEDAL.get(i, f"#{i+1}")
        avatar = get_avatar(row.get("level", 1))
        score = row.get("highest_streak", 0)
        is_me = row["user_id"] == user_id
        border = T["success"] if is_me else T["border"]
        st.markdown(f"""
        <div style="background:{T['bg_card']}; border-radius:10px; padding:12px 20px;
                    border:2px solid {border}; margin-bottom:8px;
                    display:flex; align-items:center; justify-content:space-between">
            <span style="font-size:1.3rem">{medal}</span>
            <span style="flex:1; margin-left:14px; color:{T['text_main']}; font-weight:600">{avatar} {name}</span>
            <span style="color:#fab387; font-weight:800; font-size:1.1rem">🔥 {score} days</span>
        </div>
        """, unsafe_allow_html=True)

elif lb_mode == "✅ Most Tasks Completed":
    rows = get_leaderboard_tasks(10)
    for i, row in enumerate(rows):
        name = mask_username(row["user_id"])
        medal = MEDAL.get(i, f"#{i+1}")
        score = row.get("completed_tasks", 0)
        is_me = row["user_id"] == user_id
        border = T["success"] if is_me else T["border"]
        st.markdown(f"""
        <div style="background:{T['bg_card']}; border-radius:10px; padding:12px 20px;
                    border:2px solid {border}; margin-bottom:8px;
                    display:flex; align-items:center; justify-content:space-between">
            <span style="font-size:1.3rem">{medal}</span>
            <span style="flex:1; margin-left:14px; color:{T['text_main']}; font-weight:600">🌀 {name}</span>
            <span style="color:#a6e3a1; font-weight:800; font-size:1.1rem">✅ {score} tasks</span>
        </div>
        """, unsafe_allow_html=True)