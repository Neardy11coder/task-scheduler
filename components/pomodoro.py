import streamlit as st
import streamlit.components.v1 as components

def render_pomodoro():
    scheduler = st.session_state.scheduler

    st.subheader("🍅 Pomodoro Timer")
    st.caption("Stay focused with timed work sessions. Pick a task and start the clock!")

    # Task selector for Pomodoro
    pomo_tasks = [(t.name, t.priority) for _, _, t in sorted(scheduler._heap)] if not scheduler.is_empty() else []
    pomo_options = [f"{['🔴','🟠','🟡','🔵','⚪'][p-1]} {name}" for name, p in pomo_tasks]
    pomo_options_raw = [name for name, _ in pomo_tasks]

    col_task_sel, col_pomo_count = st.columns([3, 1])
    with col_task_sel:
        selected_idx = st.selectbox(
            "🎯 Working on",
            options=range(len(pomo_options)),
            format_func=lambda i: pomo_options[i] if pomo_options else "No tasks — add one first!",
            disabled=len(pomo_options) == 0,
            label_visibility="collapsed"
        ) if pomo_options else None
        selected_task_name = pomo_options_raw[selected_idx] if (pomo_options and selected_idx is not None) else "No task selected"

    with col_pomo_count:
        st.markdown(f"""
        <div class="stat-box" style="margin:0">
            <div class="stat-number" style="font-size:1.6rem">{{st.session_state.pomodoro_count}}</div>
            <div class="stat-label">🍅 Done today</div>
        </div>
        """, unsafe_allow_html=True)

    pomo_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      body {{
        background: transparent;
        font-family: 'Segoe UI', system-ui, sans-serif;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 320px;
      }}
      .pomo-wrap {{
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 18px;
        width: 100%;
        max-width: 480px;
      }}
      .mode-btns {{ display: flex; gap: 8px; }}
      .mode-btn {{
        padding: 6px 18px;
        border-radius: 20px;
        border: 1.5px solid #45475a;
        background: transparent;
        color: #6c7086;
        font-size: 0.82rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
      }}
      .mode-btn.active {{
        border-color: #f38ba8; color: #f38ba8; background: #f38ba811;
      }}
      .mode-btn:hover:not(.active) {{
        border-color: #585b70; color: #cdd6f4;
      }}
      .ring-wrap {{ position: relative; width: 200px; height: 200px; }}
      svg {{ transform: rotate(-90deg); }}
      .bg-ring {{ fill: none; stroke: #313244; stroke-width: 12; }}
      .prog-ring {{ fill: none; stroke: #f38ba8; stroke-width: 12;
        stroke-linecap: round;
        transition: stroke-dashoffset 1s linear, stroke 0.4s;
      }}
      .timer-label {{
        position: absolute; top: 50%; left: 50%;
        transform: translate(-50%, -50%); text-align: center;
      }}
      .timer-time {{
        font-size: 2.6rem; font-weight: 800; color: #cdd6f4;
        letter-spacing: 2px; line-height: 1;
      }}
      .timer-task {{
        font-size: 0.72rem; color: #6c7086; margin-top: 6px;
        max-width: 130px; overflow: hidden; white-space: nowrap;
        text-overflow: ellipsis;
      }}
      .control-btns {{ display: flex; gap: 12px; }}
      .ctrl-btn {{
        padding: 10px 28px; border-radius: 30px; border: none;
        font-size: 0.9rem; font-weight: 700; cursor: pointer;
        transition: all 0.2s; letter-spacing: 0.5px;
      }}
      .btn-start {{ background: #a6e3a1; color: #1e1e2e; }}
      .btn-start:hover {{ background: #94d4a0; transform: scale(1.04); }}
      .btn-pause {{ background: #f9e2af; color: #1e1e2e; }}
      .btn-pause:hover {{ background: #e8d19e; transform: scale(1.04); }}
      .btn-reset {{ background: #313244; color: #cdd6f4; }}
      .btn-reset:hover {{ background: #45475a; transform: scale(1.04); }}
      .session-done {{
        font-size: 0.8rem; color: #a6e3a1; opacity: 0;
        transition: opacity 0.5s; font-weight: 600;
      }}
      .session-done.show {{ opacity: 1; }}
    </style>
    </head>
    <body>
    <div class="pomo-wrap">
      <div class="mode-btns">
        <button class="mode-btn active" id="btn-work"   onclick="setMode('work')">🍅 Work</button>
        <button class="mode-btn"        id="btn-short"  onclick="setMode('short')">☕ Short Break</button>
        <button class="mode-btn"        id="btn-long"   onclick="setMode('long')">🛋️ Long Break</button>
      </div>

      <div class="ring-wrap">
        <svg width="200" height="200" viewBox="0 0 200 200">
          <circle class="bg-ring"   cx="100" cy="100" r="88"/>
          <circle class="prog-ring" cx="100" cy="100" r="88"
                  id="progress-ring" stroke-dasharray="553" stroke-dashoffset="0"/>
        </svg>
        <div class="timer-label">
          <div class="timer-time" id="timer-display">25:00</div>
          <div class="timer-task" id="task-name-label">{selected_task_name}</div>
        </div>
      </div>

      <div class="control-btns">
        <button class="ctrl-btn btn-start" id="btn-start-pause" onclick="toggleTimer()">▶ Start</button>
        <button class="ctrl-btn btn-reset" onclick="resetTimer()">↺ Reset</button>
      </div>

      <div class="session-done" id="session-done-msg">✅ Session complete! Great work!</div>
    </div>

    <script>
      const MODES = {{ work: 25*60, short: 5*60, long: 15*60 }};
      const COLORS = {{ work: '#f38ba8', short: '#a6e3a1', long: '#89b4fa' }};
      const CIRC = 2 * Math.PI * 88;

      let mode = 'work';
      let totalSecs = MODES[mode];
      let secsLeft  = totalSecs;
      let running   = false;
      let interval  = null;

      const ring    = document.getElementById('progress-ring');
      const display = document.getElementById('timer-display');
      const msgEl   = document.getElementById('session-done-msg');
      const startBtn = document.getElementById('btn-start-pause');

      function setMode(m) {{
        if (running) return;
        mode = m;
        totalSecs = MODES[m];
        secsLeft  = totalSecs;
        ring.style.stroke = COLORS[m];
        document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
        document.getElementById('btn-' + m).classList.add('active');
        updateDisplay();
        updateRing();
        msgEl.classList.remove('show');
      }}

      function fmt(s) {{
        const m = Math.floor(s / 60);
        const sec = s % 60;
        return String(m).padStart(2,'0') + ':' + String(sec).padStart(2,'0');
      }}

      function updateDisplay() {{
        display.textContent = fmt(secsLeft);
      }}

      function updateRing() {{
        const pct = secsLeft / totalSecs;
        ring.style.strokeDashoffset = CIRC * (1 - pct);
      }}

      function toggleTimer() {{
        if (running) {{
          clearInterval(interval);
          running = false;
          startBtn.textContent = '▶ Resume';
          startBtn.className = 'ctrl-btn btn-start';
        }} else {{
          running = true;
          startBtn.textContent = '⏸ Pause';
          startBtn.className = 'ctrl-btn btn-pause';
          msgEl.classList.remove('show');
          interval = setInterval(tick, 1000);
        }}
      }}

      function tick() {{
        if (secsLeft <= 0) {{
          clearInterval(interval);
          running = false;
          startBtn.textContent = '▶ Start';
          startBtn.className = 'ctrl-btn btn-start';
          msgEl.classList.add('show');
          try {{
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain); gain.connect(ctx.destination);
            osc.frequency.value = 880;
            osc.type = 'sine';
            gain.gain.setValueAtTime(0.4, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.2);
            osc.start(); osc.stop(ctx.currentTime + 1.2);
          }} catch(e) {{}}
          return;
        }}
        secsLeft--;
        updateDisplay();
        updateRing();
      }}

      function resetTimer() {{
        clearInterval(interval);
        running = false;
        secsLeft = totalSecs;
        startBtn.textContent = '▶ Start';
        startBtn.className = 'ctrl-btn btn-start';
        msgEl.classList.remove('show');
        updateDisplay();
        updateRing();
      }}

      ring.style.strokeDasharray = CIRC;
      ring.style.stroke = COLORS[mode];
      updateDisplay();
      updateRing();
    </script>
    </body>
    </html>
    """

    components.html(pomo_html, height=360, scrolling=False)
