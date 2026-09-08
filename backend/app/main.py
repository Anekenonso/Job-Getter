"""Job-Getter FastAPI application entrypoint.

Thin composition root: it wires middleware and routers together. All business
logic lives in the agents/services/pipeline modules.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.api import jobs, upload
from app.middleware import RateLimitMiddleware

app = FastAPI(title="Job-Getter API", version="1.0.0")

# CORS: locked to the configured frontend origins rather than "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

app.include_router(upload.router)
app.include_router(jobs.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "llm": "enabled" if config.LLM_ENABLED else "heuristic"}
