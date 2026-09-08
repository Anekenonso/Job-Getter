"""Normalize raw job payloads from different sources into the internal `Job`.

Each source (Jobicy, Remotive, Arbeitnow, or the seeded cache) has its own field
names. These adapters map them onto one schema so the rest of the pipeline never
needs to know where a job came from. Nothing is invented: missing salary stays
None, and we never fabricate an application URL.
"""

from __future__ import annotations

import hashlib
import re

from app.models.job import Job

# Common phrasings that signal a geographic restriction on an otherwise-remote role.
_RESTRICTION_PATTERNS = [
    (re.compile(r"\bus[\s-]*only\b", re.I), "US only"),
    (re.compile(r"\bunited states only\b", re.I), "US only"),
    (re.compile(r"\bus[\s-]*based\b", re.I), "US only"),
    (re.compile(r"\beu[\s-]*only\b", re.I), "EU only"),
    (re.compile(r"\beurope only\b", re.I), "EU only"),
    (re.compile(r"\buk[\s-]*only\b", re.I), "UK only"),
    (re.compile(r"\bcanada only\b", re.I), "Canada only"),
]

_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    return re.sub(r"\s+", " ", _TAG_RE.sub(" ", text or "")).strip()


def _make_id(source: str, url: str, title: str) -> str:
    digest = hashlib.sha1(f"{source}|{url}|{title}".encode()).hexdigest()[:12]
    return f"{source.lower()}-{digest}"


def detect_restriction(*texts: str) -> str | None:
    blob = " ".join(t for t in texts if t)
    for pattern, label in _RESTRICTION_PATTERNS:
        if pattern.search(blob):
            return label
    return None


def _split_skills(raw) -> list[str]:
    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, str):
        items = re.split(r"[,/|]", raw)
    else:
        items = []
    seen, out = set(), []
    for item in items:
        skill = str(item).strip().lower()
        if skill and skill not in seen:
            seen.add(skill)
            out.append(skill)
    return out


def from_jobicy(raw: dict) -> Job:
    location = raw.get("jobGeo") or "Anywhere"
    description = _strip_html(raw.get("jobExcerpt") or raw.get("jobDescription") or "")
    url = raw.get("url") or raw.get("jobUrl") or ""
    title = raw.get("jobTitle") or "Untitled role"
    return Job(
        id=_make_id("jobicy", url, title),
        title=title,
        company=raw.get("companyName") or "Unknown",
        location=location or "Remote",
        remote=True,
        location_restriction=detect_restriction(location, description),
        salary=_salary_range(raw.get("annualSalaryMin"), raw.get("annualSalaryMax"), raw.get("salaryCurrency")),
        description=description,
        required_skills=_split_skills(raw.get("jobIndustry")),
        source="Jobicy",
        url=url,
        date_posted=(raw.get("pubDate") or "")[:10] or None,
    )


def from_remotive(raw: dict) -> Job:
    description = _strip_html(raw.get("description") or "")
    location = raw.get("candidate_required_location") or "Anywhere"
    url = raw.get("url") or ""
    title = raw.get("title") or "Untitled role"
    return Job(
        id=_make_id("remotive", url, title),
        title=title,
        company=raw.get("company_name") or "Unknown",
        location=location,
        remote=True,
        location_restriction=detect_restriction(location, description),
        salary=(raw.get("salary") or "").strip() or None,
        description=description,
        required_skills=_split_skills(raw.get("tags")),
        source="Remotive",
        url=url,
        date_posted=(raw.get("publication_date") or "")[:10] or None,
    )


def from_arbeitnow(raw: dict) -> Job:
    description = _strip_html(raw.get("description") or "")
    location = raw.get("location") or "Anywhere"
    url = raw.get("url") or ""
    title = raw.get("title") or "Untitled role"
    tags = raw.get("tags") or []
    return Job(
        id=_make_id("arbeitnow", url, title),
        title=title,
        company=raw.get("company_name") or "Unknown",
        location=location,
        remote=bool(raw.get("remote", True)),
        location_restriction=detect_restriction(location, description),
        salary=None,
        description=description,
        required_skills=_split_skills(tags),
        source="Arbeitnow",
        url=url,
        date_posted=None,
    )


def from_cache(raw: dict) -> Job:
    """Adapter for our own seeded/cached schema (already close to `Job`)."""
    return Job(
        id=raw.get("id") or _make_id(raw.get("source", "cache"), raw.get("url", ""), raw.get("title", "")),
        title=raw.get("title", "Untitled role"),
        company=raw.get("company", "Unknown"),
        location=raw.get("location", "Remote"),
        remote=raw.get("remote", True),
        location_restriction=raw.get("location_restriction") or detect_restriction(
            raw.get("location", ""), raw.get("description", "")
        ),
        salary=raw.get("salary"),
        description=raw.get("description", ""),
        required_skills=_split_skills(raw.get("required_skills")),
        requirements=raw.get("requirements", []),
        source=raw.get("source", "Cache"),
        url=raw.get("url", ""),
        date_posted=raw.get("date_posted"),
    )


def _salary_range(low, high, currency) -> str | None:
    if not low and not high:
        return None
    symbol = {"USD": "$", "EUR": "€", "GBP": "£"}.get((currency or "").upper(), "")
    if low and high:
        return f"{symbol}{int(low):,} - {symbol}{int(high):,}"
    value = low or high
    return f"{symbol}{int(value):,}"


def dedupe(jobs: list[Job]) -> list[Job]:
    """Drop duplicate postings, keyed on normalized title + company."""
    seen, out = set(), []
    for job in jobs:
        key = (job.title.strip().lower(), job.company.strip().lower())
        if key not in seen:
            seen.add(key)
            out.append(job)
    return out
