"""Request/response schemas for the API layer."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.candidate import CandidateProfile
from app.models.job import JobMatch


class SearchPreferences(BaseModel):
    remote_only: bool = True


class FindJobsRequest(BaseModel):
    candidate_profile: CandidateProfile
    search_preferences: SearchPreferences = Field(default_factory=SearchPreferences)
    exclude_ids: list[str] = Field(default_factory=list)
    variation: int = 0


class JobsResponse(BaseModel):
    jobs: list[JobMatch]
    possible_matches: list[JobMatch] = Field(default_factory=list)
    strong_count: int
    message: str | None = None


class AnalyzeResponse(JobsResponse):
    candidate: CandidateProfile
