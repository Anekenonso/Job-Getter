"""Thin Groq LLM client.

Wraps Groq's OpenAI-compatible chat-completions endpoint. The whole module is
optional: if no API key is configured (or the call fails/times out), callers are
expected to fall back to deterministic heuristics. This keeps the product fully
functional at $0 while allowing an AI upgrade by simply setting GROQ_API_KEY.
"""

from __future__ import annotations

import json
import logging

import httpx

from app import config

logger = logging.getLogger(__name__)


class LLMUnavailable(RuntimeError):
    """Raised when the LLM cannot be used, so callers fall back to heuristics."""


def is_enabled() -> bool:
    return config.LLM_ENABLED


def complete_json(system_prompt: str, user_prompt: str) -> dict:
    """Send a prompt to Groq and parse a JSON object from the response.

    Raises LLMUnavailable on any problem (disabled, network, timeout, bad JSON)
    so the caller can degrade gracefully.
    """
    if not config.LLM_ENABLED:
        raise LLMUnavailable("LLM disabled or no API key configured.")

    payload = {
        "model": config.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {config.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=config.LLM_TIMEOUT_SECONDS) as client:
            response = client.post(
                f"{config.GROQ_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)
    except (httpx.HTTPError, KeyError, IndexError, json.JSONDecodeError) as exc:
        logger.warning("Groq call failed, falling back to heuristics: %s", exc)
        raise LLMUnavailable(str(exc)) from exc
