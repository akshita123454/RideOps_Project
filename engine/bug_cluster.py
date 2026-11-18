"""
bug_cluster.py — Detect product-level bugs hiding inside support ticket patterns.

Groups tickets by description similarity and surfaces clusters that are
large enough to indicate a systemic product issue rather than one-off complaints.
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict


def find_bug_clusters(
    df: pd.DataFrame,
    min_cluster_size: int = 5,
    similarity_threshold: float = 0.75,
) -> list[dict]:
    """
    Two-pass clustering:
      Pass 1 — exact description matches (fast, catches the obvious ones).
      Pass 2 — TF-IDF cosine similarity for near-duplicates (catches variations).

    Returns a list of cluster dicts sorted by size (largest first).
    """

    # ── Pass 1: exact matches ────────────────────────────────────────
    desc_groups = df.groupby("description")
    exact_clusters: dict[str, list[int]] = {}
    for desc, grp in desc_groups:
        if len(grp) >= min_cluster_size:
            exact_clusters[desc] = grp.index.tolist()

    # mark indices already claimed
    claimed = set()
    for idxs in exact_clusters.values():
        claimed.update(idxs)

    # ── Pass 2: fuzzy match the remaining tickets ────────────────────
    unclaimed_df = df.loc[~df.index.isin(claimed)]

    if len(unclaimed_df) > 20:
        vectorizer = TfidfVectorizer(
            stop_words="english", max_features=400, ngram_range=(1, 2)
        )
        vecs = vectorizer.fit_transform(unclaimed_df["description"].fillna(""))
        sim_matrix = cosine_similarity(vecs)

        # greedy clustering
        visited = set()
        fuzzy_clusters: list[list[int]] = []
        unclaimed_indices = unclaimed_df.index.tolist()

        for i in range(len(unclaimed_indices)):
            if i in visited:
                continue
            cluster = [i]
            visited.add(i)
            for j in range(i + 1, len(unclaimed_indices)):
                if j in visited:
                    continue
                if sim_matrix[i, j] >= similarity_threshold:
                    cluster.append(j)
                    visited.add(j)
            if len(cluster) >= min_cluster_size:
                fuzzy_clusters.append(
                    [unclaimed_indices[k] for k in cluster]
                )
    else:
        fuzzy_clusters = []

    # ── Build result dicts ───────────────────────────────────────────
    results = []

    for desc, idxs in exact_clusters.items():
        grp = df.loc[idxs]
        results.append(_cluster_summary(grp, desc, match_type="exact"))

    for idxs in fuzzy_clusters:
        grp = df.loc[idxs]
        # use the most common description as the representative label
        rep = grp["description"].mode().iloc[0] if len(grp) else ""
        results.append(_cluster_summary(grp, rep, match_type="fuzzy"))

    results.sort(key=lambda c: c["ticket_count"], reverse=True)
    return results


def _cluster_summary(grp: pd.DataFrame, label: str, match_type: str) -> dict:
    """Summarise a cluster into a compact dict."""
    return {
        "description": label,
        "match_type": match_type,
        "ticket_count": len(grp),
        "category": grp["category"].mode().iloc[0] if len(grp) else "",
        "affected_clients": grp["client_name"].nunique(),
        "client_list": ", ".join(grp["client_name"].unique()[:5])
            + ("…" if grp["client_name"].nunique() > 5 else ""),
        "avg_resolution_hrs": round(grp["resolution_hrs"].mean(), 1)
            if grp["resolution_hrs"].notna().any() else None,
        "escalation_rate": round(grp["is_escalated"].mean() * 100, 1),
        "avg_csat": round(grp["csat_score"].mean(), 2)
            if grp["csat_score"].notna().any() else None,
        "months_active": sorted(grp["created_month"].unique().tolist()),
        "ticket_ids": grp["ticket_id"].tolist(),
    }


def cluster_impact_summary(clusters: list[dict], total_tickets: int) -> dict:
    """Roll up all clusters into a single impact statement."""
    total_in_clusters = sum(c["ticket_count"] for c in clusters)
    return {
        "total_clusters": len(clusters),
        "total_tickets_in_clusters": total_in_clusters,
        "pct_of_all_tickets": round(total_in_clusters / max(total_tickets, 1) * 100, 1),
        "top_cluster_desc": clusters[0]["description"] if clusters else "",
        "top_cluster_size": clusters[0]["ticket_count"] if clusters else 0,
    }
