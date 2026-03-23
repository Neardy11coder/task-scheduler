import streamlit as st
from datetime import date
from gamification import get_avatar, get_level_threshold, calculate_streak
from supabase_db import get_user_stats, update_user_stats, get_task_stats, get_exams
from export_utils import generate_csv_payload, generate_markdown_report
from calendar_export import generate_ics
from components.utils import PRIORITY_LABELS

def render_sidebar():
    user_id = st.session_state.user_id
    scheduler = st.session_state.scheduler

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
        st.markdown(f'''
        <div class="stat-box">
            <div class="stat-number">{{stats['pending']}}</div>
            <div class="stat-label">Pending Tasks</div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown(f'''
        <div class="stat-box">
            <div class="stat-number">{{stats['completed']}}</div>
            <div class="stat-label">Completed Total</div>
        </div>
        ''', unsafe_allow_html=True)

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
                elif r_type == "interval": recur_str = f" | 🔁 Every {{top_recur.get('days', 2)}} days"

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

        st.markdown("#### 📥 Export Data")
        csv_data = generate_csv_payload(user_id)
        if csv_data:
            st.download_button(
                label="📊 Download CSV",
                data=csv_data,
                file_name="tasks_export.csv",
                mime="text/csv",
                use_container_width=True,
                help="Raw tabular data for Excel or spreadsheets"
            )
            
        md_data = generate_markdown_report(user_id, scheduler.get_all_tasks())
        if md_data:
            st.download_button(
                label="📜 Download Report (MD)",
                data=md_data,
                file_name="productivity_report.md",
                mime="text/markdown",
                use_container_width=True,
                help="Beautifully formatted summary for Notion/Obsidian"
            )

        st.divider()

        st.markdown("#### 📅 Calendar Export")
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
