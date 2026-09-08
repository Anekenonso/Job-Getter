"""Central configuration for the Job-Getter backend.

Everything that a deployer or product owner might reasonably want to tune lives
here so it is never hard-coded across the pipeline. Values can be overridden
through environment variables, which keeps secrets (API keys) and per-environment
settings (CORS origins) out of the codebase.
"""

from __future__ import annotations

import os
from pathlib import Path

# --- Paths -------------------------------------------------------------------

APP_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = APP_ROOT / "data"
JOB_CACHE_PATH = DATA_DIR / "jobs_cache.json"


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def _env_list(name: str, default: list[str]) -> list[str]:
    raw = os.getenv(name)
    if not raw:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


# --- Upload constraints ------------------------------------------------------

MAX_FILE_SIZE_MB = _env_int("MAX_FILE_SIZE_MB", 5)
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_SUFFIXES = {".pdf", ".docx", ".txt"}

# --- Results -----------------------------------------------------------------

TOP_N_RESULTS = _env_int("TOP_N_RESULTS", 10)
# A job must clear this score to count as a "strong" match. Below it, the job is
# offered separately as a "possible" match rather than padding the top list.
STRONG_MATCH_THRESHOLD = _env_int("STRONG_MATCH_THRESHOLD", 65)
# How many shortlisted jobs get sent to the (expensive) matcher. Keeps LLM cost
# bounded per the cost-control strategy in the spec.
MATCH_SHORTLIST_SIZE = _env_int("MATCH_SHORTLIST_SIZE", 25)

# --- Match weights -----------------------------------------------------------
# Sum to 1.0. These mirror the spec's scoring rubric and can be retuned without
# touching the matching code.

MATCH_WEIGHTS = {
    "skills": 0.30,
    "experience": 0.25,
    "role_similarity": 0.20,
    "seniority": 0.10,
    "education": 0.05,
    "industry": 0.05,
    "location": 0.05,
}

# --- LLM ---------------------------------------------------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
LLM_TIMEOUT_SECONDS = _env_int("LLM_TIMEOUT_SECONDS", 30)
# When false (or no key present) the pipeline falls back to deterministic
# heuristics, so the product works end-to-end with zero external dependencies.
LLM_ENABLED = bool(GROQ_API_KEY) and os.getenv("LLM_ENABLED", "1") != "0"

# --- CORS --------------------------------------------------------------------

CORS_ALLOW_ORIGINS = _env_list(
    "CORS_ALLOW_ORIGINS",
    ["http://localhost:3000", "http://127.0.0.1:3000"],
)

# --- Rate limiting -----------------------------------------------------------

RATE_LIMIT_REQUESTS = _env_int("RATE_LIMIT_REQUESTS", 20)
RATE_LIMIT_WINDOW_SECONDS = _env_int("RATE_LIMIT_WINDOW_SECONDS", 60)

# --- Request timeouts --------------------------------------------------------

REQUEST_TIMEOUT_SECONDS = _env_int("REQUEST_TIMEOUT_SECONDS", 120)
