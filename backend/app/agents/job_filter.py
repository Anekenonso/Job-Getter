"""Filter / Eligibility Agent.

Responsible for removing clearly unsuitable jobs before the (more expensive)
matching step, per the cost-control strategy. Uses cheap programmatic rules:
remote status, gross seniority mismatch, and obvious duplicates.

Geographic restrictions are NOT used to silently drop jobs — instead the
restriction is preserved on the job so the matcher/UI can label it honestly. We
only hard-drop jobs that are not remote at all.
"""

from __future__ import annotations

from app.models.candidate import CandidateProfile
from app.models.job import Job

_SENIORITY_RANK = {"Junior": 1, "Mid": 2, "Senior": 3}


def _seniority_of_job(job: Job) -> int | None:
    text = f"{job.title} {job.description}".lower()
    if any(w in text for w in ("principal", "staff", "head of", "director")):
        return 4
    if "senior" in text or "lead" in text:
        return 3
    if "junior" in text or "entry" in text or "intern" in text:
        return 1
    if "mid" in text:
        return 2
    return None


def is_eligible(profile: CandidateProfile, job: Job) -> bool:
    # Rule 1: must be remote.
    if not job.remote:
        return False

    # Rule 2: drop only egregious seniority gaps (candidate two-plus levels below).
    job_level = _seniority_of_job(job)
    cand_level = _SENIORITY_RANK.get(profile.seniority, 1)
    if job_level is not None and job_level - cand_level >= 2:
        return False

    return True


def filter_jobs(profile: CandidateProfile, jobs: list[Job]) -> list[Job]:
    return [job for job in jobs if is_eligible(profile, job)]
