"""
app.py — The Second Desk | Why the Backlog Grows
Landing page: Little's Law decomposition + the two-loop finding + system KPIs.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from engine.data_loader import load_tickets
from engine.metrics import (
    backlog_pressure_index,
    pressure_label,
    decompose_backlog_growth,
)
from engine.ui_layout import render_enterprise_navbar

st.set_page_config(
    page_title="RideOps | The Second Desk",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_enterprise_navbar(active_page="overview")

df = load_tickets()

# ── Header ────────────────────────────────────────────────────────────
st.markdown("## Why the Backlog Grows")
st.markdown(
    "<span style='color: #475569; font-size: 0.95rem;'>"
    "The support team is a rework factory with two broken decisions: "
    "'escalate' and 'close'. This page decomposes the backlog with Little's Law."
    "</span>",
    unsafe_allow_html=True,
)
st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# ── Little's Law decomposition ────────────────────────────────────────
dec = decompose_backlog_growth(df)

st.markdown("### Little's Law: Open = Arrival Rate × Cycle Time")
st.caption("Backlog (L) grows because inflow (λ) rose and cycle time (W) inflated — but only one is fixable without hiring.")

ll1, ll2, ll3 = st.columns(3)
ll1.metric("Arrival Rate (λ)", f"{dec['lambda_jul']} → {dec['lambda_sep']} /mo", delta="+51.8% demand")
ll2.metric("Median Cycle Time (W)", f"{dec['w_jul']:.0f}h → {dec['w_sep']:.0f}h", delta="inflated by rework")
ll3.metric("Implied Backlog (L = λ·W)", f"{dec['l_jul']:.0f} → {dec['l_sep']:.0f}")

st.markdown(
    f"""
    <div class="institutional-card">
        <div class="institutional-card-header">BACKLOG GROWTH DECOMPOSITION</div>
        <div style="font-size: 0.85rem; color: #1E293B; line-height: 1.6;">
            Growth from <strong>inflow</strong> (W·Δλ): <strong>{dec['from_inflow']:,.0f}</strong><br>
            Growth from <strong>cycle time</strong> (λ·ΔW): <strong>{dec['from_cycle']:,.0f}</strong><br>
            Interaction term (Δλ·ΔW): <strong>{dec['from_interaction']:,.0f}</strong><br>
            <span style="color: #64748B; font-size: 0.8rem;">
                Inflow is a hiring problem (off the table). Cycle time is the controllable lever —
                it is inflated by two rework loops, not one.
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── The two-loop finding ──────────────────────────────────────────────
st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
st.markdown("### The Hidden Second Loop")
loop1, loop2 = st.columns(2)

with loop1:
    st.markdown(
        """
        <div class="institutional-card" style="border-left: 4px solid #B45309;">
            <div class="institutional-card-header">LOOP 1 — ESCALATION (VISIBLE)</div>
            <div style="font-size: 0.85rem; color: #1E293B; line-height: 1.6;">
                56.6% of escalations (275/486) come back as non-bugs.<br>
                229 tickets ping-pong 2+ times at a <strong>128.5h</strong> median.<br>
                Escalated = <strong>86.8h</strong> vs L1 = <strong>12.6h</strong> (7× slower).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with loop2:
    st.markdown(
        """
        <div class="institutional-card" style="border-left: 4px solid #B91C1C;">
            <div class="institutional-card-header">LOOP 2 — REOPEN (NOBODY NAMED IT)</div>
            <div style="font-size: 0.85rem; color: #1E293B; line-height: 1.6;">
                11.5% of tickets reopen after closure.<br>
                Karan B closes <strong>29.5%</strong> too early at <strong>CSAT 2.0</strong>.<br>
                Meera blames engineering, Sandeep blames L1 — neither names premature closure.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ── Backlog Pressure Index (kept as a headline health read) ───────────
bpi = backlog_pressure_index(df)
label, colour = pressure_label(bpi)

st.markdown("### System Health")
c_bpi, c_kpi = st.columns([1, 3])

with c_bpi:
    st.markdown(
        f"""
        <div class="institutional-card">
            <div class="institutional-card-header">BACKLOG PRESSURE</div>
            <div style="font-size: 2rem; font-weight: 800; color: #0F172A;">{bpi} / 100</div>
            <span class="{'badge-normal' if bpi < 30 else ('badge-elevated' if bpi < 60 else 'badge-critical')}">
                {label}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c_kpi:
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Tickets", f"{len(df):,}")
    k2.metric("Open Backlog", f"{int(df['is_open'].sum())}")
    k3.metric("Median Resolution", f"{df['resolution_hrs'].median():.0f} hrs")
    k4.metric("Mean CSAT", f"{df['csat_score'].mean():.2f} / 5")

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ── Monthly volume trajectory ─────────────────────────────────────────
st.markdown("### Monthly Intake & Resolution")
monthly = df.groupby("created_month").agg(
    tickets=("ticket_id", "count"),
    escalated=("is_escalated", "sum"),
    reopened=("is_reopened", "sum"),
).reset_index()
monthly.columns = ["Month", "Total Volume", "Escalated", "Reopened"]

fig = go.Figure()
fig.add_trace(go.Bar(x=monthly["Month"], y=monthly["Total Volume"], name="Total Intake", marker_color="#1E40AF"))
fig.add_trace(go.Bar(x=monthly["Month"], y=monthly["Escalated"], name="Escalated", marker_color="#2563EB"))
fig.add_trace(go.Bar(x=monthly["Month"], y=monthly["Reopened"], name="Reopened", marker_color="#94A3B8"))
fig.update_layout(
    barmode="group",
    height=320,
    margin=dict(t=20, b=30, l=40, r=20),
    legend=dict(orientation="h", y=-0.18, font=dict(color="#0F172A", size=11)),
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(family="Inter, sans-serif", color="#0F172A"),
    xaxis=dict(gridcolor="#F1F5F9", linecolor="#CBD5E1", tickfont=dict(color="#334155")),
    yaxis=dict(gridcolor="#F1F5F9", linecolor="#CBD5E1", tickfont=dict(color="#334155")),
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ── Workspaces ────────────────────────────────────────────────────────
st.markdown("### Functional Workspaces")

w1, w2, w3 = st.columns(3)
with w1:
    st.markdown(
        """
        <div class="institutional-card">
            <div class="institutional-card-header">THE SECOND DESK</div>
            <div style="font-size: 0.92rem; font-weight: 600; color: #0F172A;">L1 Decision Gate</div>
            <p style="font-size: 0.82rem; color: #475569;">Escalation gate + closure gate + known-defect short-circuit.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Agent_Cockpit.py", label="Open The Second Desk →", use_container_width=True)

with w2:
    st.markdown(
        """
        <div class="institutional-card">
            <div class="institutional-card-header">OPS COMMAND</div>
            <div style="font-size: 0.92rem; font-weight: 600; color: #0F172A;">Ritika · Weekly KPIs</div>
            <p style="font-size: 0.82rem; color: #475569;">Throughput, burn-down projection, agent heatmap.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/2_Ops_Command.py", label="Open Ops Command →", use_container_width=True)

with w3:
    st.markdown(
        """
        <div class="institutional-card">
            <div class="institutional-card-header">DEFECT RADAR</div>
            <div style="font-size: 0.92rem; font-weight: 600; color: #0F172A;">Sandeep · Upstream Bugs</div>
            <p style="font-size: 0.82rem; color: #475569;">Recurring defects feeding the short-circuit.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/3_Bug_Radar.py", label="Open Defect Radar →", use_container_width=True)
