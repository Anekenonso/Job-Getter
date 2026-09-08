"""Job Research Agent.

Responsible only for discovering potential jobs. It turns a candidate profile
into a set of search queries (LLM when available, heuristics otherwise), then
delegates the actual fetching to the search service. It does not score matches.

To keep repeat searches fresh, it can rotate/vary the queries and pass along the
set of already-seen job IDs so the search service can exclude them.
"""

from __future__ import annotations

from app.models.candidate import CandidateProfile
from app.models.job import Job
from app.services import llm, search

_LLM_SYSTEM = (
    "You generate concise remote-job search queries from a candidate profile. "
    "Respond with a single JSON object."
)

_LLM_TEMPLATE = """Given this candidate profile, produce 5-7 remote job search
queries that reflect their actual qualifications and reasonable adjacent roles.

Return JSON: {{ "queries": ["remote ...", ...] }}

PROFILE:
{profile}
"""


def _heuristic_queries(profile: CandidateProfile) -> list[str]:
    queries: list[str] = []
    for title in profile.job_titles[:5]:
        queries.append(f"remote {title.lower()}")
    for skill in profile.skills[:3]:
        queries.append(f"remote {skill} jobs")
    # De-duplicate while preserving order.
    seen, out = set(), []
    for q in queries:
        if q not in seen:
            seen.add(q)
            out.append(q)
    return out or ["remote software engineer"]


def generate_queries(profile: CandidateProfile, variation: int = 0) -> list[str]:
    """Build search queries. `variation` rotates ordering for repeat searches."""
    queries: list[str] | None = None
    if llm.is_enabled():
        try:
            data = llm.complete_json(
                _LLM_SYSTEM, _LLM_TEMPLATE.format(profile=profile.public_signals())
            )
            raw = data.get("queries")
            if isinstance(raw, list) and raw:
                queries = [str(q) for q in raw if str(q).strip()]
        except llm.LLMUnavailable:
            queries = None

    if not queries:
        queries = _heuristic_queries(profile)

    # Rotate the query list so a repeat search explores in a different order.
    if variation and queries:
        shift = variation % len(queries)
        queries = queries[shift:] + queries[:shift]
    return queries


def research(
    profile: CandidateProfile,
    exclude_ids: set[str] | None = None,
    variation: int = 0,
) -> tuple[list[Job], list[str]]:
    """Return (candidate jobs, queries used)."""
    queries = generate_queries(profile, variation=variation)
    jobs = search.search(queries, exclude_ids=exclude_ids)
    return jobs, queries
