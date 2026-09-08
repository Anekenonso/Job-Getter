"""Matching Agent.

Compares a candidate profile against each shortlisted job and produces a score
(0-100), an honest explanation, the matching skills, and any gaps. Scoring is
weighted per `config.MATCH_WEIGHTS` so the rubric can be retuned without code
changes.

A deterministic scorer always runs (cheap, explainable). When the LLM is enabled
it can enrich the explanation/gaps for the shortlist, but it never fabricates a
skill the CV does not support.
"""

from __future__ import annotations

import re

from app import config
from app.models.candidate import CandidateProfile
from app.models.job import Job, JobMatch, ScoreBreakdown
from app.services import llm

_SENIORITY_RANK = {"Junior": 1, "Mid": 2, "Senior": 3}
_WORD_RE = re.compile(r"[a-z0-9\+\.#]+")


def _tokens(text: str) -> set[str]:
    return {t for t in _WORD_RE.findall(text.lower()) if len(t) > 1}


def _skills_component(profile: CandidateProfile, job: Job) -> tuple[float, list[str]]:
    """Fraction of the job's required skills the candidate demonstrably has."""
    required = [s.lower() for s in job.required_skills]
    if not required:
        # No explicit skill list: fall back to token overlap on the description.
        cand = _tokens(" ".join(profile.skills + profile.tools))
        job_tokens = _tokens(job.description)
        overlap = cand & job_tokens
        matched = sorted(overlap)[:6]
        return (min(1.0, len(overlap) / 5) if overlap else 0.0, matched)

    cand_blob = " ".join(profile.skills + profile.tools).lower()
    matched = [skill for skill in required if skill in cand_blob]
    return (len(matched) / len(required), matched)


def _experience_component(profile: CandidateProfile, job: Job) -> tuple[float, str | None]:
    required_years = _required_years(job)
    if required_years is None:
        return 0.7, None  # unknown requirement → neutral-positive
    if profile.years_experience >= required_years:
        return 1.0, None
    gap = required_years - profile.years_experience
    ratio = max(0.0, profile.years_experience / required_years)
    note = (
        f"Job requests {required_years}+ years of experience; "
        f"your CV shows approximately {profile.years_experience}."
    )
    return ratio, (note if gap >= 1 else None)


def _required_years(job: Job) -> int | None:
    match = re.search(r"(\d+)\s*\+?\s*(?:years?|yrs?)", job.description.lower())
    if match:
        return int(match.group(1))
    return None


def _role_similarity_component(profile: CandidateProfile, job: Job) -> float:
    title = job.title.lower()
    for candidate_title in profile.job_titles:
        ct = candidate_title.lower()
        if ct in title or title in ct:
            return 1.0
    # Partial: any shared significant word between titles.
    job_words = _tokens(job.title)
    cand_words = set()
    for t in profile.job_titles:
        cand_words |= _tokens(t)
    overlap = job_words & cand_words
    if overlap:
        return 0.6
    return 0.2


def _seniority_component(profile: CandidateProfile, job: Job) -> float:
    cand = _SENIORITY_RANK.get(profile.seniority, 1)
    text = f"{job.title} {job.description}".lower()
    if "senior" in text or "lead" in text:
        job_level = 3
    elif "junior" in text or "entry" in text:
        job_level = 1
    elif "mid" in text:
        job_level = 2
    else:
        return 0.8  # unspecified → mostly fine
    diff = abs(cand - job_level)
    return {0: 1.0, 1: 0.7}.get(diff, 0.3)


def _education_component(profile: CandidateProfile, job: Job) -> float:
    desc = job.description.lower()
    if "degree" not in desc and "bachelor" not in desc and "master" not in desc:
        return 1.0  # no stated requirement
    return 1.0 if profile.education else 0.4


def _industry_component(profile: CandidateProfile, job: Job) -> float:
    if not profile.industries:
        return 0.6
    blob = f"{job.title} {job.description} {job.company}".lower()
    return 1.0 if any(ind.lower() in blob for ind in profile.industries) else 0.5


