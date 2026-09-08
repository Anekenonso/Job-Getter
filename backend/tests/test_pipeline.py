"""Unit tests for the agent pipeline across a range of CV scenarios."""

from app.agents import cv_parser, job_filter, job_matcher, ranking
from app.models.candidate import CandidateProfile
from app.models.job import Job


def test_parser_extracts_junior_profile():
    text = (
        "Junior frontend developer with 1 year of experience building React "
        "and TypeScript interfaces with Tailwind CSS."
    )
    profile = cv_parser.parse(text)
    assert profile.seniority == "Junior"
    assert "frontend" in profile.skills or "javascript" in profile.skills


def test_parser_extracts_senior_profile():
    text = (
        "Senior data engineer with 8 years of experience in Python, SQL, and "
        "analytics. Led BI dashboards and ETL automation."
    )
    profile = cv_parser.parse(text)
    assert profile.seniority == "Senior"
    assert profile.years_experience >= 6


def test_poor_cv_has_insufficient_signal():
    text = "hello world"
    profile = cv_parser.parse(text)
    assert not cv_parser.has_enough_signal(text, profile)


def test_filter_drops_non_remote_jobs():
    profile = CandidateProfile(skills=["python"], job_titles=["Python Developer"])
    onsite = Job(id="1", title="Dev", company="X", remote=False, url="http://x")
    remote = Job(id="2", title="Dev", company="Y", remote=True, url="http://y")
    filtered = job_filter.filter_jobs(profile, [onsite, remote])
    assert [j.id for j in filtered] == ["2"]


def test_location_restriction_lowers_score_and_flags_gap():
    profile = CandidateProfile(
        skills=["python", "automation"],
        job_titles=["Automation Engineer"],
        years_experience=4,
        seniority="Mid",
    )
    restricted = Job(
        id="r",
        title="Automation Engineer",
        company="X",
        remote=True,
        location_restriction="US only",
        required_skills=["python", "automation"],
        url="http://x",
    )
    match = job_matcher.score(profile, restricted)
    assert any("US only" in gap for gap in match.gaps)


def test_matcher_reports_experience_gap():
    profile = CandidateProfile(
        skills=["python"], job_titles=["Python Developer"], years_experience=2, seniority="Junior"
    )
    job = Job(
        id="j",
        title="Python Developer",
        company="X",
        remote=True,
        required_skills=["python"],
        description="We need 5+ years of experience in Python.",
        url="http://x",
    )
    match = job_matcher.score(profile, job)
    assert any("years" in gap for gap in match.gaps)


def test_matcher_never_claims_unlisted_skill():
    profile = CandidateProfile(skills=["python"], job_titles=["Python Developer"])
    job = Job(
        id="j",
        title="Python Developer",
        company="X",
        remote=True,
        required_skills=["python", "rust", "golang"],
        url="http://x",
    )
    match = job_matcher.score(profile, job)
    matched_lower = {s.lower() for s in match.matching_skills}
    assert "rust" not in matched_lower
    assert "golang" not in matched_lower
    assert "python" in matched_lower


def test_ranking_splits_strong_and_possible():
    matches = [
        job_matcher.JobMatch.from_job(
            Job(id=str(i), title="T", company="C", remote=True, url="http://x"),
            match_score=score,
            match_reason="r",
        )
        for i, score in enumerate([90, 80, 70, 40, 30])
    ]
    result = ranking.rank(matches)
    assert result["strong_count"] == 3
    assert all(m.match_score >= 65 for m in result["strong"])
