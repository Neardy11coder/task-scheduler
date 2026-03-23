import streamlit as st
import json
import streamlit.components.v1 as components
from supabase_db import get_exams
from components.utils import CATEGORY_CONFIG, get_theme

def render_calendar():
    user_id = st.session_state.user_id
    scheduler = st.session_state.scheduler
    T = get_theme()

    st.subheader("📆 Interactive Calendar")
    st.caption("View your exams and tasks with deadlines in a monthly calendar")

    calendar_events = []

    # Add active tasks with deadlines
    for t in scheduler.get_all_tasks():
        if t.deadline:
            calendar_events.append({
                "title": f"[P{t.priority}] {t.name}",
                "start": t.deadline,
                "color": CATEGORY_CONFIG.get(t.category, {}).get("color", "#cba6f7"),
                "allDay": True
            })

    # Add exams
    exams = get_exams(user_id)
    for ex in exams:
        calendar_events.append({
            "title": f"📝 EXAM: {ex['subject']}",
            "start": ex["exam_date"],
            "color": "#f38ba8",
            "allDay": True
        })

    events_json = json.dumps(calendar_events)

    calendar_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.10/index.global.min.js"></script>
    <style>
      body {{
        background: transparent;
        color: {T['text_main']};
        font-family: 'Segoe UI', system-ui, sans-serif;
        margin: 0; padding: 0;
      }}
      #calendar {{
        max-width: 100%;
        margin: 0 auto;
        background: {T['bg_card']};
        padding: 15px;
        border-radius: 12px;
        border: 1px solid {T['border']};
      }}
      .fc-theme-standard td, .fc-theme-standard th {{
        border-color: {T['grid']} !important;
      }}
      .fc-button {{
        background: {T['bg_surface']} !important;
        border: 1px solid {T['border']} !important;
        color: {T['text_main']} !important;
        text-transform: capitalize !important;
        box-shadow: none !important;
      }}
      .fc-button-primary:not(:disabled):active, .fc-button-primary:not(:disabled).fc-button-active {{
        background: {T['accent']} !important;
        color: {T['bg_base']} !important;
        border-color: {T['accent']} !important;
      }}
      .fc-col-header-cell-cushion {{ color: {T['text_main']} !important; }}
      .fc-event {{
        border: none !important;
        padding: 3px 6px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
      }}
      .fc-daygrid-day-number {{
        color: {T['text_muted']};
        text-decoration: none;
      }}
      .fc-toolbar-title {{
        font-size: 1.2rem !important;
        color: {T['text_main']} !important;
      }}
    </style>
    </head>
    <body>
    <div id="calendar"></div>
    <script>
      document.addEventListener('DOMContentLoaded', function() {{
        var calendarEl = document.getElementById('calendar');
        var calendar = new FullCalendar.Calendar(calendarEl, {{
          initialView: 'dayGridMonth',
          headerToolbar: {{
            left: 'title',
            right: 'prev,next today'
          }},
          events: {events_json},
          height: 550
        }});
        calendar.render();
      }});
    </script>
    </body>
    </html>
    """
    components.html(calendar_html, height=580, scrolling=False)
