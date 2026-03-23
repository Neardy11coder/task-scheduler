import streamlit as st
from ai_helper import suggest_priority_and_category, generate_weekly_plan
from components.utils import CATEGORY_CONFIG, PRIORITY_LABELS
from scheduler import TaskScheduler

def render_add_task():
    scheduler = st.session_state.scheduler

    # ── Add Task ──────────────────────────────────────────────
    st.subheader("➕ Add New Task")

    use_ai = st.toggle("🤖 AI Auto-Suggest Priority & Category", value=True)

    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

    with col1:
        task_name = st.text_input("Task Name", placeholder="e.g. Finish DSA assignment")

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

    tags_input = st.text_input("Tags (Optional, comma-separated)", placeholder="e.g. study, urgent, chores")
    subtasks_text = st.text_area("Sub-tasks (Optional)", placeholder="Buy domain\nDesign logo", height=100)
    add_btn = st.button("➕ Add Task", use_container_width=True, type="primary")

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
                        
            parsed_tags = [t.strip().lower() for t in tags_input.split(",")] if tags_input.strip() else []
            scheduler.add_task(
                name=task_name.strip(),
                priority=priority,
                deadline=deadline.strip() if deadline.strip() else None,
                category=category,
                subtasks=subtasks_list,
                dependencies=selected_deps,
                recurrence=recurrence_dict,
                tags=parsed_tags
            )
            st.success(f"✅ **'{task_name}'** added as {PRIORITY_LABELS[priority][1]} priority!")
            st.session_state.play_audio = 'add'
            st.rerun()

    st.divider()

    # ── AI Weekly Planner ─────────────────────────────────────
    with st.expander("🗓️ AI Weekly Planner — Describe your week, AI creates your tasks"):
        st.caption("Tell the AI what you need to accomplish this week and it will create all your tasks automatically")

        weekly_goals = st.text_area(
            "What do you need to accomplish this week?",
            placeholder="Example:\nI have a DSA exam on Friday, need to submit my OS assignment by Wednesday...",
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
                st.session_state.scheduler = TaskScheduler(user_id=st.session_state.user_id)
                st.success(f"🎉 Added {len(tasks)} tasks to your schedule!")
                st.rerun()

        with col_cancel:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.generated_tasks = None
                st.session_state.show_generated = False
                st.rerun()
