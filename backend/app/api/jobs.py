"""Job search routes: find-jobs and search-again."""

from __future__ import annotations

from fastapi import APIRouter

from app import pipeline
from app.api.responses import build_message
from app.api.schemas import FindJobsRequest, JobsResponse

router = APIRouter(prefix="/api", tags=["jobs"])


def _run(request: FindJobsRequest, variation: int) -> JobsResponse:
    result = pipeline.find_jobs(
        request.candidate_profile,
        exclude_ids=set(request.exclude_ids),
        variation=variation,
    )
    strong = result["strong"]
    possible = result["possible"]
    return JobsResponse(
        jobs=strong,
        possible_matches=possible,
        strong_count=result["strong_count"],
        message=build_message(len(strong), len(possible)),
    )


@router.post("/find-jobs", response_model=JobsResponse)
async def find_jobs(request: FindJobsRequest) -> JobsResponse:
    return _run(request, variation=request.variation)


@router.post("/search-again", response_model=JobsResponse)
async def search_again(request: FindJobsRequest) -> JobsResponse:
    """Varied re-search for the same session. Excludes already-seen jobs and
    rotates the query order so results differ while staying relevant."""
    variation = request.variation or 1
    return _run(request, variation=variation)
