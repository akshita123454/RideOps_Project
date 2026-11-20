"""
metrics.py — Every KPI calculation the tool needs.

Functions are pure (DataFrame in → result out) so pages can call them
without worrying about state.
"""

import pandas as pd
import numpy as np


# ── System-level KPIs ────────────────────────────────────────────────

def backlog_pressure_index(df: pd.DataFrame) -> float:
    """
    Composite 0-100 score capturing the overall health of the support pipeline.

    Components (each 0-25, summed):
      1. Open ticket ratio      – open / total (last 30 days)
      2. Inflow acceleration    – week-over-week growth in new tickets
      3. Avg age of open tickets in hours (capped at 168 = 1 week)
      4. Wasteful escalation rate
    """
    recent = df[df["created_at"] >= df["created_at"].max() - pd.Timedelta(days=30)]

    # component 1 – open ratio (0-25)
    open_ratio = recent["is_open"].mean()
    c1 = min(open_ratio * 250, 25)  # 10 % open → 25

    # component 2 – inflow acceleration (0-25)
    weekly = recent.groupby("created_week").size()
    if len(weekly) >= 2:
        growth = (weekly.iloc[-1] - weekly.iloc[-2]) / max(weekly.iloc[-2], 1)
        c2 = min(max(growth, 0) * 100, 25)
    else:
        c2 = 0

    # component 3 – average age of currently open tickets (0-25)
    open_df = df[df["is_open"]]
    if len(open_df):
        now = df["created_at"].max()
        avg_age_hrs = (now - open_df["created_at"]).dt.total_seconds().mean() / 3600
        c3 = min(avg_age_hrs / 168 * 25, 25)
    else:
        c3 = 0

    # component 4 – wasteful escalation rate (0-25)
    esc = recent[recent["is_escalated"]]
    waste_rate = esc["is_wasteful_esc"].mean() if len(esc) else 0
    c4 = waste_rate * 25

    return round(c1 + c2 + c3 + c4, 1)


def pressure_label(score: float) -> tuple[str, str]:
    """Return (label, colour hex) for a pressure score."""
    if score < 30:
        return "NORMAL", "#047857"
    if score < 60:
        return "ELEVATED", "#B45309"
    return "CRITICAL", "#B91C1C"


# ── Weekly flow ──────────────────────────────────────────────────────

