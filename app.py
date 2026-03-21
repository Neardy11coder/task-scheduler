import streamlit as st
from scheduler import TaskScheduler

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="Task Scheduler",
    page_icon="📋",
    layout="centered"
)

# ── Session state (persists data across reruns) ───────────
if "scheduler" not in st.session_state:
    st.session_state.scheduler = TaskScheduler()

scheduler = st.session_state.scheduler

# ── Title ─────────────────────────────────────────────────
st.title("📋 Priority-Based Task Scheduler")
st.caption("Powered by Min-Heap | Built with Streamlit")
st.divider()

# ── Add Task Form ─────────────────────────────────────────
st.subheader("➕ Add New Task")

col1, col2 = st.columns(2)

with col1:
    task_name = st.text_input("Task Name", placeholder="e.g. Fix login bug")
    priority = st.selectbox("Priority", [1, 2, 3, 4, 5],
                            help="1 = Highest, 5 = Lowest")

with col2:
    deadline = st.text_input("Deadline (optional)", placeholder="e.g. 2026-03-30")
    st.write("")  # spacer
    st.write("")  # spacer
    add_btn = st.button("Add Task ✅", use_container_width=True)

if add_btn:
    if task_name.strip() == "":
        st.error("Task name cannot be empty!")
    else:
        scheduler.add_task(
            name=task_name.strip(),
            priority=priority,
            deadline=deadline.strip() if deadline.strip() else None
        )
        st.success(f"Task **'{task_name}'** added with Priority {priority}!")
        st.rerun()

st.divider()

# ── Current Schedule ──────────────────────────────────────
st.subheader("📊 Current Schedule")

if scheduler.is_empty():
    st.info("No tasks yet. Add some tasks above!")
else:
    st.caption(f"Total pending tasks: **{scheduler.task_count()}**")

    tasks = scheduler.get_all_tasks()

    for i, task in enumerate(tasks):
        col_a, col_b = st.columns([5, 1])
        with col_a:
            deadline_str = f" | 📅 {task.deadline}" if task.deadline else ""
            priority_emoji = ["🔴", "🟠", "🟡", "🔵", "⚪"][task.priority - 1]
            st.markdown(
                f"{priority_emoji} **{task.name}** — Priority {task.priority}{deadline_str}  \n"
                f"<small>Added: {task.created_at}</small>",
                unsafe_allow_html=True
            )
        with col_b:
            if st.button("Done ✓", key=f"done_{i}"):
                removed = scheduler.remove_top_task()
                st.success(f"✅ Completed: **{removed.name}**")
                st.rerun()

st.divider()

# ── Complete Top Task ─────────────────────────────────────
st.subheader("⚡ Quick Complete")
st.caption("Instantly mark the highest priority task as done")

if st.button("Complete Top Task 🎯", use_container_width=True):
    if scheduler.is_empty():
        st.warning("No tasks to complete!")
    else:
        removed = scheduler.remove_top_task()
        st.success(f"✅ Completed: **{removed.name}** (Priority {removed.priority})")
        st.rerun()