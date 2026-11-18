"""
ticket_dna.py — Ticket similarity engine using TF-IDF on descriptions.

Provides two main features:
  1. find_similar()      – top-K past resolved tickets that look like the current one
  2. escalation_risk()   – probability that escalating this ticket will be wasteful,
                           based on outcomes of similar tickets in the past
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TicketDNA:
    """Build a TF-IDF model over all ticket descriptions, then query it."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.closed_mask = df["status"] == "Closed"
        self.closed_indices = df.index[self.closed_mask].tolist()

        # fit TF-IDF on every ticket so the vocabulary covers open ones too
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=600,
            ngram_range=(1, 2),
            sublinear_tf=True,
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(
            df["description"].fillna("")
        )

    # ------------------------------------------------------------------
    def find_similar(self, ticket_idx: int, top_k: int = 5) -> list[dict]:
        """Return the top-K most-similar *closed* tickets."""

        query_vec = self.tfidf_matrix[ticket_idx]
        closed_vecs = self.tfidf_matrix[self.closed_indices]
        sims = cosine_similarity(query_vec, closed_vecs).flatten()

        # don't match yourself
        if ticket_idx in self.closed_indices:
            pos = self.closed_indices.index(ticket_idx)
            sims[pos] = -1.0

        ranked = sims.argsort()[::-1][:top_k]
        results = []
        for r in ranked:
            score = float(sims[r])
            if score < 0.10:
                continue
            row = self.df.iloc[self.closed_indices[r]]
            results.append(
                {
                    "ticket_id": row["ticket_id"],
                    "description": row["description"],
                    "category": row["category"],
                    "similarity": round(score, 2),
                    "was_escalated": bool(row["is_escalated"]),
                    "eng_outcome": row.get("eng_outcome", ""),
                    "was_wasteful": bool(row.get("is_wasteful_esc", False)),
                    "resolution_hrs": row.get("resolution_hrs"),
                    "resolution_path": self._path_label(row),
                }
            )
        return results

    # ------------------------------------------------------------------
    def escalation_risk(self, ticket_idx: int, top_k: int = 15):
        """
        Return (waste_probability, similar_tickets).
        waste_probability is the fraction of similar escalated tickets
        that turned out to be non-bugs.
        """
        similar = self.find_similar(ticket_idx, top_k=top_k)
        if not similar:
            return 0.5, similar  # no data — unknown

        escalated = [s for s in similar if s["was_escalated"]]
        if not escalated:
            return 0.0, similar  # none were escalated

        wasteful = [s for s in escalated if s["was_wasteful"]]
        return len(wasteful) / len(escalated), similar

    # ------------------------------------------------------------------
    @staticmethod
    def _path_label(row) -> str:
        if not row["is_escalated"]:
            return "Resolved by L1"
        outcome = row.get("eng_outcome", "")
        return f"Escalated → {outcome}" if outcome else "Escalated (pending)"
