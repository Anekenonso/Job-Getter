"""CV Parser Agent.

Responsible only for understanding the CV: it turns raw text into a structured
`CandidateProfile`. It uses the LLM when available and falls back to deterministic
heuristics otherwise, so extraction always produces a usable profile.

It does not search for jobs.
"""

from __future__ import annotations

import json
import re

from app.models.candidate import CandidateProfile
from app.services import llm

# --- Heuristic keyword banks -------------------------------------------------

SKILL_KEYWORDS = {
    "python": ["python", "django", "fastapi", "flask", "pandas", "numpy"],
    "javascript": ["javascript", "typescript", "react", "node", "next.js", "vue"],
    "sql": ["sql", "postgres", "mysql", "database", "query optimization"],
    "ai": ["ai", "machine learning", "ml", "llm", "nlp", "genai", "computer vision"],
    "automation": ["automation", "workflow", "zapier", "integration", "etl", "orchestration"],
    "aws": ["aws", "lambda", "s3", "ec2", "cloud"],
    "devops": ["docker", "kubernetes", "ci/cd", "terraform", "ansible"],
    "data": ["data analysis", "analytics", "bi", "tableau", "power bi"],
    "testing": ["pytest", "playwright", "cypress", "unit testing", "qa", "selenium"],
    "frontend": ["react", "css", "tailwind", "html", "accessibility", "figma"],
}

TOOL_NAMES = [
    "Python", "FastAPI", "Django", "Flask", "SQL", "PostgreSQL", "MySQL",
    "GitHub", "Docker", "Kubernetes", "React", "Next.js", "Vue", "AWS",
    "Node.js", "TypeScript", "Tailwind", "Terraform", "Jest", "Playwright",
]

DEGREE_PATTERNS = [
    (re.compile(r"\bph\.?d\b", re.I), "PhD"),
    (re.compile(r"\bmaster'?s?\b|\bm\.?sc\b|\bmba\b", re.I), "Master's Degree"),
    (re.compile(r"\bbachelor'?s?\b|\bb\.?sc\b|\bb\.?a\b|\bb\.?eng\b", re.I), "Bachelor's Degree"),
    (re.compile(r"\bassociate'?s?\b", re.I), "Associate Degree"),
]


def _detect_skills(text: str) -> list[str]:
    lower = text.lower()
    found = [label for label, kws in SKILL_KEYWORDS.items() if any(k in lower for k in kws)]
    return sorted(found)


def _detect_tools(text: str) -> list[str]:
    lower = text.lower()
    return [tool for tool in TOOL_NAMES if tool.lower() in lower][:8]


def _estimate_years(text: str) -> int:
    match = re.search(r"(\d+)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience", text.lower())
    if match:
        return int(match.group(1))
    match = re.search(r"experience\s*(?:of|:)?\s*(\d+)\s*\+?\s*(?:years?|yrs?)", text.lower())
    if match:
        return int(match.group(1))
    return 0


def _infer_seniority(years: int, text: str) -> str:
    lower = text.lower()
    if "senior" in lower or "lead" in lower or "principal" in lower or years >= 6:
        return "Senior"
    if "junior" in lower or "entry" in lower:
        return "Junior"
    if years >= 3:
        return "Mid"
    return "Junior"


def _detect_education(text: str) -> list[str]:
    found = []
    for pattern, label in DEGREE_PATTERNS:
        if pattern.search(text) and label not in found:
            found.append(label)
    return found


def _infer_title(text: str, skills: list[str]) -> str:
    lower = text.lower()
    if "ai" in skills and "automation" in skills:
        return "AI Automation Engineer"
    if "frontend" in skills or "javascript" in skills:
        return "Frontend Developer"
    if "data" in skills:
        return "Data Analyst"
    if "devops" in skills or "aws" in skills:
        return "DevOps Engineer"
    if "python" in skills:
        return "Python Developer"
    if "testing" in skills:
        return "QA Automation Engineer"
    return "Software Engineer"


