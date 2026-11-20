"""
1_Agent_Cockpit.py — The Second Desk
L1 decision gate: escalation risk + closure risk + known-defect short-circuit.
"""

import streamlit as st
import pandas as pd

from engine.data_loader import load_tickets, ESCALATION_CHECKLISTS
from engine.ticket_dna import TicketDNA
from engine.bug_cluster import find_bug_clusters
from engine.metrics import agent_scorecard, agent_monthly_trend
from engine.decision_gate import (
    escalation_risk,
    closure_risk,
    category_waste_base_rates,
    category_reopen_base_rates,
)
from engine.ui_layout import render_enterprise_navbar

st.set_page_config(
    page_title="RideOps | The Second Desk",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_enterprise_navbar(active_page="cockpit")

df = load_tickets()


@st.cache_resource
def build_dna():
    return TicketDNA(df)


dna = build_dna()


@st.cache_data
def get_known_defect_clusters():
    return find_bug_clusters(df, min_cluster_size=6, similarity_threshold=0.75)


defect_clusters = get_known_defect_clusters()


@st.cache_data
def get_base_rates():
    return category_waste_base_rates(df), category_reopen_base_rates(df)


waste_rates, reopen_rates = get_base_rates()


def _badge(risk: float) -> str:
    if risk >= 0.5:
        return "badge-critical"
    if risk >= 0.3:
        return "badge-elevated"
    return "badge-normal"


# ── Header ────────────────────────────────────────────────────────────
st.markdown("## The Second Desk")
st.markdown(
    "<span style='color: #475569; font-size: 0.95rem;'>"
    "A decision gate for frontline specialists. Before you escalate or close, "
    "the desk shows the probability the decision will bounce back — and why."
    "</span>",
    unsafe_allow_html=True,
)
st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

agents = sorted(df["assigned_agent"].unique())
selected_agent = st.selectbox("Select Active Support Specialist:", agents)
agent_df = df[df["assigned_agent"] == selected_agent]

# ── Decision track record (reframed scorecard) ────────────────────────
st.markdown("### Your Decision Track Record")
sc = agent_scorecard(df)
me = sc[sc["agent"] == selected_agent].iloc[0]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Escalation Rate", f"{me['escalation_rate']:.1f}%")
m2.metric("Wasteful Escalation Rate", f"{me['wasteful_esc_rate']:.1f}%")
m3.metric("Reopen Rate", f"{me['reopen_rate']:.1f}%")
m4.metric("Avg CSAT", f"{me['avg_csat']:.2f}" if pd.notna(me["avg_csat"]) else "N/A")

trend = agent_monthly_trend(df, selected_agent)
if len(trend) > 1:
    with st.expander("Monthly Decision Trajectory"):
        st.dataframe(trend, use_container_width=True, hide_index=True)

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ── Open queue with two gates ─────────────────────────────────────────
st.markdown("### Active Queue — Gate Each Decision")
open_tickets = agent_df[agent_df["is_open"]].sort_values("created_at")

if open_tickets.empty:
    st.info("Queue is clear: no pending cases assigned to this specialist.")
else:
    st.markdown(
        f"<span style='font-size: 0.88rem; color: #1E40AF; font-weight: 600;'>"
        f"Assigned pending cases: {len(open_tickets)}"
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

        with st.expander(f"{tid} | {prio} | {cat} — {desc}"):

            # 1. Known-defect short-circuit (reuses clustering engine)
            matched = None
            for c in defect_clusters:
                if c["description"].lower() in desc.lower() or desc.lower() in c["description"].lower():
                    matched = c
                    break

            blocked_by_defect = matched is not None
            if blocked_by_defect:
                st.markdown(
                    f"""
                    <div class="institutional-card" style="border-left: 4px solid #B91C1C; background: #FEF2F2; padding: 12px 16px; margin-bottom: 12px;">
                        <div style="font-weight: 700; color: #B91C1C; font-size: 0.85rem;">
                            KNOWN DEFECT — DO NOT ESCALATE
                        </div>
                        <div style="font-size: 0.82rem; color: #7F1D1D; margin-top: 4px; line-height: 1.5;">
                            Matches recurring defect <strong>{matched['description']}</strong> —
                            {matched['ticket_count']} instances across {matched['affected_clients']} accounts.
                            Apply the approved client workaround and log as a known issue.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            esc = escalation_risk(df, ticket, dna, waste_rates)
            clo = closure_risk(df, ticket, reopen_rates)

            g1, g2 = st.columns(2)

            with g1:
                esc_pct = round(esc["risk"] * 100)
                st.markdown(
                    f"""
                    <div class="institutional-card" style="padding: 12px 16px;">
                        <div class="institutional-card-header">ESCALATION GATE</div>
                        <div style="font-size: 1.5rem; font-weight: 800; color: #0F172A;">{esc_pct}%</div>
                        <div style="margin: 2px 0 6px 0;">
                            <span class="{_badge(esc['risk'])}">bounce-back risk</span>
                        </div>
                        <div style="font-size: 0.82rem; color: #1E293B; font-weight: 600;">
                            {esc['recommendation']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with g2:
                clo_pct = round(clo["risk"] * 100)
                st.markdown(
                    f"""
                    <div class="institutional-card" style="padding: 12px 16px;">
                        <div class="institutional-card-header">CLOSURE GATE</div>
                        <div style="font-size: 1.5rem; font-weight: 800; color: #0F172A;">{clo_pct}%</div>
                        <div style="margin: 2px 0 6px 0;">
                            <span class="{_badge(clo['risk'])}">reopen risk</span>
                        </div>
                        <div style="font-size: 0.82rem; color: #1E293B; font-weight: 600;">
                            {clo['recommendation']}
                        </div>
                        <div style="font-size: 0.76rem; color: #64748B; margin-top: 4px;">
                            Your reopen rate: {round(clo['agent_reopen_rate'] * 100, 1)}%
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Evidence (why the gate says what it says)
            if esc["evidence"]:
                st.markdown("#### Evidence from past tickets")
                for i, s in enumerate(esc["evidence"], 1):
                    if s["was_wasteful"]:
                        tag = "<span class='badge-elevated'>ESCALATED & BOUNCED (NON-BUG)</span>"
                    elif s["was_escalated"]:
                        tag = "<span style='padding: 2px 6px; font-size: 0.72rem; font-weight: 700; color: #1E40AF; background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 4px;'>ESCALATED & PATCHED</span>"
                    else:
                        tag = "<span class='badge-normal'>RESOLVED AT L1</span>"

                    res_hrs = f" · {s['resolution_hrs']:.0f} hrs" if s.get("resolution_hrs") else ""

                    st.markdown(
                        f"""
                        <div style="border-left: 3px solid #1D4ED8; padding: 6px 12px; background: #F8FAFC; margin-bottom: 6px; font-size: 0.84rem;">
                            <strong>#{i}</strong> <code>{s['ticket_id']}</code> — {s['description']}<br>
                            {tag} &nbsp;|&nbsp; match {s['similarity']:.0%}{res_hrs}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # Checklist as evidence to lower risk (not the gate itself)
            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            with st.expander("Diagnostic checklist (evidence to lower risk)"):
                checklist = ESCALATION_CHECKLISTS.get(cat, [])
                if checklist:
                    for item in checklist:
                        st.checkbox(f"[VERIFIED] {item}", key=f"{tid}_{item[:30]}")
                else:
                    st.caption("No category checklist defined.")

            # Action buttons gated by risk
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            st.markdown("#### Decision")
            ac1, ac2 = st.columns(2)

            with ac1:
                close_blocked = clo["risk"] >= 0.25
                if st.button("Resolve at L1 (Close)", key=f"btn_res_{tid}", use_container_width=True, disabled=close_blocked):
                    st.success(f"Case {tid} resolved at L1. Backlog reduced.")
                if close_blocked:
                    st.caption("[DECISION GATE ALERT] Reopen risk too high — hold 48h before closing.")

            with ac2:
                esc_blocked = esc["risk"] >= 0.5 or blocked_by_defect
                if st.button("Escalate to Engineering", key=f"btn_esc_{tid}", use_container_width=True, disabled=esc_blocked):
                    st.warning(f"Case {tid} escalated with verified diagnostic evidence attached.")
                if blocked_by_defect:
                    st.caption("[DECISION GATE ALERT] Known platform defect — do not escalate, apply client workaround.")
                elif esc["risk"] >= 0.5:
                    st.caption("[DECISION GATE ALERT] Escalation likely to bounce back (non-bug) — resolve at L1 first.")

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ── Historical log ────────────────────────────────────────────────────
with st.expander("Historical Resolved Cases Log (Recent 30)"):
    closed = agent_df[~agent_df["is_open"]].sort_values("final_closed_at", ascending=False).head(30)
    st.dataframe(
        closed[[
            "ticket_id", "category", "priority", "description",
            "escalated_to_eng", "eng_outcome", "resolution_hrs",
            "reopen_count", "csat_score",
        ]],
        use_container_width=True,
        hide_index=True,
    )
