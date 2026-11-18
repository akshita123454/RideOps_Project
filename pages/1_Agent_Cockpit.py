"""
1_Agent_Cockpit.py — Frontline Resolution Console
Support Triage, Precedent Analysis, Escalation Gating, and Verification Protocols
"""

import streamlit as st
import pandas as pd
from engine.data_loader import load_tickets, ESCALATION_CHECKLISTS
from engine.ticket_dna import TicketDNA
from engine.bug_cluster import find_bug_clusters
from engine.metrics import agent_scorecard, agent_monthly_trend
from engine.ui_layout import render_enterprise_navbar

st.set_page_config(
    page_title="RideOps | Frontline Resolution Console",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Render Institutional Top Navigation Bar ──────────────────────────
render_enterprise_navbar(active_page="cockpit")

# ── Load Data & Precedent Engine ─────────────────────────────────────
df = load_tickets()

@st.cache_resource
def build_dna():
    return TicketDNA(df)

dna = build_dna()

@st.cache_data
def get_known_defect_clusters():
    return find_bug_clusters(df, min_cluster_size=6, similarity_threshold=0.75)

defect_clusters = get_known_defect_clusters()

# ── Header & Persona Context ─────────────────────────────────────────
st.markdown("## Frontline Resolution Console")
st.markdown(
    "<span style='color: #475569; font-size: 0.95rem;'>"
    "Triage workspace for frontline support specialists. "
    "Features precedent case retrieval, escalation risk modeling, known defect interception, and mandatory diagnostic gating."
    "</span>",
    unsafe_allow_html=True,
)
st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# ── Specialist Selection ─────────────────────────────────────────────
agents = sorted(df["assigned_agent"].unique())
selected_agent = st.selectbox("Select Active Support Specialist:", agents)

agent_df = df[df["assigned_agent"] == selected_agent]

# ── Operational Performance Scorecard ────────────────────────────────
st.markdown("### Operational Performance Scorecard")

sc = agent_scorecard(df)
me = sc[sc["agent"] == selected_agent].iloc[0]

m1, m2, m3, m4, m5 = st.columns(5)

def _metric(col, label, val, fmt, team_val, invert=False):
    delta = val - team_val
    direction = "inverse" if invert else "normal"
    col.metric(label, fmt.format(val), delta=f"{delta:+.1f} vs team baseline", delta_color=direction)

team_esc = round(sc["escalation_rate"].mean(), 1)
team_reopen = round(sc["reopen_rate"].mean(), 1)
team_frt = round(sc["median_frt_min"].median(), 0)
team_res = round(sc["median_resolution_hrs"].median(), 1)
team_csat = round(sc["avg_csat"].mean(), 2)

_metric(m1, "Escalation Rate", me["escalation_rate"], "{:.1f}%", team_esc, invert=True)
_metric(m2, "Case Reopen Rate", me["reopen_rate"], "{:.1f}%", team_reopen, invert=True)
_metric(m3, "Median Initial Response", me["median_frt_min"] or 0, "{:.0f} min", team_frt, invert=True)
_metric(m4, "Median Resolution", me["median_resolution_hrs"] or 0, "{:.1f} hrs", team_res, invert=True)
_metric(m5, "Client CSAT Rating", me["avg_csat"] or 0, "{:.2f} / 5", team_csat, invert=False)

# Monthly Trend Breakdown
trend = agent_monthly_trend(df, selected_agent)
if len(trend) > 1:
    with st.expander("Monthly Performance Trajectory"):
        st.dataframe(trend, use_container_width=True, hide_index=True)

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ── Active Queue & Diagnostic Protocol ────────────────────────────────
st.markdown("### Active Assigned Queue")

open_tickets = agent_df[agent_df["is_open"]].sort_values("created_at")

if open_tickets.empty:
    st.info("Queue is clear: No pending unresolved cases currently assigned to this specialist.")
else:
    st.markdown(
        f"<span style='font-size: 0.88rem; color: #1E40AF; font-weight: 600;'>"
        f"Assigned Pending Cases: {len(open_tickets)}"
        f"</span>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    for _, ticket in open_tickets.iterrows():
        idx = ticket.name
        tid = ticket["ticket_id"]
        cat = ticket["category"]
        prio = ticket["priority"]
        desc = ticket["description"]
        status = ticket["status"]

        with st.expander(f"{tid} | Priority: {prio} | Category: {cat} — {desc}"):
            # ── Check for Known Defect Match ─────────────────────────
            matched_defect = None
            for c in defect_clusters:
                if c["description"].lower() in desc.lower() or desc.lower() in c["description"].lower():
                    matched_defect = c
                    break

            if matched_defect:
                st.markdown(
                    f"""
                    <div class="institutional-card" style="border-left: 4px solid #B91C1C; background: #FEF2F2; padding: 12px 16px; margin-bottom: 12px;">
                        <div style="font-weight: 700; color: #B91C1C; font-size: 0.85rem;">
                            CRITICAL: IDENTIFIED RECURRING PRODUCT DEFECT MATCH
                        </div>
                        <div style="font-size: 0.82rem; color: #7F1D1D; margin-top: 4px; line-height: 1.5;">
                            This ticket matches verified system defect: <strong>{matched_defect['description']}</strong> 
                            ({matched_defect['ticket_count']} historical instances recorded across {matched_defect['affected_clients']} enterprise accounts).<br>
                            <strong>Operational Protocol:</strong> <u>DO NOT ESCALATE TO ENGINEERING</u>. 
                            Engineering patch is currently scheduled. Provide the approved client workaround (Admin manual roster cache purge) and log as known issue.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            tc1, tc2 = st.columns([2, 1])

            with tc1:
                st.markdown(
                    f"""
                    <div style="font-size: 0.88rem; line-height: 1.6; color: #1E293B;">
                        <strong>Corporate Account:</strong> {ticket['client_name']} ({ticket['client_tier']})<br>
                        <strong>Inbound Channel:</strong> {ticket['channel']} &nbsp;|&nbsp; <strong>Current State:</strong> {status}<br>
                        <strong>Logged Timestamp:</strong> {ticket['created_at'].strftime('%Y-%m-%d %H:%M IST')}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # ── Escalation Payoff & Risk Calculator ───────────────────
            with tc2:
                waste_prob, similar = dna.escalation_risk(idx, top_k=15)
                risk_pct = round(waste_prob * 100)

                if risk_pct >= 50:
                    badge_class = "badge-critical"
                    badge_text = "HIGH RISK OF REJECTION"
                elif risk_pct >= 25:
                    badge_class = "badge-elevated"
                    badge_text = "MODERATE REJECTION RISK"
                else:
                    badge_class = "badge-normal"
                    badge_text = "LOW RISK OF REJECTION"

                esc_time = df[df["is_escalated"]]["resolution_hrs"].median()
                l1_time = df[~df["is_escalated"]]["resolution_hrs"].median()

                st.markdown(
                    f"""
                    <div class="institutional-card" style="padding: 12px; margin-bottom: 0;">
                        <div class="institutional-card-header">ESCALATION RISK INDEX</div>
                        <div style="font-size: 1.6rem; font-weight: 800; color: #0F172A;">
                            {risk_pct}%
                        </div>
                        <div style="margin: 4px 0 8px 0;">
                            <span class="{badge_class}">{badge_text}</span>
                        </div>
                        <div style="font-size: 0.76rem; color: #475569; border-top: 1px solid #E2E8F0; padding-top: 6px;">
                            <strong>Expected Cycle Time:</strong><br>
                            If Escalated to Eng: <strong>~{esc_time:.0f} hrs</strong><br>
                            If Handled Internally: <strong>~{l1_time:.0f} hrs</strong>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # ── Precedent Case Retrieval ─────────────────────────────
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            st.markdown("#### Precedent Case Analysis (Historical Resolutions)")
            similar_tickets = dna.find_similar(idx, top_k=5)

            if similar_tickets:
                for i, s in enumerate(similar_tickets, 1):
                    if not s["was_escalated"]:
                        tag = "<span class='badge-normal'>RESOLVED AT L1</span>"
                    elif s["was_wasteful"]:
                        tag = "<span class='badge-elevated'>ESCALATION REJECTED (NON-BUG)</span>"
                    else:
                        tag = "<span style='padding: 2px 6px; font-size: 0.72rem; font-weight: 700; color: #1E40AF; background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 4px;'>ESCALATED & CODE-PATCHED</span>"

                    res_hrs = f" &nbsp;|&nbsp; Duration: {s['resolution_hrs']:.0f} hrs" if s["resolution_hrs"] else ""

                    st.markdown(
                        f"""
                        <div style="border-left: 3px solid #1D4ED8; padding: 6px 12px; background: #F8FAFC; margin-bottom: 6px; font-size: 0.84rem;">
                            <strong>Case #{i}:</strong> <code>{s['ticket_id']}</code> — {s['description']}<br>
                            Outcome: {tag} &nbsp;|&nbsp; Match Confidence: <strong>{s['similarity']:.0%}</strong>{res_hrs}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No statistically significant precedent cases detected in historical archive.")

            # ── Pre-Escalation Diagnostic Protocol Checklist ─────────
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            st.markdown("#### Mandatory Diagnostic Verification Protocol")
            checklist = ESCALATION_CHECKLISTS.get(cat, [])
            all_verified = True
            if checklist:
                for item in checklist:
                    checked = st.checkbox(f"[VERIFIED] {item}", key=f"{tid}_{item[:30]}")
                    if not checked:
                        all_verified = False
            else:
                st.caption("Standard operational verification checklist not specified for this category.")

            # ── Action Execution Console (Decision-Action Gating) ───
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            st.markdown("#### Operational Action Dispatch")
            act_col1, act_col2 = st.columns(2)

            with act_col1:
                if st.button("Execute L1 Resolution (Close Case)", key=f"btn_res_{tid}", use_container_width=True):
                    st.success(f"Case {tid} successfully resolved via standard frontline protocol. Duration logged: 12 minutes. Backlog reduced.")

            with act_col2:
                if all_verified:
                    if st.button("Submit Escalation to Engineering", key=f"btn_esc_{tid}", use_container_width=True):
                        st.warning(f"Case {tid} escalated to Engineering queue with verified diagnostic audit attached.")
                else:
                    st.button("Escalate to Engineering (Locked: Complete Checklist First)", key=f"btn_lock_{tid}", disabled=True, use_container_width=True)
                    st.caption("<span style='color: #B91C1C; font-size: 0.75rem;'>* Escalation is gated until all diagnostic protocol checks are verified.</span>", unsafe_allow_html=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ── Historical Case Log ──────────────────────────────────────────────
with st.expander("Historical Resolved Cases Log (Recent 30 Records)"):
    closed = agent_df[~agent_df["is_open"]].sort_values("final_closed_at", ascending=False).head(30)
    display_cols = [
        "ticket_id", "category", "priority", "description",
        "escalated_to_eng", "eng_outcome", "resolution_hrs",
        "reopen_count", "csat_score",
    ]
    st.dataframe(
        closed[display_cols],
        use_container_width=True,
        hide_index=True,
    )
