"""
decision_gate.py — The Second Desk decision-gate risk engine.

Two calibrated, explainable risk scores for every open ticket:
  1. escalation_risk  -> P(this escalation will bounce back as a non-bug)
  2. closure_risk     -> P(this closure will reopen)

No black-box ML. Each score is a weighted blend of named, inspectable
empirical rates (category base rate + agent history + TF-IDF similarity),
shrunk toward a stable category base rate with Laplace smoothing.
"""

import pandas as pd


def _smoothed(rate_num: float, rate_den: float, k: float = 1.0) -> float:
    """Laplace smoothing: shrink a noisy rate toward 0.5 when the sample is small."""
    if rate_den == 0:
        return 0.5
    return (rate_num + k) / (rate_den + 2 * k)


def category_waste_base_rates(df: pd.DataFrame) -> dict:
    """P(wasteful | escalated) per category, Laplace-smoothed."""
    esc = df[df["is_escalated"]]
    out = {}
    for cat in df["category"].dropna().unique():
        sub = esc[esc["category"] == cat]
        out[cat] = _smoothed(float(sub["is_wasteful_esc"].sum()), len(sub)) if len(sub) else 0.5
    return out


def category_reopen_base_rates(df: pd.DataFrame) -> dict:
    """P(reopen | closed) per category, Laplace-smoothed."""
    closed = df[df["status"] == "Closed"]
    out = {}
    for cat in df["category"].dropna().unique():
        sub = closed[closed["category"] == cat]
        out[cat] = _smoothed(float(sub["is_reopened"].sum()), len(sub)) if len(sub) else 0.5
    return out


def escalation_risk(df, row, dna, base_rates, top_k=12) -> dict:
    """Calibrated P(escalation is wasteful) + recommendation + evidence."""
    idx = row.name

    # 1) stable category base rate
    cat_rate = base_rates.get(row["category"], 0.5)

    # 2) this agent's personal wasteful-escalation rate
    a_esc = df[(df["assigned_agent"] == row["assigned_agent"]) & df["is_escalated"]]
    agent_rate = _smoothed(float(a_esc["is_wasteful_esc"].sum()), len(a_esc)) if len(a_esc) else 0.5

    # 3) TF-IDF similarity signal (demoted to one input, not the whole model)
    sim_prob, similar = dna.escalation_risk(idx, top_k=top_k)
    if sim_prob is None:
        sim_prob = 0.5

    # shrink the two noisy signals toward the stable category rate
    risk = 0.5 * cat_rate + 0.3 * agent_rate + 0.2 * sim_prob

    if sim_prob < 0.25 and cat_rate < 0.35:
        recommendation = "Escalate — matches a known code defect"
    elif risk >= 0.5:
        recommendation = "Resolve at L1 — similar tickets bounced back as non-bugs"
    else:
        recommendation = "Investigate further before escalating"

    return {
        "risk": round(float(risk), 3),
        "recommendation": recommendation,
        "evidence": similar[:3],
    }


def closure_risk(df, row, reopen_rates) -> dict:
    """Calibrated P(reopen) + the agent's own history as evidence."""
    cat_rate = reopen_rates.get(row["category"], float(df["is_reopened"].mean()))

    a_df = df[df["assigned_agent"] == row["assigned_agent"]]
    agent_rate = float(a_df["is_reopened"].mean()) if len(a_df) else 0.5

    risk = 0.6 * cat_rate + 0.4 * agent_rate

    recommendation = (
        "Hold 48h — high reopen history in this category"
        if risk >= 0.25
        else "Safe to close"
    )

    return {
        "risk": round(float(risk), 3),
        "recommendation": recommendation,
        "agent_reopen_rate": round(float(agent_rate), 3),
    }
