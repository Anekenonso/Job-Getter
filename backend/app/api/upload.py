"""Upload / CV analysis routes."""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from app import pipeline
from app.api.responses import build_message
from app.api.schemas import AnalyzeResponse
from app.services import cv_processing

router = APIRouter(prefix="/api", tags=["cv"])


@router.post("/analyze-cv", response_model=AnalyzeResponse)
async def analyze_cv(file: UploadFile = File(...)) -> AnalyzeResponse:
    content = await file.read()
    cv_processing.validate_upload(file.filename, content)

    text = cv_processing.extract_text(file.filename, content)
    if not text:
        raise HTTPException(
            status_code=400,
            detail="We couldn't read this file. Please upload a PDF or DOCX CV.",
        )

    result = pipeline.analyze_and_match(text)

    if not result["enough_signal"]:
        raise HTTPException(
            status_code=422,
            detail=(
                "We couldn't extract enough professional information from this CV "
                "to find reliable matches. Try uploading a more detailed CV."
            ),
        )

    strong = result["strong"]
    possible = result["possible"]
    return AnalyzeResponse(
        candidate=result["candidate"],
        jobs=strong,
        possible_matches=possible,
        strong_count=result["strong_count"],
        message=build_message(len(strong), len(possible)),
    )
