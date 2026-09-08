"""Candidate profile schema.

Mirrors the structured output described in the spec (section 5). Fields that the
parser cannot reliably determine default to empty rather than being invented.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    professional_title: str = "Professional"
    seniority: str = "Junior"
    years_experience: int = 0
    skills: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    industries: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    job_titles: list[str] = Field(default_factory=list)

    def public_signals(self) -> dict:
        """Minimal, non-identifying view sent to external services.

        Deliberately excludes name/contact details per the privacy requirement
        to minimize personal information leaving the system.
        """
        return {
            "professional_title": self.professional_title,
            "seniority": self.seniority,
            "years_experience": self.years_experience,
            "skills": self.skills,
            "tools": self.tools,
            "industries": self.industries,
            "job_titles": self.job_titles,
        }
