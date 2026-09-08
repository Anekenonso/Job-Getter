"""API-level tests covering the full pipeline through the HTTP layer."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

STRONG_CV = (
    b"Senior Python engineer with 6 years of experience in AI, automation, "
    b"FastAPI, and SQL. Built production APIs, ETL workflows, and ML tooling "
    b"in AWS and Docker. Bachelor's degree in Computer Science."
)


def test_analyze_cv_returns_ranked_matches():
    response = client.post(
        "/api/analyze-cv",
        files={"file": ("cv.txt", STRONG_CV, "text/plain")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["candidate"]["professional_title"] in {
        "AI Automation Engineer",
        "Python Developer",
    }
    jobs = payload["jobs"]
    assert 1 <= len(jobs) <= 10
    # Results are sorted by descending match score.
    scores = [job["match_score"] for job in jobs]
    assert scores == sorted(scores, reverse=True)
    # Every result carries an application URL (anti-hallucination requirement).
    assert all(job["url"] for job in jobs)


def test_analyze_cv_rejects_large_files():
    large_payload = b"A" * (11 * 1024 * 1024)
    response = client.post(
        "/api/analyze-cv",
        files={"file": ("large.txt", large_payload, "text/plain")},
    )
    assert response.status_code == 413


def test_analyze_cv_rejects_unsupported_type():
    response = client.post(
        "/api/analyze-cv",
        files={"file": ("cv.png", b"not a real cv", "image/png")},
    )
    assert response.status_code == 400


def test_analyze_cv_handles_poor_cv():
    response = client.post(
        "/api/analyze-cv",
        files={"file": ("cv.txt", b"hi", "text/plain")},
    )
    assert response.status_code == 422


def test_find_jobs_endpoint():
    profile = {
        "professional_title": "Python Developer",
        "seniority": "Mid",
        "years_experience": 4,
        "skills": ["python", "sql", "apis"],
        "tools": ["FastAPI"],
        "industries": ["Technology"],
        "job_titles": ["Python Developer", "Backend Engineer"],
    }
    response = client.post(
        "/api/find-jobs",
        json={"candidate_profile": profile},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "jobs" in payload
    assert "strong_count" in payload


def test_search_again_excludes_seen_jobs():
    profile = {
        "professional_title": "Python Developer",
        "seniority": "Mid",
        "years_experience": 4,
        "skills": ["python", "sql", "apis", "automation"],
        "tools": ["FastAPI"],
        "industries": ["Technology"],
        "job_titles": ["Python Developer", "Backend Engineer"],
    }
    first = client.post("/api/find-jobs", json={"candidate_profile": profile}).json()
    seen = [job["id"] for job in first["jobs"]]

    again = client.post(
        "/api/search-again",
        json={"candidate_profile": profile, "exclude_ids": seen, "variation": 1},
    ).json()
    again_ids = {job["id"] for job in again["jobs"]}
    # No repeat of already-seen jobs.
    assert again_ids.isdisjoint(set(seen))
