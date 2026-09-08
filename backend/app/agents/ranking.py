"""Ranking Agent.

Orders scored jobs and selects the final results. Splits them into "strong"
matches (at or above the configured threshold) and weaker "possible" matches,
so the app can be honest when it can't find a full set of strong matches rather
than padding the list with poor results.
"""

from __future__ import annotations

from app import config
from app.models.job import JobMatch


def rank(matches: list[JobMatch], top_n: int | None = None) -> dict:
    """Return the final result set.

    Shape:
        {
          "strong": [JobMatch, ...],   # up to top_n, score >= threshold
          "possible": [JobMatch, ...], # weaker matches, offered separately
          "strong_count": int,
        }
    """
    top_n = top_n or config.TOP_N_RESULTS
    ordered = sorted(matches, key=lambda m: m.match_score, reverse=True)

    strong = [m for m in ordered if m.match_score >= config.STRONG_MATCH_THRESHOLD]
    weak = [m for m in ordered if m.match_score < config.STRONG_MATCH_THRESHOLD]

    top_strong = strong[:top_n]
    # Only offer "possible" matches if we couldn't fill the strong list.
    remaining = top_n - len(top_strong)
    possible = weak[:remaining] if remaining > 0 else []

    return {
        "strong": top_strong,
        "possible": possible,
        "strong_count": len(top_strong),
    }
