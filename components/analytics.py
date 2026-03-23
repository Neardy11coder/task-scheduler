import streamlit as st
import plotly.graph_objects as go
from supabase_db import get_analytics_data
from components.utils import get_theme

def render_analytics():
    user_id = st.session_state.user_id
    scheduler = st.session_state.scheduler
    T = get_theme()

    st.subheader("📈 Analytics Dashboard")
    st.caption("Productivity insights powered by your task history")

    data = get_analytics_data(user_id)

    if data["total"] == 0:
        st.info("Add and complete some tasks to see analytics!")
    else:
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f"""<div class="stat-box">
                <div class="stat-number">{data['total']}</div>
                <div class="stat-label">Total Tasks</div></div>""",
                unsafe_allow_html=True)
        with k2:
            st.markdown(f"""<div class="stat-box">
                <div class="stat-number">{data['completed']}</div>
                <div class="stat-label">Completed</div></div>""",
                unsafe_allow_html=True)
        with k3:
            st.markdown(f"""<div class="stat-box">
                <div class="stat-number">{data['pending']}</div>
                <div class="stat-label">Pending</div></div>""",
                unsafe_allow_html=True)
        with k4:
            st.markdown(f"""<div class="stat-box">
                <div class="stat-number">{data['completion_rate']}%</div>
                <div class="stat-label">Completion Rate</div></div>""",
                unsafe_allow_html=True)

        st.write("")
        chart1, chart2 = st.columns(2)

        with chart1:
            if data["category_counts"]:
                cats   = list(data["category_counts"].keys())
                counts = list(data["category_counts"].values())
                colors = ["#89b4fa", "#a6e3a1", "#f9e2af", "#f38ba8", "#cba6f7"]
                fig_pie = go.Figure(data=[go.Pie(
                    labels=cats, values=counts, hole=0.5,
                    marker=dict(colors=colors[:len(cats)]),
                    textinfo="label+percent",
                    textfont=dict(color=T["text_main"], size=12),
                )])
                fig_pie.update_layout(
                    title=dict(text="Tasks by Category", font=dict(color=T["text_main"], size=14)),
                    paper_bgcolor=T["chart_bg"], plot_bgcolor=T["chart_bg"],
                    font=dict(color=T["text_main"]), showlegend=False,
                    margin=dict(t=40, b=20, l=20, r=20), height=300,
                )
                st.plotly_chart(fig_pie, use_container_width=True)

        with chart2:
            priority_labels = ["P1 Critical", "P2 High", "P3 Medium", "P4 Low", "P5 Minimal"]
            priority_colors = ["#f38ba8", "#fab387", "#f9e2af", "#89b4fa", "#a6e3a1"]
            priority_values = [data["priority_counts"].get(i, 0) for i in range(1, 6)]
            fig_bar = go.Figure(data=[go.Bar(
                x=priority_labels, y=priority_values,
                marker_color=priority_colors,
                text=priority_values, textposition="outside",
                textfont=dict(color=T["text_main"]),
            )])
            fig_bar.update_layout(
                title=dict(text="Tasks by Priority", font=dict(color=T["text_main"], size=14)),
                paper_bgcolor=T["chart_bg"], plot_bgcolor=T["chart_bg"],
                font=dict(color=T["text_main"]),
                xaxis=dict(tickfont=dict(color=T["text_main"]), gridcolor=T["grid"]),
                yaxis=dict(tickfont=dict(color=T["text_main"]), gridcolor=T["grid"]),
                margin=dict(t=40, b=20, l=20, r=20), height=300,
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        if data["daily_counts"]:
            days   = sorted(data["daily_counts"].keys())
            counts = [data["daily_counts"][d] for d in days]
            fig_line = go.Figure(data=[go.Bar(
                x=days, y=counts, marker_color=T["accent"],
                text=counts, textposition="outside",
                textfont=dict(color=T["text_main"]),
            )])
            fig_line.update_layout(
                title=dict(text="Tasks Completed Per Day", font=dict(color=T["text_main"], size=14)),
                paper_bgcolor=T["chart_bg"], plot_bgcolor=T["chart_bg"],
                font=dict(color=T["text_main"]),
                xaxis=dict(tickfont=dict(color=T["text_main"]), gridcolor=T["grid"]),
                yaxis=dict(
                    tickfont=dict(color=T["text_main"]), gridcolor=T["grid"],
                    title=dict(text="Tasks Completed", font=dict(color=T["text_muted"]))
                ),
                margin=dict(t=40, b=20, l=20, r=20), height=280,
            )
            st.plotly_chart(fig_line, use_container_width=True)

        st.write("")
        score_col, tip_col = st.columns([1, 2])

        with score_col:
            rate = data["completion_rate"]
            if rate >= 80:
                score_color = "#a6e3a1"
                score_label = "Excellent 🔥"
            elif rate >= 50:
                score_color = "#f9e2af"
                score_label = "Good 👍"
            elif rate >= 25:
                score_color = "#fab387"
                score_label = "Improving 📈"
            else:
                score_color = "#f38ba8"
                score_label = "Just Starting 🌱"

            st.markdown(f"""
            <div style="background:{T['bg_card']}; border-radius:12px; padding:20px;
                        text-align:center; border: 2px solid {score_color};">
                <div style="font-size:2.5rem; font-weight:800; color:{score_color}">{rate}%</div>
                <div style="font-size:1rem; color:{score_color}; margin-top:4px;">{score_label}</div>
                <div style="font-size:0.75rem; color:{T['text_muted']}; margin-top:8px;">Completion Rate</div>
            </div>
            """, unsafe_allow_html=True)

        with tip_col:
            st.markdown("#### 💡 Productivity Insights")
            if data["pending"] > 5:
                st.warning(f"⚠️ You have {data['pending']} pending tasks!")
            if data["priority_counts"].get(1, 0) > 3:
                st.error(f"🔴 {data['priority_counts'][1]} Critical tasks — focus here first!")
            if rate >= 80:
                st.success("🔥 Outstanding completion rate!")
            elif rate >= 50:
                st.info("👍 Good progress! Keep completing high priority tasks.")
            else:
                st.info("🌱 Just getting started! Complete your top priority task first.")
            top = scheduler.peek_top_task()
            if top:
                st.markdown(f"**Next recommended task:** {top.name} (Priority {top.priority})")
