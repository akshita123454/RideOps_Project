"""
2_Ops_Command.py — Executive Operations Command Center
Operational Throughput Dynamics, Capacity Reclaim Simulator, and Team Heatmap
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from engine.data_loader import load_tickets
from engine.metrics import (
    weekly_inflow_outflow,
    agent_scorecard,
    category_resolution_profile,
    csat_by_resolution_bucket,
    simulate_backlog,
    weekly_digest,
)
from engine.ui_layout import render_enterprise_navbar

st.set_page_config(
    page_title="RideOps | Executive Operations Command",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Render Institutional Top Navigation Bar ──────────────────────────
render_enterprise_navbar(active_page="command")

# ── Load Data ────────────────────────────────────────────────────────
df = load_tickets()

# ── Header & Executive Scope ─────────────────────────────────────────
st.markdown("## Executive Operations Command")
st.markdown(
    "<span style='color: #475569; font-size: 0.95rem;'>"
    "Operations leadership intelligence interface. "
    "Throughput analytics, capacity reclamation modeling, and personnel performance distribution."
    "</span>",
    unsafe_allow_html=True,
)
st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# ── 1. Weekly Inflow vs Outflow & Running Backlog ─────────────────────
st.markdown("### Throughput Dynamics: Inbound Volume vs. Outbound Resolution")
st.caption("Monitoring net accumulation of queue deficit across weekly reporting cycles.")

flow = weekly_inflow_outflow(df)

fig_flow = go.Figure()
fig_flow.add_trace(go.Bar(
    x=flow["week"],
    y=flow["inflow"],
    name="New Inbound Cases",
    marker_color="#1E40AF"  # Corporate Navy
))
fig_flow.add_trace(go.Bar(
    x=flow["week"],
    y=flow["outflow"],
    name="Resolved Closures",
    marker_color="#2563EB"  # Corporate Royal Blue
))
fig_flow.add_trace(go.Scatter(
    x=flow["week"],
    y=flow["running_backlog"],
    name="Cumulative Backlog Delta",
    mode="lines+markers",
    line=dict(color="#0F172A", width=2.5),  # Black/Charcoal line
    marker=dict(size=5, color="#0F172A"),
    yaxis="y2"
))

fig_flow.update_layout(
    height=360,
    margin=dict(t=20, b=30, l=40, r=40),
    legend=dict(orientation="h", y=-0.18, font=dict(color="#0F172A", size=11)),
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(family="Inter, sans-serif", color="#0F172A"),
    xaxis=dict(
        gridcolor="#F1F5F9",
        linecolor="#CBD5E1",
        title=dict(text="Weekly Period", font=dict(color="#334155", size=11)),
        tickfont=dict(color="#334155")
    ),
    yaxis=dict(
        gridcolor="#F1F5F9",
        linecolor="#CBD5E1",
        title=dict(text="Weekly Volume", font=dict(color="#334155", size=11)),
        tickfont=dict(color="#334155")
    ),
    yaxis2=dict(
        title=dict(text="Net Cumulative Backlog", font=dict(color="#0F172A", size=11)),
        overlaying="y",
        side="right",
        linecolor="#CBD5E1",
        tickfont=dict(color="#0F172A")
    ),
    barmode="group",
)
st.plotly_chart(fig_flow, use_container_width=True)

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ── 2. Scenario Simulation Engine ────────────────────────────────────
st.markdown("### Scenario Modeling: Capacity Reclamation from Waste Interception")
st.caption(
    "Quantifying the impact of intercepting non-bug escalations at frontline triage. "
    "Currently, 56.6% of escalated cases return as non-bugs, incurring a ~75-hour cycle time penalty."
)

col_sim1, col_sim2 = st.columns([1, 2])

with col_sim1:
    target_reduction = st.slider(
        "Wasteful Escalation Reduction Target (%):",
        min_value=0,
        max_value=100,
        value=40,
        step=5,
        format="%d%%"
    )

    wasteful_total = df["is_wasteful_esc"].sum()
    saved_tickets = int(wasteful_total * (target_reduction / 100))
    eng_hours_saved = saved_tickets * 75
    eng_months = round(eng_hours_saved / (13 * 40), 1)

    st.markdown(
        f"""
        <div class="institutional-card">
            <div class="institutional-card-header">PROJECTED CAPACITY RECLAIMED</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #0F172A; margin: 4px 0;">
                {saved_tickets} Cases
            </div>
            <div style="font-size: 0.82rem; color: #475569; margin-bottom: 12px;">
                Intercepted from unnecessary engineering queues
            </div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #1E40AF; margin: 4px 0;">
                ~{eng_hours_saved:,} Dev Hours
            </div>
            <div style="font-size: 0.82rem; color: #475569;">
                Equivalent to <strong>{eng_months} engineer-months</strong> of reclaimed deep product capacity.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_sim2:
    sim_df = simulate_backlog(df, target_reduction / 100)

    fig_sim = go.Figure()
    fig_sim.add_trace(go.Scatter(
        x=sim_df["week"],
        y=sim_df["running_backlog"],
        name="Historical Trajectory",
        line=dict(color="#DC2626", dash="dash", width=2)
    ))
    fig_sim.add_trace(go.Scatter(
        x=sim_df["week"],
        y=sim_df["improved_backlog"],
        name=f"Projected Trajectory ({target_reduction}% Waste Intercepted)",
        line=dict(color="#1D4ED8", width=3)
    ))
    fig_sim.update_layout(
        height=300,
        margin=dict(t=20, b=25, l=40, r=20),
        legend=dict(orientation="h", y=-0.22, font=dict(color="#0F172A", size=11)),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, sans-serif", color="#0F172A"),
        xaxis=dict(gridcolor="#F1F5F9", linecolor="#CBD5E1", tickfont=dict(color="#334155")),
        yaxis=dict(gridcolor="#F1F5F9", linecolor="#CBD5E1", title="Cumulative Backlog Count", tickfont=dict(color="#334155")),
    )
    st.plotly_chart(fig_sim, use_container_width=True)

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ── 3. Personnel Operational Distribution Matrix ─────────────────────
st.markdown("### Personnel Operational Distribution Matrix")
st.caption("Distribution analysis across assigned support personnel to identify procedural variances.")

