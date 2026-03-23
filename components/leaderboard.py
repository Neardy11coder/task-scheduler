import streamlit as st
from supabase_db import get_leaderboard_xp, get_leaderboard_streak, get_leaderboard_tasks
from gamification import get_avatar
from components.utils import get_theme

def render_leaderboard():
    user_id = st.session_state.user_id
    T = get_theme()

    st.subheader("🏆 Leaderboard")
    st.caption("Compete with others — usernames are anonymized for privacy")

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
