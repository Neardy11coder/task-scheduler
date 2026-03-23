import streamlit as st
from supabase_db import get_completed_tasks, update_task_subtasks
from components.utils import CATEGORY_CONFIG, PRIORITY_LABELS

def render_active_tasks():
    scheduler = st.session_state.scheduler

    # ── Global Search ─────────────────────────────────────────
    with st.expander("🔍 Global Search (Active & Completed Tasks)", expanded=False):
        global_query = st.text_input("Search by task name, subtasks, or tags...", key="global_q")
        if global_query.strip():
            q = global_query.strip().lower()
            all_act = scheduler.get_all_tasks()
            found_act = [t for t in all_act if q in t.name.lower() or any(q in s.get("text","").lower() for s in getattr(t, "subtasks", [])) or any(q in tag.lower() for tag in getattr(t, "tags", []))]
            
            all_comp = get_completed_tasks(st.session_state.user_id)
            found_comp = [c for c in all_comp if q in c["name"].lower()]
            
            if not found_act and not found_comp:
                st.info("No matching tasks found.")
            else:
                if found_act:
                    st.markdown("**🔥 Active Matches**")
                    for t in found_act:
                        emoji, label = PRIORITY_LABELS[t.priority]
                        deadline_str = f" | Due: {t.deadline}" if t.deadline else ""
                        st.markdown(f"- {emoji} **{t.name}** (Priority {t.priority}){deadline_str}")
                if found_comp:
                    st.markdown("**✅ Completed Matches**")
                    for c in found_comp:
                        emoji = ["🔴", "🟠", "🟡", "🔵", "⚪"][c["priority"] - 1]
                        deadline_str = f" | Due: {c['deadline']}" if c.get("deadline") else ""
                        st.markdown(f"- {emoji} <s>{c['name']}</s> (Priority {c['priority']}){deadline_str}")

    # ── Active Tasks (Checklists) ─────────────────────────────
    st.subheader("🔥 Active Tasks")
    all_pending = scheduler.get_all_tasks()

    if not all_pending:
        st.info("No active tasks! Add one below.")
    else:
        # --- Filter UI ---
        all_tags = sorted(list(set(tag for t in all_pending for tag in getattr(t, "tags", []))))
        all_cats = sorted(list(set(t.category for t in all_pending)))
        
        search_query = st.text_input("🔍 Search", placeholder="Search task name or subtasks...", label_visibility="collapsed")
        
        filt_col1, filt_col2 = st.columns(2)
        with filt_col1:
            cat_filter = st.multiselect("Filter by Category", all_cats, placeholder="All Categories")
        with filt_col2:
            tag_filter = st.multiselect("Filter by Tags", all_tags, placeholder="All Tags")
            
        pending_tasks = all_pending
        if search_query:
            query_lower = search_query.strip().lower()
            pending_tasks = [
                t for t in pending_tasks 
                if query_lower in t.name.lower() or 
                   any(query_lower in s.get("text", "").lower() for s in getattr(t, "subtasks", []))
            ]
        if cat_filter:
            pending_tasks = [t for t in pending_tasks if t.category in cat_filter]
        if tag_filter:
            pending_tasks = [t for t in pending_tasks if any(tag in getattr(t, "tags", []) for tag in tag_filter)]

        if not pending_tasks:
            st.info("No tasks match your filters.")
            
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

            tag_badges = ""
            task_tags = getattr(task, "tags", [])
            if task_tags:
                tag_badges = " " + " ".join([f"`#{t}`" for t in task_tags])

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

                st.caption(f"{label} Priority | {cat_icon} {task.category}{deadline_str}{recur_str}{tag_badges}")
                
                if total_sub > 0:
                    for i, sub in enumerate(task.subtasks):
                        sub_key = f"sub_{task.db_id}_{i}"
                        is_checked = st.checkbox(sub["text"], value=sub.get("completed", False), key=sub_key)
                        
                        if is_checked != sub.get("completed", False):
                            task.subtasks[i]["completed"] = is_checked
                            update_task_subtasks(task.db_id, task.subtasks)
                            st.rerun()
                else:
                    st.caption("No sub-tasks.")