def _location_component(profile: CandidateProfile, job: Job) -> tuple[float, str | None]:
    if job.location_restriction:
        note = (
            f"Role is restricted to {job.location_restriction}; "
            "confirm you can work from there."
        )
        return 0.4, note
    return 1.0, None


def score(profile: CandidateProfile, job: Job) -> JobMatch:
    weights = config.MATCH_WEIGHTS

    skills_frac, matching_skills = _skills_component(profile, job)
    exp_frac, exp_gap = _experience_component(profile, job)
    role_frac = _role_similarity_component(profile, job)
    sen_frac = _seniority_component(profile, job)
    edu_frac = _education_component(profile, job)
    ind_frac = _industry_component(profile, job)
    loc_frac, loc_gap = _location_component(profile, job)

    breakdown = ScoreBreakdown(
        skills=round(skills_frac * weights["skills"] * 100),
        experience=round(exp_frac * weights["experience"] * 100),
        role_similarity=round(role_frac * weights["role_similarity"] * 100),
        seniority=round(sen_frac * weights["seniority"] * 100),
        education=round(edu_frac * weights["education"] * 100),
        industry=round(ind_frac * weights["industry"] * 100),
        location=round(loc_frac * weights["location"] * 100),
    )
    total = (
        breakdown.skills
        + breakdown.experience
        + breakdown.role_similarity
        + breakdown.seniority
        + breakdown.education
        + breakdown.industry
        + breakdown.location
    )
    total = max(0, min(99, total))

    gaps = [g for g in (exp_gap, loc_gap) if g]
    reason = _build_reason(total, matching_skills)

    return JobMatch.from_job(
        job,
        match_score=total,
        match_reason=reason,
        matching_skills=[s.title() if s.islower() else s for s in matching_skills],
        gaps=gaps,
        breakdown=breakdown,
    )


def _build_reason(total: int, matching_skills: list[str]) -> str:
    if matching_skills:
        skills_txt = ", ".join(s.title() if s.islower() else s for s in matching_skills[:4])
        if total >= config.STRONG_MATCH_THRESHOLD:
            return f"Strong overlap on {skills_txt} lines up directly with the role."
        return f"Relevant overlap on {skills_txt}, with a few gaps to confirm."
    if total >= config.STRONG_MATCH_THRESHOLD:
        return "Your background maps well onto this role."
    return "Useful adjacent experience, though not a direct fit for the core role."


_LLM_SYSTEM = (
    "You explain job matches honestly. Never claim a candidate has a skill their "
    "profile does not list. Respond with a single JSON object."
)

_LLM_TEMPLATE = """Given the candidate and job, write an honest one-sentence
explanation of why they match and list any genuine gaps.

Return JSON: {{ "reason": "...", "gaps": ["..."] }}

CANDIDATE: {profile}
JOB TITLE: {title}
JOB DESCRIPTION: {description}
REQUIRED SKILLS: {skills}
"""


def enrich_explanation(profile: CandidateProfile, match: JobMatch) -> JobMatch:
    """Optionally improve the explanation via LLM. Safe no-op if unavailable."""
    if not llm.is_enabled():
        return match
    try:
        data = llm.complete_json(
            _LLM_SYSTEM,
            _LLM_TEMPLATE.format(
                profile=profile.public_signals(),
                title=match.title,
                description=match.description[:1500],
                skills=", ".join(match.required_skills),
            ),
        )
    except llm.LLMUnavailable:
        return match
    reason = data.get("reason")
    gaps = data.get("gaps")
    if isinstance(reason, str) and reason.strip():
        match.match_reason = reason.strip()
    if isinstance(gaps, list):
        match.gaps = [str(g) for g in gaps if str(g).strip()][:3]
    return match


def match_all(
    profile: CandidateProfile, jobs: list[Job], enrich: bool = True
) -> list[JobMatch]:
    """Score every job, then optionally enrich the top shortlist via LLM."""
    matches = [score(profile, job) for job in jobs]
    matches.sort(key=lambda m: m.match_score, reverse=True)

    if enrich and llm.is_enabled():
        for match in matches[: config.MATCH_SHORTLIST_SIZE]:
            enrich_explanation(profile, match)
    return matches