def weekly_inflow_outflow(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame with columns [week, inflow, outflow, net, running_backlog]."""
    inflow = df.groupby("created_week").size().rename("inflow")

    closed = df[df["final_closed_at"].notna()].copy()
    closed["closed_week"] = closed["final_closed_at"].dt.to_period("W").apply(
        lambda r: r.start_time
    )
    outflow = closed.groupby("closed_week").size().rename("outflow")

    flow = pd.DataFrame({"inflow": inflow, "outflow": outflow}).fillna(0).astype(int)
    flow["net"] = flow["inflow"] - flow["outflow"]
    flow["running_backlog"] = flow["net"].cumsum()
    flow.index.name = "week"
    return flow.reset_index()


# ── Agent-level metrics ──────────────────────────────────────────────

def agent_scorecard(df: pd.DataFrame) -> pd.DataFrame:
    """One row per agent with key metrics."""
    records = []
    for agent, grp in df.groupby("assigned_agent"):
        esc = grp["is_escalated"].mean()
        waste = grp["is_wasteful_esc"].mean()
        reopen = grp["is_reopened"].mean()
        frt = grp["frt_minutes"].median()
        res = grp["resolution_hrs"].median()
        csat = grp["csat_score"].mean()
        records.append(
            {
                "agent": agent,
                "tickets": len(grp),
                "open": grp["is_open"].sum(),
                "escalation_rate": round(esc * 100, 1),
                "wasteful_esc_rate": round(waste * 100, 1),
                "reopen_rate": round(reopen * 100, 1),
                "median_frt_min": round(frt, 0) if pd.notna(frt) else None,
                "median_resolution_hrs": round(res, 1) if pd.notna(res) else None,
                "avg_csat": round(csat, 2) if pd.notna(csat) else None,
            }
        )
    return pd.DataFrame(records).sort_values("escalation_rate", ascending=False)


def agent_monthly_trend(df: pd.DataFrame, agent: str) -> pd.DataFrame:
    """Monthly metrics for a single agent."""
    grp = df[df["assigned_agent"] == agent]
    records = []
    for month, mdf in grp.groupby("created_month"):
        records.append(
            {
                "month": str(month),
                "tickets": len(mdf),
                "escalation_rate": round(mdf["is_escalated"].mean() * 100, 1),
                "reopen_rate": round(mdf["is_reopened"].mean() * 100, 1),
                "median_frt_min": round(mdf["frt_minutes"].median(), 0)
                    if mdf["frt_minutes"].notna().any() else None,
            }
        )
    return pd.DataFrame(records)


# ── Category analysis ────────────────────────────────────────────────

def category_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly ticket volume by category."""
    ct = pd.crosstab(df["category"], df["created_month"])
    ct = ct.reset_index()
    return ct


def category_resolution_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Per-category: volume, escalation rate, median resolution, CSAT."""
    records = []
    for cat, grp in df.groupby("category"):
        records.append(
            {
                "category": cat,
                "tickets": len(grp),
                "escalation_rate": round(grp["is_escalated"].mean() * 100, 1),
                "wasteful_esc_rate": round(grp["is_wasteful_esc"].mean() * 100, 1),
                "median_resolution_hrs": round(grp["resolution_hrs"].median(), 1)
                    if grp["resolution_hrs"].notna().any() else None,
                "avg_csat": round(grp["csat_score"].mean(), 2)
                    if grp["csat_score"].notna().any() else None,
            }
        )
    return pd.DataFrame(records).sort_values("tickets", ascending=False)


# ── CSAT analysis ────────────────────────────────────────────────────

def csat_by_resolution_bucket(df: pd.DataFrame) -> pd.DataFrame:
    """CSAT grouped by resolution-time buckets."""
    resolved = df[df["resolution_hrs"].notna() & df["csat_score"].notna()].copy()
    bins = [0, 6, 12, 24, 48, 96, 9999]
    labels = ["<6 h", "6-12 h", "12-24 h", "24-48 h", "48-96 h", ">96 h"]
    resolved["bucket"] = pd.cut(resolved["resolution_hrs"], bins=bins, labels=labels)
    return (
        resolved.groupby("bucket", observed=False)["csat_score"]
        .agg(["mean", "count"])
        .reset_index()
    )


# ── What-If simulator ───────────────────────────────────────────────

def simulate_backlog(df: pd.DataFrame, waste_reduction_pct: float) -> pd.DataFrame:
    """
    Project weekly backlog under two scenarios:
      - actual (what happened)
      - improved (if `waste_reduction_pct` of wasteful escalations
        had been resolved at L1 in 12 h instead of 87 h)

    waste_reduction_pct: 0.0-1.0 (e.g. 0.4 = 40 % of wasteful esc. prevented)
    """
    flow = weekly_inflow_outflow(df)

    # count wasteful escalations per week
    wasteful = df[df["is_wasteful_esc"]].copy()
    waste_per_week = wasteful.groupby("created_week").size().rename("wasteful")

    flow = flow.set_index("week")
    flow = flow.join(waste_per_week, how="left").fillna(0)

    # in the improved scenario, some wasteful tickets are resolved same-week
    # instead of bouncing through engineering for 87 h+
    flow["saved"] = (flow["wasteful"] * waste_reduction_pct).astype(int)
    flow["improved_outflow"] = flow["outflow"] + flow["saved"]
    flow["improved_net"] = flow["inflow"] - flow["improved_outflow"]
    flow["improved_backlog"] = flow["improved_net"].cumsum()

    return flow.reset_index()


# ── Weekly digest ────────────────────────────────────────────────────

def weekly_digest(df: pd.DataFrame) -> str:
    """Generate a plain-text summary suitable for a Monday-morning email."""
    last_week = df["created_week"].max()
    wk = df[df["created_week"] == last_week]
    prev_wk_date = last_week - pd.Timedelta(days=7)
    prev = df[df["created_week"] == prev_wk_date]

    inflow = len(wk)
    prev_inflow = len(prev) if len(prev) else inflow
    change_pct = round((inflow - prev_inflow) / max(prev_inflow, 1) * 100, 1)

    total_open = df["is_open"].sum()
    esc_rate = round(wk["is_escalated"].mean() * 100, 1) if len(wk) else 0

    # agent with highest escalation rate this week
    agent_esc = wk.groupby("assigned_agent")["is_escalated"].mean()
    top_agent = agent_esc.idxmax() if len(agent_esc) else "N/A"
    top_rate = round(agent_esc.max() * 100, 1) if len(agent_esc) else 0

    # fastest-growing category
    cat_now = wk["category"].value_counts()
    cat_prev = prev["category"].value_counts() if len(prev) else cat_now
    cat_growth = ((cat_now - cat_prev) / cat_prev.clip(lower=1) * 100).dropna()
    if len(cat_growth):
        hot_cat = cat_growth.idxmax()
        hot_pct = round(cat_growth.max(), 1)
    else:
        hot_cat, hot_pct = "N/A", 0

    lines = [
        f"RideOps Support — Weekly Digest (week of {last_week.strftime('%b %d, %Y')})",
        "=" * 60,
        f"New tickets this week : {inflow} ({'+' if change_pct >= 0 else ''}{change_pct}% vs prior week)",
        f"Currently open        : {total_open}",
        f"Escalation rate       : {esc_rate}%",
        "",
        f"Agent spotlight        : {top_agent} — {top_rate}% escalation rate this week",
        f"Category to watch     : {hot_cat} ({'+' if hot_pct >= 0 else ''}{hot_pct}% growth)",
        "",
        "— Automated Report · RideOps Operations Intelligence",
    ]
    return "\n".join(lines)
def decompose_backlog_growth(df: pd.DataFrame) -> dict:
    """Attribute backlog growth to inflow (lambda) vs cycle time (W).

    Little's Law: L = lambda * W  (open backlog = arrival rate * avg cycle time)
    Growth decomposition: dL ~= W*d(lambda) + lambda*d(W) + d(lambda)*d(W)
    """
    inflow = df.groupby("created_month").size()                          # lambda
    closed = df[df["final_closed_at"].notna()]
    cycle = closed.groupby("created_month")["resolution_hrs"].median()   # W

    lam_jul, lam_sep = int(inflow.iloc[0]), int(inflow.iloc[-1])
    w_jul, w_sep = float(cycle.iloc[0]), float(cycle.iloc[-1])
    l_jul, l_sep = lam_jul * w_jul, lam_sep * w_sep                      # L = lambda * W

    d_lam = lam_sep - lam_jul
    d_w = w_sep - w_jul
    from_inflow = w_jul * d_lam
    from_cycle = lam_jul * d_w
    from_interaction = d_lam * d_w

    return {
        "lambda_jul": lam_jul,
        "lambda_sep": lam_sep,
        "w_jul": round(w_jul, 1),
        "w_sep": round(w_sep, 1),
        "l_jul": round(l_jul, 0),
        "l_sep": round(l_sep, 0),
        "from_inflow": round(from_inflow, 1),
        "from_cycle": round(from_cycle, 1),
        "from_interaction": round(from_interaction, 1),
    }
