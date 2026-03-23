import streamlit as st
from datetime import datetime, date
from supabase_db import save_exam, get_exams, delete_exam
from ai_helper import generate_exam_tasks
from scheduler import TaskScheduler
from components.utils import get_theme

def render_exams():
    user_id = st.session_state.user_id
    scheduler = st.session_state.scheduler
    T = get_theme()

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

            # Exam countdown card
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