sc = agent_scorecard(df)

def highlight_outliers(val):
    if isinstance(val, (int, float)):
        if val > 50:
            return "background-color: #FEF2F2; color: #B91C1C; font-weight: 600;"
        elif val > 20:
            return "background-color: #FFFBEB; color: #B45309; font-weight: 600;"
    return ""

st.dataframe(
    sc.style.applymap(highlight_outliers, subset=["escalation_rate", "reopen_rate"]),
    use_container_width=True,
    hide_index=True
)

st.markdown(
    """
    <div style="font-size: 0.82rem; color: #64748B; margin-top: 4px;">
        <strong>Diagnostic Note:</strong>
        Specialist Rahul T exhibits an escalation rate of 61.6% (75.3% of which return as non-bugs).
        Specialist Karan B demonstrates a 29.5% case reopen rate due to premature ticket resolution.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ── 4. Category Escalation & Resolution Profiling ─────────────────────
col_c1, col_c2 = st.columns(2)

with col_c1:
    st.markdown("### Category Escalation & Cycle Time")
    st.caption("Median resolution duration plotted against engineering escalation frequency.")
    cat_prof = category_resolution_profile(df)

    fig_cat = px.scatter(
        cat_prof,
        x="escalation_rate",
        y="median_resolution_hrs",
        size="tickets",
        color_discrete_sequence=["#1D4ED8"],
        hover_name="category",
        labels={
            "escalation_rate": "Escalation Rate (%)",
            "median_resolution_hrs": "Median Resolution (Hours)"
        }
    )
    fig_cat.update_layout(
        height=320,
        margin=dict(t=20, b=20, l=40, r=20),
        showlegend=False,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, sans-serif", color="#0F172A"),
        xaxis=dict(gridcolor="#F1F5F9", linecolor="#CBD5E1", tickfont=dict(color="#334155")),
        yaxis=dict(gridcolor="#F1F5F9", linecolor="#CBD5E1", tickfont=dict(color="#334155")),
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with col_c2:
    st.markdown("### CSAT Degradation by Duration")
    st.caption("Empirical relationship between resolution cycle time and customer satisfaction.")
    csat_buckets = csat_by_resolution_bucket(df)

    fig_csat = px.bar(
        csat_buckets,
        x="bucket",
        y="mean",
        labels={"bucket": "Resolution Window", "mean": "Mean CSAT (1-5)"},
        color_discrete_sequence=["#1E40AF"]
    )
    fig_csat.update_layout(
        height=320,
        margin=dict(t=20, b=20, l=40, r=20),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, sans-serif", color="#0F172A"),
        xaxis=dict(gridcolor="#F1F5F9", linecolor="#CBD5E1", tickfont=dict(color="#334155")),
        yaxis=dict(gridcolor="#F1F5F9", linecolor="#CBD5E1", range=[1, 5], tickfont=dict(color="#334155")),
    )
    st.plotly_chart(fig_csat, use_container_width=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ── 5. Executive Briefing Memorandum ─────────────────────────────────
st.markdown("### Weekly Operational Briefing Memorandum")
st.caption("Standardized executive report generated for distribution across Operations, Support, and Engineering.")

digest_text = weekly_digest(df)
st.text_area("Generated Executive Memorandum", digest_text, height=190)
st.download_button(
    "Export Executive Briefing (.txt)",
    digest_text,
    file_name="rideops_weekly_executive_briefing.txt",
    use_container_width=False,
)
