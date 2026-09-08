"""Job discovery service.

For V1 the "web research" is served from the pre-ingested job cache (filled by
the ingestion cron). This module loads that cache, applies query-driven variation
so repeat searches surface different roles, and hands normalized `Job` objects to
the pipeline. Swapping in live API calls later means only changing this file.
"""

from __future__ import annotations

import json
import logging

from app import config
from app.models.job import Job
from app.services import job_normalizer

logger = logging.getLogger(__name__)


def load_cache() -> list[Job]:
    if not config.JOB_CACHE_PATH.exists():
        logger.warning("Job cache not found at %s", config.JOB_CACHE_PATH)
        return []
    try:
        with config.JOB_CACHE_PATH.open("r", encoding="utf-8") as f:
            raw_jobs = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        logger.error("Failed to read job cache: %s", exc)
        return []
    jobs = [job_normalizer.from_cache(raw) for raw in raw_jobs]
    return job_normalizer.dedupe(jobs)


def _relevance(job: Job, queries: list[str]) -> int:
    """Cheap lexical overlap between the search queries and a job posting."""
    haystack = f"{job.title} {job.description} {' '.join(job.required_skills)}".lower()
    score = 0
    for query in queries:
        for term in query.lower().split():
            if len(term) > 2 and term in haystack:
                score += 1
    return score


def search(
    queries: list[str],
    exclude_ids: set[str] | None = None,
    limit: int | None = None,
) -> list[Job]:
    """Return candidate jobs ordered by lexical relevance to the queries.

    `exclude_ids` lets a repeat search skip jobs already shown, introducing
    variation without ever sacrificing relevance (spec section 14).
    """
    exclude_ids = exclude_ids or set()
    jobs = [job for job in load_cache() if job.id not in exclude_ids]

    if queries:
        jobs.sort(key=lambda job: _relevance(job, queries), reverse=True)

    if limit is not None:
        jobs = jobs[:limit]
    return jobs
