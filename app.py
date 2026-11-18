"""
app.py — RideOps Operations Intelligence Platform
Landing Page: Executive System Overview & Operational Health Metrics
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from engine.data_loader import load_tickets
from engine.metrics import (
    backlog_pressure_index,
    pressure_label,
)
from engine.ui_layout import render_enterprise_navbar

st.set_page_config(
    page_title="RideOps | Operations Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Render Institutional Top Navigation Bar ──────────────────────────
render_enterprise_navbar(active_page="overview")

# ── Load Dataset ─────────────────────────────────────────────────────
df = load_tickets()

# ── Header & Context ─────────────────────────────────────────────────
st.markdown("## System Health Overview")
st.markdown(
    "<span style='color: #475569; font-size: 0.95rem;'>"
    "Executive monitoring console for corporate employee transportation support operations. "
    "Data scope: 1,444 support records across 200 corporate clients."
    "</span>",
    unsafe_allow_html=True,
)
st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# ── Backlog Pressure Index (Composite Score) ─────────────────────────
bpi = backlog_pressure_index(df)
label, colour = pressure_label(bpi)

col_bpi, col_desc = st.columns([1, 2])

with col_bpi:
    st.markdown(
        f"""
        <div class="institutional-card">
            <div class="institutional-card-header">BACKLOG PRESSURE INDEX (BPI)</div>
            <div style="font-size: 2.2rem; font-weight: 800; color: #0F172A; margin: 4px 0 8px 0;">
                {bpi} <span style="font-size: 1rem; color: #64748B; font-weight: 500;">/ 100</span>
            </div>
            <div>
                <span class="{'badge-normal' if bpi < 30 else ('badge-elevated' if bpi < 60 else 'badge-critical')}">
                    STATUS: {label}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_desc:
    st.markdown(
        """
        <div class="institutional-card">
            <div class="institutional-card-header">DIAGNOSTIC CRITERIA & THRESHOLDS</div>
            <table style="width: 100%; font-size: 0.85rem; border-collapse: collapse; margin-top: 4px;">
                <thead>
                    <tr style="border-bottom: 1px solid #E2E8F0; text-align: left; color: #475569;">
                        <th style="padding: 4px 8px;">Index Score</th>
                        <th style="padding: 4px 8px;">Operating State</th>
                        <th style="padding: 4px 8px;">Prescribed Operational Action</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1px solid #F1F5F9;">
                        <td style="padding: 4px 8px; font-weight: 600;">0 – 30</td>
                        <td style="padding: 4px 8px; color: #047857; font-weight: 600;">NORMAL</td>
                        <td style="padding: 4px 8px; color: #334155;">Routine operations; queue throughput exceeds intake.</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #F1F5F9;">
                        <td style="padding: 4px 8px; font-weight: 600;">31 – 60</td>
                        <td style="padding: 4px 8px; color: #B45309; font-weight: 600;">ELEVATED</td>
                        <td style="padding: 4px 8px; color: #334155;">Inflow exceeds capacity; triage guardrails recommended.</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px 8px; font-weight: 600;">61 – 100</td>
                        <td style="padding: 4px 8px; color: #B91C1C; font-weight: 600;">CRITICAL</td>
                        <td style="padding: 4px 8px; color: #334155;">SLA breach imminent; mandatory escalation gating required.</td>
                    </tr>
                </tbody>
            </table>
            <div style="font-size: 0.75rem; color: #64748B; margin-top: 8px;">
                * Index aggregates open queue ratio, inflow acceleration, mean ticket age, and wasteful escalation rates.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# ── Core Key Performance Indicators ──────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)

total_records = len(df)
active_open = int(df["is_open"].sum())
median_resolution = df["resolution_hrs"].median()
mean_csat = df["csat_score"].mean()
waste_escalation_pct = df[df["is_escalated"]]["is_wasteful_esc"].mean() * 100

c1.metric("Total Inbound Tickets", f"{total_records:,}")
c2.metric("Active Open Backlog", f"{active_open}")
c3.metric("Median Resolution", f"{median_resolution:.0f} hrs")
c4.metric("Mean CSAT Rating", f"{mean_csat:.2f} / 5.0")
c5.metric("Wasteful Escalation Rate", f"{waste_escalation_pct:.0f}%")

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ── Monthly Throughput & Volume Trajectory Chart ─────────────────────
st.markdown("### Monthly Intake & Resolution Profile")
st.caption("Temporal comparison of total intake, escalated tickets, and client reopen rates.")

monthly = df.groupby("created_month").agg(
    tickets=("ticket_id", "count"),
    escalated=("is_escalated", "sum"),
    reopened=("is_reopened", "sum"),
).reset_index()
monthly.columns = ["Month", "Total Volume", "Escalated to Engineering", "Reopened Cases"]

fig = go.Figure()
fig.add_trace(go.Bar(
    x=monthly["Month"],
    y=monthly["Total Volume"],
    name="Total Intake",
    marker_color="#1E40AF"  # Corporate Navy
))
fig.add_trace(go.Bar(
    x=monthly["Month"],
    y=monthly["Escalated to Engineering"],
    name="Escalated to Engineering",
    marker_color="#2563EB"  # Corporate Royal Blue
))
fig.add_trace(go.Bar(
    x=monthly["Month"],
    y=monthly["Reopened Cases"],
    name="Reopened Cases",
    marker_color="#94A3B8"  # Slate Gray
))

fig.update_layout(
    barmode="group",
    height=340,
    margin=dict(t=20, b=30, l=40, r=20),
    legend=dict(orientation="h", y=-0.18, font=dict(color="#0F172A", size=11)),
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(family="Inter, sans-serif", color="#0F172A"),
    xaxis=dict(
        gridcolor="#F1F5F9",
        linecolor="#CBD5E1",
        tickfont=dict(color="#334155")
    ),
    yaxis=dict(
        gridcolor="#F1F5F9",
        linecolor="#CBD5E1",
        title=dict(text="Ticket Volume", font=dict(color="#334155", size=12)),
        tickfont=dict(color="#334155")
    ),
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ── Operations Pipeline Model (Factory Floor Framework) ───────────────
st.markdown("### Operations Pipeline Architecture: Support as a Factory Floor")
st.caption("Applying Theory of Constraints to eliminate structural waste across the customer resolution lifecycle.")

st.markdown(
    """
    <div class="institutional-card">
        <div class="institutional-card-header">THEORY OF CONSTRAINTS MAPPING</div>
        <table style="width: 100%; font-size: 0.82rem; border-collapse: collapse; margin-top: 6px;">
            <thead>
                <tr style="border-bottom: 1px solid #E2E8F0; text-align: left; color: #475569;">
                    <th style="padding: 6px 8px;">Factory Concept</th>
                    <th style="padding: 6px 8px;">Support Operation Equivalent</th>
                    <th style="padding: 6px 8px;">Empirical Baseline</th>
                    <th style="padding: 6px 8px;">System Intervention & Tool Capability</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid #F1F5F9;">
                    <td style="padding: 6px 8px; font-weight: 600; color: #1E40AF;">Throughput</td>
                    <td style="padding: 6px 8px;">Weekly Resolved Volume</td>
                    <td style="padding: 6px 8px;">17.1 cases/agent/wk (Capacity limit)</td>
                    <td style="padding: 6px 8px;">Weekly Inflow vs. Outflow Dynamics (Ops Command)</td>
                </tr>
                <tr style="border-bottom: 1px solid #F1F5F9;">
                    <td style="padding: 6px 8px; font-weight: 600; color: #1E40AF;">Cycle Time</td>
                    <td style="padding: 6px 8px;">End-to-End Resolution Hours</td>
                    <td style="padding: 6px 8px;">12.6h (L1) vs. 86.8h (Engineering)</td>
                    <td style="padding: 6px 8px;">Escalation Payoff Forecasting & Benchmark Comparison</td>
                </tr>
                <tr style="border-bottom: 1px solid #F1F5F9;">
                    <td style="padding: 6px 8px; font-weight: 600; color: #1E40AF;">Rework</td>
                    <td style="padding: 6px 8px;">Client Case Reopen Frequency</td>
                    <td style="padding: 6px 8px;">11.5% overall (Karan B: 29.5%, CSAT 2.0)</td>
                    <td style="padding: 6px 8px;">Premature Closure Auditing & 48h Verification Window</td>
                </tr>
                <tr style="border-bottom: 1px solid #F1F5F9;">
                    <td style="padding: 6px 8px; font-weight: 600; color: #1E40AF;">Defect Rate</td>
                    <td style="padding: 6px 8px;">Wasteful Escalation Rate</td>
                    <td style="padding: 6px 8px;">56.6% rejected/non-bugs (275 cases)</td>
                    <td style="padding: 6px 8px;">TF-IDF Precedent Playbooks & Risk Index</td>
                </tr>
                <tr style="border-bottom: 1px solid #F1F5F9;">
                    <td style="padding: 6px 8px; font-weight: 600; color: #1E40AF;">Bottleneck</td>
                    <td style="padding: 6px 8px;">L1-to-Engineering Handoff</td>
                    <td style="padding: 6px 8px;">229 ping-pong cases (128.5 hrs median)</td>
                    <td style="padding: 6px 8px;">Mandatory Pre-Escalation Diagnostic Checklists</td>
                </tr>
                <tr>
                    <td style="padding: 6px 8px; font-weight: 600; color: #1E40AF;">Root Cause</td>
                    <td style="padding: 6px 8px;">Platform Code Defects</td>
                    <td style="padding: 6px 8px;">183 cases from 3 roster defects (13%)</td>
                    <td style="padding: 6px 8px;">Two-Pass NLP Clustering & Jira Spec Generator</td>
                </tr>
            </tbody>
        </table>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ── Primary Systems Directory ─────────────────────────────────────────
st.markdown("### Functional Workspaces")
st.caption("Access role-specific intelligence and execution interfaces.")

mod1, mod2, mod3 = st.columns(3)

with mod1:
    st.markdown(
        """
        <div class="institutional-card">
            <div class="institutional-card-header">FRONTLINE RESOLUTION CONSOLE</div>
            <div style="font-size: 0.92rem; font-weight: 600; color: #0F172A; margin: 4px 0 8px 0;">
                L1 Support Agent Interface
            </div>
            <p style="font-size: 0.82rem; color: #475569; line-height: 1.4; margin-bottom: 12px;">
                Precedent case analysis, historical resolution matching, escalation payoff forecasting,
                and category diagnostic checklists.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Agent_Cockpit.py", label="Open Agent Console →", use_container_width=True)

with mod2:
    st.markdown(
        """
        <div class="institutional-card">
            <div class="institutional-card-header">EXECUTIVE OPERATIONS COMMAND</div>
            <div style="font-size: 0.92rem; font-weight: 600; color: #0F172A; margin: 4px 0 8px 0;">
                Operations Leadership Interface
            </div>
            <p style="font-size: 0.82rem; color: #475569; line-height: 1.4; margin-bottom: 12px;">
                Throughput dynamics, personnel performance distribution, scenario simulation modeling,
                and automated executive memorandum generation.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/2_Ops_Command.py", label="Open Operations Command →", use_container_width=True)

with mod3:
    st.markdown(
        """
        <div class="institutional-card">
            <div class="institutional-card-header">SYSTEMIC DEFECT RADAR</div>
            <div style="font-size: 0.92rem; font-weight: 600; color: #0F172A; margin: 4px 0 8px 0;">
                Product & Quality Assurance Interface
            </div>
            <p style="font-size: 0.82rem; color: #475569; line-height: 1.4; margin-bottom: 12px;">
                Two-pass cluster identification of upstream software defects, client impact quantification,
                and production engineering specifications.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/3_Bug_Radar.py", label="Open Defect Radar →", use_container_width=True)
