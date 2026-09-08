"""Job and match schemas.

`Job` is the normalized internal format that every source is converted into
(spec section 8). `JobMatch` wraps a job with its score, breakdown, explanation,
and honest gap list (spec sections 10-12).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Job(BaseModel):
    id: str
    title: str
    company: str
    location: str = "Remote"
    remote: bool = True
    # Free-form geographic restriction, e.g. "US only". None means unrestricted.
    location_restriction: str | None = None
    salary: str | None = None
    description: str = ""
    required_skills: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
    source: str = "Unknown"
    url: str
    date_posted: str | None = None


class ScoreBreakdown(BaseModel):
    skills: int = 0
    experience: int = 0
    role_similarity: int = 0
    seniority: int = 0
    education: int = 0
    industry: int = 0
    location: int = 0


class JobMatch(BaseModel):
    # Flattened job fields so the frontend gets a single flat object per card.
    id: str
    title: str
    company: str
    location: str
    remote: bool
    location_restriction: str | None = None
    salary: str | None = None
    description: str
    required_skills: list[str]
    source: str
    url: str
    date_posted: str | None = None

    match_score: int
    match_reason: str
    matching_skills: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    breakdown: ScoreBreakdown | None = None

    @classmethod
    def from_job(cls, job: Job, **scoring) -> "JobMatch":
        return cls(
            id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
            remote=job.remote,
            location_restriction=job.location_restriction,
            salary=job.salary,
            description=job.description,
            required_skills=job.required_skills,
            source=job.source,
            url=job.url,
            date_posted=job.date_posted,
            **scoring,
        )
