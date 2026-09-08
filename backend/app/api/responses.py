"""Helpers for turning ranked pipeline output into API responses."""

from __future__ import annotations

from app import config


def build_message(strong_count: int, possible_count: int) -> str | None:
    """Honest messaging when we can't fill the full set of strong matches."""
    top_n = config.TOP_N_RESULTS
    if strong_count >= top_n:
        return None
    if strong_count == 0 and possible_count == 0:
        return (
            "We couldn't find strong remote matches right now. "
            "Try again shortly or upload a more detailed CV."
        )
    if strong_count == 0:
        return (
            f"We didn't find strong matches, but {possible_count} roles "
            "look potentially relevant."
        )
    return (
        f"We found {strong_count} strong "
        f"{'match' if strong_count == 1 else 'matches'} for your CV. "
        "We didn't fill the rest with poor matches."
    )
