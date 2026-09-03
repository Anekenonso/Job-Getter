from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_analyze_cv_returns_ranked_jobs():
    sample_cv = b"""Senior Python engineer with 6 years of experience in AI, automation, FastAPI, and SQL.\nBuilt production APIs, ETL workflows, and ML tooling in AWS and Docker.\n"""

    response = client.post(
        "/api/analyze-cv",
        files={"file": ("cv.txt", sample_cv, "text/plain")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["candidate"]["professional_title"] in {"AI Automation Engineer", "Python Developer"}
    assert len(payload["jobs"]) == 10
    assert payload["jobs"][0]["match_score"] >= payload["jobs"][-1]["match_score"]


def test_analyze_cv_rejects_large_files():
    large_payload = b"A" * (11 * 1024 * 1024)

    response = client.post(
        "/api/analyze-cv",
        files={"file": ("large.txt", large_payload, "text/plain")},
    )

    assert response.status_code == 413
