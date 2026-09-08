"""Pipeline orchestrator.

Wires the agents together in the order described in the spec's agent workflow:

    CV text -> CV Parser -> Research -> Filter -> Matcher -> Ranking -> results

Keeping the orchestration in one place (rather than inside any single agent)
means each agent stays single-purpose and the flow is easy to follow.
"""

from __future__ import annotations

from app import config
from app.agents import cv_parser, job_filter, job_matcher, job_researcher, ranking
from app.models.candidate import CandidateProfile


def find_jobs(
    profile: CandidateProfile,
    exclude_ids: set[str] | None = None,
    variation: int = 0,
) -> dict:
    """Run research -> filter -> match -> rank for an already-parsed profile."""
    candidate_jobs, queries = job_researcher.research(
        profile, exclude_ids=exclude_ids, variation=variation
    )
    eligible = job_filter.filter_jobs(profile, candidate_jobs)

    # Bound how many jobs reach the (potentially LLM-backed) matcher.
    shortlist = eligible[: max(config.MATCH_SHORTLIST_SIZE, config.TOP_N_RESULTS)]
    matches = job_matcher.match_all(profile, shortlist)

    result = ranking.rank(matches)
    result["queries"] = queries
    return result


def analyze_and_match(cv_text: str) -> dict:
    """Full flow from raw CV text to ranked results."""
    profile = cv_parser.parse(cv_text)
    result = find_jobs(profile)
    result["candidate"] = profile
    result["enough_signal"] = cv_parser.has_enough_signal(cv_text, profile)
    return result
