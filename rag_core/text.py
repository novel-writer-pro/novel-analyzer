"""Shared text formatting helpers for reusable retrieval pipelines."""

from __future__ import annotations

from .contracts import RetrievalHit


def build_rerank_text(hit: RetrievalHit, *, char_limit: int) -> str:
    """Build a clipped rerank payload from a retrieval hit."""

    keywords = ", ".join(hit.keyword_list[:8])
    text = "\n".join(part for part in [hit.title.strip(), hit.summary_text.strip(), keywords.strip()] if part)
    if len(text) <= char_limit:
        return text
    clipped = text[:char_limit].rstrip("，。；;、, \n")
    return clipped + "…"
