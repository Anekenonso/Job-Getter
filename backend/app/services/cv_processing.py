"""Turn an uploaded CV file into plain text.

Pure I/O + text extraction. No interpretation happens here — that is the CV
parser agent's job. Files are handled in memory only and never written to disk,
satisfying the no-persistent-storage requirement.
"""

from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

from docx import Document
from fastapi import HTTPException
from pypdf import PdfReader

from app.config import ALLOWED_SUFFIXES, MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _extract_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(p for p in pages if p)


def _extract_docx(file_bytes: bytes) -> str:
    doc = Document(BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def _extract_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")


def validate_upload(file_name: str, file_bytes: bytes) -> None:
    if not file_name:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    suffix = Path(file_name).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail="We couldn't read this file. Please upload a PDF or DOCX CV.",
        )
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {MAX_FILE_SIZE_MB} MB limit.",
        )


def extract_text(file_name: str, file_bytes: bytes) -> str:
    suffix = Path(file_name).suffix.lower()
    try:
        if suffix == ".pdf":
            text = _extract_pdf(file_bytes)
        elif suffix == ".docx":
            text = _extract_docx(file_bytes)
        elif suffix == ".txt":
            text = _extract_txt(file_bytes)
        else:
            raise HTTPException(
                status_code=400,
                detail="We couldn't read this file. Please upload a PDF or DOCX CV.",
            )
    except HTTPException:
        raise
    except Exception:
        # Corrupt/unreadable file of an otherwise-supported type.
        raise HTTPException(
            status_code=400,
            detail="We couldn't read this file. Please upload a PDF or DOCX CV.",
        )
    return normalize_text(text)
