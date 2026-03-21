import streamlit as st
import plotly.graph_objects as go
from scheduler import TaskScheduler
from visualizer import generate_heap_html
from supabase_db import get_completed_tasks, get_task_stats, get_analytics_data
from auth_manager import sign_in, sign_up
import streamlit.components.v1 as components

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="Task Scheduler",
    page_icon="📋",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
    .task-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        border-left: 5px solid #cdd6f4;
    }
    .priority-1 { border-left-color: #f38ba8; }
    .priority-2 { border-left-color: #fab387; }
    .priority-3 { border-left-color: #f9e2af; }
    .priority-4 { border-left-color: #89b4fa; }
    .priority-5 { border-left-color: #a6e3a1; }
    .task-title { font-size: 1.1rem; font-weight: 700; color: #cdd6f4; margin: 0; }
    .task-meta { font-size: 0.8rem; color: #6c7086; margin-top: 4px; }
    .badge {
        display: inline-block; padding: 2px 10px;
        border-radius: 20px; font-size: 0.75rem;
        font-weight: 600; margin-right: 8px;
    }
    .badge-1 { background: #f38ba822; color: #f38ba8; }
    .badge-2 { background: #fab38722; color: #fab387; }
    .badge-3 { background: #f9e2af22; color: #f9e2af; }
    .badge-4 { background: #89b4fa22; color: #89b4fa; }
    .badge-5 { background: #a6e3a122; color: #a6e3a1; }
    .stat-box {
        background: #1e1e2e; border-radius: 10px;
        padding: 16px; text-align: center; margin-bottom: 12px;
    }
    .stat-number { font-size: 2rem; font-weight: 800; color: #cba6f7; }
    .stat-label { font-size: 0.8rem; color: #6c7086; }
    div[data-testid="stSidebar"] { background: #181825; }
    .completed-row {
        padding: 8px 12px; border-radius: 8px; margin-bottom: 6px;
        background: #1e1e2e; border-left: 3px solid #a6e3a1;
        color: #6c7086; font-size: 0.85rem;
    }
    .auth-box {
        max-width: 420px; margin: 60px auto;
        background: #1e1e2e; border-radius: 16px;
        padding: 40px; border: 1px solid #313244;
    }
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
    st.session_state.scheduler = TaskScheduler(
        user_id=st.session_state.user_id
    )

scheduler = st.session_state.scheduler
user_id   = st.session_state.user_id

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"## 📋 Task Scheduler")
    st.caption(f"Logged in as **{st.session_state.username}**")
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
        st.markdown(f"{emoji} **{top.name}**")
        st.caption(f"{label} priority")
        if top.deadline:
            st.caption(f"📅 Due: {top.deadline}")
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

    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ── Main area ─────────────────────────────────────────────
st.title("📋 Priority-Based Task Scheduler")
st.caption("Tasks are automatically sorted by urgency using a Min-Heap")
st.divider()

# ── Add Task ──────────────────────────────────────────────
st.subheader("➕ Add New Task")

col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

with col1:
    task_name = st.text_input("Task Name", placeholder="e.g. Fix login bug")
with col2:
    priority = st.selectbox(
        "Priority", options=[1, 2, 3, 4, 5],
        format_func=lambda x: f"{PRIORITY_LABELS[x][0]} {PRIORITY_LABELS[x][1]}"
    )
with col3:
    category = st.selectbox(
        "Category", options=list(CATEGORY_CONFIG.keys()),
        format_func=lambda x: f"{CATEGORY_CONFIG[x]['icon']} {x}"
    )
with col4:
    deadline = st.text_input("Deadline (optional)", placeholder="e.g. 2026-03-30")
    add_btn = st.button("➕ Add Task", use_container_width=True, type="primary")

if add_btn:
    if task_name.strip() == "":
        st.error("⚠️ Task name cannot be empty!")
    else:
        scheduler.add_task(
            name=task_name.strip(),
            priority=priority,
            deadline=deadline.strip() if deadline.strip() else None,
            category=category
        )
        st.success(f"✅ **'{task_name}'** added as {PRIORITY_LABELS[priority][1]} priority!")
        st.rerun()

st.divider()

# ── Task List ─────────────────────────────────────────────
st.subheader("📊 Current Schedule")

if scheduler.is_empty():
    st.markdown("""
    <div style='text-align:center; padding: 40px; color: #6c7086;'>
        <h3>🎉 All clear!</h3>
        <p>No pending tasks. Add some tasks above to get started.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    tasks = scheduler.get_all_tasks()
    st.caption(f"Showing {len(tasks)} task(s) — sorted by priority")
    st.write("")

    for i, task in enumerate(tasks):
        emoji, label = PRIORITY_LABELS[task.priority]
        deadline_str = f"&nbsp;&nbsp;📅 <b>{task.deadline}</b>" if task.deadline else ""
        col_task, col_btn = st.columns([6, 1])

        with col_task:
            cat = task.category if task.category in CATEGORY_CONFIG else "Other"
            cat_icon  = CATEGORY_CONFIG[cat]["icon"]
            cat_color = CATEGORY_CONFIG[cat]["color"]
            st.markdown(f"""
            <div class="task-card priority-{task.priority}">
                <span class="badge badge-{task.priority}">{emoji} {label}</span>
                <span class="badge" style="background:{cat_color}22; color:{cat_color}">
                    {cat_icon} {cat}
                </span>
                <p class="task-title">{task.name}</p>
                <p class="task-meta">🕐 Added: {task.created_at}{deadline_str}</p>
            </div>
            """, unsafe_allow_html=True)

        with col_btn:
            st.write("")
            st.write("")
            if st.button("✅ Done", key=f"done_{i}", use_container_width=True):
                removed = scheduler.remove_top_task()
                st.session_state.completed_count += 1
                st.toast(f"Completed: {removed.name} 🎉")
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
    if st.button("⚡ Complete Top Task", use_container_width=True, type="primary"):
        if scheduler.is_empty():
            st.warning("No tasks to complete!")
        else:
            removed = scheduler.remove_top_task()
            st.session_state.completed_count += 1
            st.toast(f"✅ Completed: {removed.name}")
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
                textfont=dict(color="#cdd6f4", size=12),
            )])
            fig_pie.update_layout(
                title=dict(text="Tasks by Category", font=dict(color="#cdd6f4", size=14)),
                paper_bgcolor="#1e1e2e", plot_bgcolor="#1e1e2e",
                font=dict(color="#cdd6f4"), showlegend=False,
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
            textfont=dict(color="#cdd6f4"),
        )])
        fig_bar.update_layout(
            title=dict(text="Tasks by Priority", font=dict(color="#cdd6f4", size=14)),
            paper_bgcolor="#1e1e2e", plot_bgcolor="#1e1e2e",
            font=dict(color="#cdd6f4"),
            xaxis=dict(tickfont=dict(color="#cdd6f4"), gridcolor="#313244"),
            yaxis=dict(tickfont=dict(color="#cdd6f4"), gridcolor="#313244"),
            margin=dict(t=40, b=20, l=20, r=20), height=300,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    if data["daily_counts"]:
        days   = sorted(data["daily_counts"].keys())
        counts = [data["daily_counts"][d] for d in days]
        fig_line = go.Figure(data=[go.Bar(
            x=days, y=counts, marker_color="#cba6f7",
            text=counts, textposition="outside",
            textfont=dict(color="#cdd6f4"),
        )])
        fig_line.update_layout(
            title=dict(text="Tasks Completed Per Day", font=dict(color="#cdd6f4", size=14)),
            paper_bgcolor="#1e1e2e", plot_bgcolor="#1e1e2e",
            font=dict(color="#cdd6f4"),
            xaxis=dict(tickfont=dict(color="#cdd6f4"), gridcolor="#313244"),
            yaxis=dict(
                tickfont=dict(color="#cdd6f4"), gridcolor="#313244",
                title=dict(text="Tasks Completed", font=dict(color="#6c7086"))
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
        <div style="background:#1e1e2e; border-radius:12px; padding:20px;
                    text-align:center; border: 2px solid {score_color};">
            <div style="font-size:2.5rem; font-weight:800; color:{score_color}">{rate}%</div>
            <div style="font-size:1rem; color:{score_color}; margin-top:4px;">{score_label}</div>
            <div style="font-size:0.75rem; color:#6c7086; margin-top:8px;">Completion Rate</div>
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