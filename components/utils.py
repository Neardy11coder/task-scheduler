import streamlit as st

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

def get_theme():
    _dark = st.session_state.get("theme", "dark") == "dark"
    return {
        "bg_base":    "#1e1e2e" if _dark else "#eff1f5",
        "bg_surface": "#181825" if _dark else "#dce0e8",
        "bg_card":    "#1e1e2e" if _dark else "#ffffff",
        "text_main":  "#cdd6f4" if _dark else "#4c4f69",
        "text_muted": "#6c7086" if _dark else "#7c7f93",
        "text_sub":   "#9ca0b0" if _dark else "#9ca0b0",
        "accent":     "#cba6f7" if _dark else "#7287fd",
        "border":     "#313244" if _dark else "#ccd0da",
        "border_light": "#45475a" if _dark else "#bcc0cc",
        "success":    "#a6e3a1" if _dark else "#40a02b",
        "chart_bg":   "#1e1e2e" if _dark else "#ffffff",
        "grid":       "#313244" if _dark else "#e0e4ef",
    }

def apply_custom_css():
    T = get_theme()
    st.markdown(f"""
    <style>
        /* ── Dynamic Theme Variables ── */
        :root {{
            --bg-base:      {T['bg_base']};
            --bg-surface:   {T['bg_surface']};
            --bg-card:      {T['bg_card']};
            --text-main:    {T['text_main']};
            --text-muted:   {T['text_muted']};
            --text-sub:     {T['text_sub']};
            --accent:       {T['accent']};
            --border:       {T['border']};
            --border-light: {T['border_light']};
            --success:      {T['success']};
            --chart-bg:     {T['chart_bg']};
        }}
        .task-card {{
            background: var(--bg-card);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 12px;
            border-left: 5px solid var(--text-main);
        }}
        .priority-1 {{ border-left-color: #f38ba8; }}
        .priority-2 {{ border-left-color: #fab387; }}
        .priority-3 {{ border-left-color: #f9e2af; }}
        .priority-4 {{ border-left-color: #89b4fa; }}
        .priority-5 {{ border-left-color: #a6e3a1; }}
        .task-title {{ font-size: 1.1rem; font-weight: 700; color: var(--text-main); margin: 0; }}
        .task-meta {{ font-size: 0.8rem; color: var(--text-muted); margin-top: 4px; }}
        .badge {{
            display: inline-block; padding: 2px 10px;
            border-radius: 20px; font-size: 0.75rem;
            font-weight: 600; margin-right: 8px;
        }}
        .badge-1 {{ background: #f38ba822; color: #f38ba8; }}
        .badge-2 {{ background: #fab38722; color: #fab387; }}
        .badge-3 {{ background: #f9e2af22; color: #f9e2af; }}
        .badge-4 {{ background: #89b4fa22; color: #89b4fa; }}
        .badge-5 {{ background: #a6e3a122; color: #a6e3a1; }}
        .stat-box {{
            background: var(--bg-card); border-radius: 10px;
            padding: 16px; text-align: center; margin-bottom: 12px;
            border: 1px solid var(--border);
        }}
        .stat-number {{ font-size: 2rem; font-weight: 800; color: var(--accent); }}
        .stat-label {{ font-size: 0.8rem; color: var(--text-muted); }}
        div[data-testid="stSidebar"] {{ background: var(--bg-surface) !important; }}
        div[data-testid="stAppViewContainer"] {{ background: var(--bg-base) !important; }}
        div[data-testid="stHeader"] {{ background: var(--bg-base) !important; }}
        .completed-row {{
            padding: 8px 12px; border-radius: 8px; margin-bottom: 6px;
            background: var(--bg-card); border-left: 3px solid var(--success);
            color: var(--text-muted); font-size: 0.85rem;
        }}
        .auth-box {{
            max-width: 420px; margin: 60px auto;
            background: var(--bg-card); border-radius: 16px;
            padding: 40px; border: 1px solid var(--border);
        }}
        /* Force Streamlit elements to use our text colors */
        .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp span, .stApp label, .stApp li {{
            color: var(--text-main) !important;
        }}
        .stMarkdown p {{ color: var(--text-main) !important; }}
        /* Theme transition */
        *, *::before, *::after {{ transition: background-color 0.25s ease, color 0.2s ease, border-color 0.2s ease; }}
        
        /* ── Mobile Layout Optimizations ── */
        @media (max-width: 768px) {{
            .block-container {{
                padding-top: 2rem !important;
                padding-bottom: 2rem !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }}
            h1 {{
                font-size: 1.8rem !important;
            }}
            h2 {{
                font-size: 1.5rem !important;
            }}
            h3 {{
                font-size: 1.25rem !important;
            }}
            /* Tighten whitespace within expanders to boost density natively */
            div[data-testid="stExpanderDetails"] {{
                padding-left: 0.5rem !important;
                padding-right: 0.5rem !important;
                padding-bottom: 0.5rem !important;
            }}
            /* Scale down the gamification sidebar numbers */
            .stat-box {{
                padding: 10px !important;
                margin-bottom: 10px !important;
            }}
            .stat-number {{
                font-size: 1.5rem !important;
            }}
        }}
    </style>
    """, unsafe_allow_html=True)
