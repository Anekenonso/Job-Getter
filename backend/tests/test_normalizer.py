"""Tests for source normalization and dedupe."""

from app.services import job_normalizer


def test_jobicy_normalization():
    raw = {
        "jobTitle": "Backend Engineer",
        "companyName": "Acme",
        "jobGeo": "USA",
        "jobExcerpt": "<p>Build <b>APIs</b></p>",
        "url": "https://jobicy.com/j/1",
        "annualSalaryMin": 100000,
        "annualSalaryMax": 140000,
        "salaryCurrency": "USD",
        "pubDate": "2026-09-01 10:00:00",
    }
    job = job_normalizer.from_jobicy(raw)
    assert job.title == "Backend Engineer"
    assert job.company == "Acme"
    assert job.source == "Jobicy"
    assert "APIs" in job.description
    assert "<" not in job.description  # HTML stripped
    assert job.salary == "$100,000 - $140,000"
    assert job.date_posted == "2026-09-01"
    assert job.url


def test_detect_restriction():
    assert job_normalizer.detect_restriction("Remote US only") == "US only"
    assert job_normalizer.detect_restriction("EU only role") == "EU only"
    assert job_normalizer.detect_restriction("Remote worldwide") is None


def test_dedupe_removes_duplicate_title_company():
    from app.models.job import Job

    jobs = [
        Job(id="1", title="Dev", company="Acme", remote=True, url="http://a"),
        Job(id="2", title="dev", company="ACME", remote=True, url="http://b"),
        Job(id="3", title="Dev", company="Other", remote=True, url="http://c"),
    ]
    deduped = job_normalizer.dedupe(jobs)
    assert len(deduped) == 2


def test_missing_salary_stays_none():
    raw = {"title": "Dev", "company_name": "X", "url": "http://x", "tags": ["python"]}
    job = job_normalizer.from_remotive(raw)
    assert job.salary is None
