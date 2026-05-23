"""Shared rerank helpers for reusable retrieval pipelines."""

from __future__ import annotations

from .contracts import RetrievalHit


def apply_rerank_scores(
    hits: list[RetrievalHit],
    rerank_scores: list[float],
    *,
    limit: int,
) -> list[RetrievalHit]:
    """Apply external rerank scores to an ordered hit list."""

    reranked = sorted(
        zip(hits, rerank_scores, strict=True),
        key=lambda item: (-item[1], -item[0].score, item[0].chapter_index),
    )
    return [
        RetrievalHit(
            chapter_index=hit.chapter_index,
            title=hit.title,
            summary_text=hit.summary_text,
            score=float(score),
            keyword_list=hit.keyword_list,
        )
        for hit, score in reranked[:limit]
    ]
