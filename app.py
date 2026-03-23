import streamlit as st
from scheduler import TaskScheduler
from components.utils import apply_custom_css, CATEGORY_CONFIG
from components.auth import render_auth
from components.sidebar import render_sidebar
from components.active_tasks import render_active_tasks
from components.add_task import render_add_task
from components.pomodoro import render_pomodoro
from components.exams import render_exams
from components.calendar import render_calendar
from components.analytics import render_analytics
from components.leaderboard import render_leaderboard
from components.pwa import render_pwa
from visualizer import generate_heap_html
import streamlit.components.v1 as components
from datetime import date, timedelta
from supabase_db import get_user_stats, update_user_stats, get_completed_tasks
from gamification import get_level_threshold, get_xp_for_priority

# ── Session state & Theme ─────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="Task Scheduler",
    page_icon="📋",
    layout="wide"
)

# Apply global CSS
apply_custom_css()

# Inject PWA tags
render_pwa()

# ── Session state init ────────────────────────────────────
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
if "play_audio" not in st.session_state:
    st.session_state.play_audio = None

# Render auth if not logged in
render_auth()

# ── App (only shown when logged in) ──────────────────────
if "scheduler" not in st.session_state:
    st.session_state.scheduler = TaskScheduler(user_id=st.session_state.user_id)

scheduler = st.session_state.scheduler
user_id = st.session_state.user_id

# ── Sidebar ───────────────────────────────────────────────
render_sidebar()

# ── Main area ─────────────────────────────────────────────
st.title("📋 Priority-Based Task Scheduler")

# Audio Player Component
if st.session_state.play_audio:
    sound_type = st.session_state.play_audio
    st.session_state.play_audio = None
    components.html(f"""
    <script>
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      function play(type) {{
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.connect(gain); gain.connect(ctx.destination);
          
          if(type === 'complete') {{
              osc.type = 'sine';
              osc.frequency.setValueAtTime(523.25, ctx.currentTime);
              osc.frequency.setValueAtTime(659.25, ctx.currentTime + 0.1);
              gain.gain.setValueAtTime(0.2, ctx.currentTime);
              gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);
              osc.start(ctx.currentTime);
              osc.stop(ctx.currentTime + 0.4);
          }} else if(type === 'add') {{
              osc.type = 'sine';
              osc.frequency.setValueAtTime(440, ctx.currentTime);
              gain.gain.setValueAtTime(0.1, ctx.currentTime);
              gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.15);
              osc.start(ctx.currentTime);
              osc.stop(ctx.currentTime + 0.2);
          }} else if(type === 'level_up') {{
              osc.type = 'triangle';
              osc.frequency.setValueAtTime(440, ctx.currentTime);
              osc.frequency.setValueAtTime(554.37, ctx.currentTime + 0.15);
              osc.frequency.setValueAtTime(659.25, ctx.currentTime + 0.3);
              osc.frequency.setValueAtTime(880, ctx.currentTime + 0.45);
              gain.gain.setValueAtTime(0.2, ctx.currentTime);
              gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.8);
              osc.start(ctx.currentTime);
              osc.stop(ctx.currentTime + 0.9);
          }}
      }}
      play('{sound_type}');
    </script>
    """, height=0, width=0)

st.caption("Tasks are automatically sorted by urgency using a Min-Heap")
st.divider()

render_active_tasks()
render_add_task()
render_pomodoro()
render_exams()
render_calendar()

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
                st.session_state.play_audio = 'level_up' if leveled_up else 'complete'
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

# ── Completed tasks ───────────────────────────────────────
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

# ── Modular Dashboard Ends ────────────────────────────────
render_analytics()
st.divider()
render_leaderboard()