def _alt_titles(primary: str, skills: list[str]) -> list[str]:
    pool = {
        primary,
        "Remote Software Engineer",
    }
    if "python" in skills:
        pool.update({"Python Developer", "Backend Engineer"})
    if "automation" in skills:
        pool.update({"Automation Engineer", "Operations Automation Specialist"})
    if "ai" in skills:
        pool.update({"AI Engineer", "ML Engineer"})
    if "frontend" in skills or "javascript" in skills:
        pool.update({"Frontend Developer", "Full Stack Engineer", "React Developer"})
    if "data" in skills:
        pool.update({"Data Analyst", "Product Analyst"})
    return list(pool)[:6]


def _heuristic_profile(text: str) -> CandidateProfile:
    skills = _detect_skills(text)
    years = _estimate_years(text)
    title = _infer_title(text, skills)
    return CandidateProfile(
        professional_title=title,
        seniority=_infer_seniority(years, text),
        years_experience=years,
        skills=skills,
        tools=_detect_tools(text),
        industries=["Technology"],
        education=_detect_education(text),
        certifications=[],
        languages=[],
        job_titles=_alt_titles(title, skills),
    )


_LLM_SYSTEM = (
    "You are a precise CV parser. Extract only information explicitly supported "
    "by the CV text. Never invent skills, employers, or credentials. Respond with "
    "a single JSON object."
)

_LLM_TEMPLATE = """Extract a candidate profile from the CV below.

Return JSON with exactly these keys:
- professional_title (string)
- seniority (one of: "Junior", "Mid", "Senior")
- years_experience (integer)
- skills (array of short lowercase skill labels)
- tools (array of tool/software names)
- industries (array)
- education (array of degree names)
- certifications (array)
- languages (array of spoken languages)
- job_titles (array of 4-6 relevant/alternative job titles to search for)

CV TEXT:
{cv_text}
"""


def _llm_profile(text: str) -> CandidateProfile | None:
    try:
        data = llm.complete_json(_LLM_SYSTEM, _LLM_TEMPLATE.format(cv_text=text[:8000]))
    except llm.LLMUnavailable:
        return None
    try:
        return CandidateProfile(
            professional_title=str(data.get("professional_title") or "Professional"),
            seniority=str(data.get("seniority") or "Junior"),
            years_experience=int(data.get("years_experience") or 0),
            skills=[str(s).lower() for s in data.get("skills", [])],
            tools=[str(t) for t in data.get("tools", [])],
            industries=[str(i) for i in data.get("industries", [])],
            education=[str(e) for e in data.get("education", [])],
            certifications=[str(c) for c in data.get("certifications", [])],
            languages=[str(lang) for lang in data.get("languages", [])],
            job_titles=[str(j) for j in data.get("job_titles", [])],
        )
    except (TypeError, ValueError, json.JSONDecodeError):
        return None


# Minimum signal we need to produce reliable matches (spec: poor-CV handling).
_MIN_SKILLS = 1
_MIN_TEXT_LEN = 80


def has_enough_signal(text: str, profile: CandidateProfile) -> bool:
    return len(text) >= _MIN_TEXT_LEN and len(profile.skills) >= _MIN_SKILLS


def parse(text: str) -> CandidateProfile:
    """Parse CV text into a candidate profile, LLM-first with heuristic fallback."""
    profile = _llm_profile(text) if llm.is_enabled() else None
    if profile is None or not profile.skills:
        heuristic = _heuristic_profile(text)
        if profile is None:
            return heuristic
        # LLM returned but with no skills — enrich from heuristics rather than lose them.
        if not profile.skills:
            profile.skills = heuristic.skills
        if not profile.tools:
            profile.tools = heuristic.tools
        if not profile.job_titles:
            profile.job_titles = heuristic.job_titles
    return profile
