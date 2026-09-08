"""Job cache refresh script.

Runs on a schedule (GitHub Actions cron) with no user involved. It pulls fresh
remote jobs from public APIs, normalizes them into the internal schema, dedupes,
and writes the shared job cache that the live API reads from.

Sources (all free, public, ToS-friendly JSON APIs):
  - Jobicy      https://jobicy.com/api/v2/remote-jobs
  - Remotive    https://remotive.com/api/remote-jobs
  - Arbeitnow   https://www.arbeitnow.com/api/job-board-api

Run locally:
    python ingestion/refresh_cache.py

The script is defensive: if a source is unreachable it is skipped rather than
failing the whole refresh. If every source fails, the existing cache is left
untouched so the app keeps serving the last good data.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import httpx

# Make the backend package importable so we reuse the exact normalizer the API uses.
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.services import job_normalizer  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("refresh_cache")

CACHE_PATH = REPO_ROOT / "data" / "jobs_cache.json"
HTTP_TIMEOUT = 30
MAX_PER_SOURCE = 80

JOBICY_URL = "https://jobicy.com/api/v2/remote-jobs?count=50"
REMOTIVE_URL = "https://remotive.com/api/remote-jobs?limit=50"
ARBEITNOW_URL = "https://www.arbeitnow.com/api/job-board-api"


def _get_json(client: httpx.Client, url: str) -> dict | list | None:
    try:
        response = client.get(url)
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, json.JSONDecodeError) as exc:
        logger.warning("Source failed (%s): %s", url, exc)
        return None


def fetch_jobicy(client: httpx.Client) -> list:
    data = _get_json(client, JOBICY_URL)
    if not data:
        return []
    raw_jobs = data.get("jobs", []) if isinstance(data, dict) else []
    return [job_normalizer.from_jobicy(j) for j in raw_jobs[:MAX_PER_SOURCE]]


def fetch_remotive(client: httpx.Client) -> list:
    data = _get_json(client, REMOTIVE_URL)
    if not data:
        return []
    raw_jobs = data.get("jobs", []) if isinstance(data, dict) else []
    return [job_normalizer.from_remotive(j) for j in raw_jobs[:MAX_PER_SOURCE]]


def fetch_arbeitnow(client: httpx.Client) -> list:
    data = _get_json(client, ARBEITNOW_URL)
    if not data:
        return []
    raw_jobs = data.get("data", []) if isinstance(data, dict) else []
    normalized = [job_normalizer.from_arbeitnow(j) for j in raw_jobs[:MAX_PER_SOURCE]]
    # Arbeitnow includes non-remote roles; keep only remote ones.
    return [job for job in normalized if job.remote]


def refresh() -> int:
    all_jobs = []
    with httpx.Client(timeout=HTTP_TIMEOUT, headers={"User-Agent": "Job-Getter/1.0"}) as client:
        for name, fetcher in (
            ("Jobicy", fetch_jobicy),
            ("Remotive", fetch_remotive),
            ("Arbeitnow", fetch_arbeitnow),
        ):
            jobs = fetcher(client)
            logger.info("%s: %d jobs", name, len(jobs))
            all_jobs.extend(jobs)

    if not all_jobs:
        logger.warning("No jobs fetched from any source; leaving existing cache untouched.")
        return 0

    deduped = job_normalizer.dedupe(all_jobs)
    # Keep only jobs that have a usable application URL (anti-hallucination).
    deduped = [job for job in deduped if job.url]
    logger.info("Writing %d jobs to cache", len(deduped))

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = [job.model_dump() for job in deduped]
    with CACHE_PATH.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return len(deduped)


if __name__ == "__main__":
    count = refresh()
    logger.info("Done. Cache now holds %d jobs.", count)
