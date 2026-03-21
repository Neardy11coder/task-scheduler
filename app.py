import streamlit as st
from scheduler import TaskScheduler
from visualizer import generate_heap_html
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
    .task-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #cdd6f4;
        margin: 0;
    }
    .task-meta {
        font-size: 0.8rem;
        color: #6c7086;
        margin-top: 4px;
    }
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 8px;
    }
    .badge-1 { background: #f38ba822; color: #f38ba8; }
    .badge-2 { background: #fab38722; color: #fab387; }
    .badge-3 { background: #f9e2af22; color: #f9e2af; }
    .badge-4 { background: #89b4fa22; color: #89b4fa; }
    .badge-5 { background: #a6e3a122; color: #a6e3a1; }
    .stat-box {
        background: #1e1e2e;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        margin-bottom: 12px;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 800;
        color: #cba6f7;
    }
    .stat-label {
        font-size: 0.8rem;
        color: #6c7086;
    }
    div[data-testid="stSidebar"] {
        background: #181825;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────
if "scheduler" not in st.session_state:
    st.session_state.scheduler = TaskScheduler()
if "completed_count" not in st.session_state:
    st.session_state.completed_count = 0

scheduler = st.session_state.scheduler

# ── Priority helpers ──────────────────────────────────────
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

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📋 Task Scheduler")
    st.caption("Powered by Min-Heap DSA")
    st.divider()

    # Stats
    total = scheduler.task_count()
    completed = st.session_state.completed_count

    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">{total}</div>
        <div class="stat-label">Pending Tasks</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">{completed}</div>
        <div class="stat-label">Completed Today</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Priority legend
    st.markdown("#### Priority Legend")
    for p, (emoji, label) in PRIORITY_LABELS.items():
        st.markdown(f"{emoji} **{label}** — Level {p}")

    st.divider()

    # Top task preview
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
        "Priority",
        options=[1, 2, 3, 4, 5],
        format_func=lambda x: f"{PRIORITY_LABELS[x][0]} {PRIORITY_LABELS[x][1]}"
    )

with col3:
    category = st.selectbox(
        "Category",
        options=list(CATEGORY_CONFIG.keys()),
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
            cat_icon = CATEGORY_CONFIG[cat]["icon"]
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
        - **Root node** = highest priority task (always served first)
        - **Node index** = position in the heap array
        - **Color** = priority level
        - **Left/Right children** always have lower priority than parent
        """)
        st.divider()
        st.markdown("#### Heap Array")
        st.caption("Raw heap internal order:")
        for i, (p, _, t) in enumerate(sorted(scheduler._heap)):
            st.caption(f"`[{i}]` P{p} — {t.name[:15]}")

st.divider()

# ── Quick Complete ────────────────────────────────────────
col_quick, col_clear = st.columns(2)

with col_quick:
    if st.button("⚡ Complete Top Task", use_container_width=True, type="primary"):
        if scheduler.is_empty():
            st.warning("No tasks to complete!")
        else:
            removed = scheduler.remove_top_task()
            st.session_state.completed_count += 1
            st.toast(f"✅ Completed: {removed.name}")
            st.rerun()

with col_clear:
    if st.button("🗑️ Clear All Tasks", use_container_width=True):
        scheduler.clear_all()
        st.session_state.completed_count = 0
        st.toast("All tasks cleared!")
        st.rerun()