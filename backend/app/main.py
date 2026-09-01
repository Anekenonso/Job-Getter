from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from docx import Document
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader

APP_ROOT = Path(__file__).resolve().parents[2]
JOB_CACHE_PATH = APP_ROOT / "data" / "jobs_cache.json"

app = FastAPI(title="Job Getter API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SKILL_KEYWORDS = {
    "python": ["python", "django", "fastapi", "flask", "pandas", "numpy"],
    "javascript": ["javascript", "typescript", "react", "node", "next", "vue"],
    "sql": ["sql", "postgres", "mysql", "database", "query optimization"],
    "ai": ["ai", "machine learning", "ml", "llm", "nlp", "genai"],
    "automation": ["automation", "workflow", "zapier", "integration", "apis", "etl"],
    "aws": ["aws", "lambda", "s3", "ec2", "docker", "kubernetes"],
    "data": ["data analysis", "analytics", "bi", "tableau", "power bi"],
    "testing": ["pytest", "playwright", "cypress", "unit testing", "qa"],
}

DEFAULT_JOB_TITLES = [
    "AI Automation Engineer",
    "Python Developer",
    "Full Stack Engineer",
    "Backend Engineer",
    "Data Analyst",
    "ML Engineer",
    "Automation Engineer",
    "Product Analyst",
    "DevOps Engineer",
    "QA Automation Engineer",
]


class JobResult(BaseModel):
    id: str
    title: str
    company: str
    location: str
    remote: bool
    salary: str | None = None
    url: str
    description: str
    required_skills: list[str]
    match_score: int
    match_reason: str


class CandidateProfile(BaseModel):
    professional_title: str
    seniority: str
    years_experience: int
    skills: list[str]
    tools: list[str]
    industries: list[str]
    job_titles: list[str]


class CVAnalysisResponse(BaseModel):
    candidate: CandidateProfile
    jobs: list[JobResult]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(__import__("io").BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(__import__("io").BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def extract_text_from_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")


def extract_text(file_name: str, file_bytes: bytes) -> str:
    suffix = Path(file_name).suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(file_bytes)
    if suffix == ".docx":
        return extract_text_from_docx(file_bytes)
    if suffix in {".txt", ".md"}:
        return extract_text_from_txt(file_bytes)
    raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF, DOCX, or TXT.")


def detect_skills(text: str) -> list[str]:
    normalized = text.lower()
    found = []
    for label, keywords in SKILL_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            found.append(label)
    return sorted(found)


def infer_title(text: str, skills: list[str]) -> str:
    title_candidates = []
    for keyword, labels in SKILL_KEYWORDS.items():
        if keyword in skills:
            title_candidates.append(keyword)
    if not title_candidates:
        title_candidates = ["software", "data", "product"]
    if "ai" in skills or "machine learning" in text.lower():
        return "AI Automation Engineer"
    if "python" in skills and "automation" in skills:
        return "AI Automation Engineer"
    if "python" in skills:
        return "Python Developer"
    if "javascript" in skills:
        return "Full Stack Engineer"
    if "data" in skills:
        return "Data Analyst"
    if "aws" in skills:
        return "DevOps Engineer"
    return DEFAULT_JOB_TITLES[0]


def estimate_years_experience(text: str) -> int:
    matches = re.findall(r"(\d+)\s*(?:years?|yrs?)(?:\s+of)?\s+experience", text.lower())
    if matches:
        return int(matches[0])
    experience_years = re.findall(r"\b(\d{1,2})\b", text)
    for year in experience_years:
        if 1 <= int(year) <= 15:
            return int(year)
    return 2


def infer_seniority(years: int) -> str:
    if years >= 6:
        return "Senior"
    if years >= 3:
        return "Mid"
    return "Junior"


def infer_tools(text: str) -> list[str]:
    tools = ["Python", "FastAPI", "SQL", "GitHub", "Docker", "React", "PostgreSQL"]
    lower = text.lower()
    found = []
    for tool in tools:
        if tool.lower() in lower:
            found.append(tool)
    return found[:5]


def extract_candidate_profile(raw_text: str) -> dict[str, Any]:
    text = normalize_text(raw_text)
    skills = detect_skills(text)
    title = infer_title(text, skills)
    years = estimate_years_experience(text)
    tools = infer_tools(text)
    profile = {
        "professional_title": title,
        "seniority": infer_seniority(years),
        "years_experience": years,
        "skills": skills,
        "tools": tools,
        "industries": ["Technology", "Remote-first"],
        "job_titles": [
            title,
            "Automation Engineer",
            "Python Developer",
            "AI Engineer",
            "Remote Software Engineer",
        ],
    }
    return profile


def load_jobs() -> list[dict[str, Any]]:
    if not JOB_CACHE_PATH.exists():
        return []
    with JOB_CACHE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def compute_match_score(profile: dict[str, Any], job: dict[str, Any]) -> tuple[int, str]:
    candidate_skills = {skill.lower() for skill in profile["skills"]}
    required_skills = {skill.lower() for skill in job.get("required_skills", [])}
    overlap = candidate_skills & required_skills
    title_overlap = 1 if any(title.lower() in job.get("title", "").lower() for title in profile["job_titles"]) else 0
    score = min(98, 30 + (len(overlap) * 18) + (title_overlap * 18))
    if score > 80:
        reason = "Strong skill overlap with the requested role and relevant tools."
    elif score > 60:
        reason = "Good technical match with a few additional qualifications to confirm."
    else:
        reason = "Useful adjacent experience but not a direct fit for the core role."
    return score, reason


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze-cv", response_model=CVAnalysisResponse)
async def analyze_cv(file: UploadFile = File(...)) -> dict[str, Any]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    content = await file.read()
    parsed_text = extract_text(file.filename, content)
    if not parsed_text.strip():
        raise HTTPException(status_code=400, detail="The uploaded file did not contain readable text.")

    profile = extract_candidate_profile(parsed_text)
    jobs = load_jobs()
    scored_jobs = []
    for job in jobs:
        score, reason = compute_match_score(profile, job)
        if job.get("remote") is False:
            continue
        scored_jobs.append({
            **job,
            "match_score": score,
            "match_reason": reason,
        })

    scored_jobs.sort(key=lambda item: item["match_score"], reverse=True)
    top_jobs = scored_jobs[:10]
    return {
        "candidate": profile,
        "jobs": top_jobs,
    }
