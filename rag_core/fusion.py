"""Shared fusion helpers for reusable retrieval pipelines."""

from __future__ import annotations

from .contracts import RetrievalHit


def reciprocal_rank_fuse(
    ranked_lists: list[list[RetrievalHit]],
    *,
    limit: int,
    k: int = 60,
) -> list[RetrievalHit]:
    """Fuse multiple ranked recall lists with reciprocal-rank fusion.

    A single recall lane is returned unchanged to keep downstream score
    expectations stable. Multi-lane callers get deterministic chapter-level
    de-duping and fused scores.
    """

    non_empty_lists = [hits for hits in ranked_lists if hits]
    if not non_empty_lists:
        return []
    if len(non_empty_lists) == 1:
        return non_empty_lists[0][:limit]

    fused_scores: dict[int, float] = {}
    best_hits: dict[int, RetrievalHit] = {}
    best_source_scores: dict[int, float] = {}
    best_ranks: dict[int, int] = {}
    for hits in non_empty_lists:
        seen_in_lane: set[int] = set()
        for rank, hit in enumerate(hits, start=1):
            if hit.chapter_index in seen_in_lane:
                continue
            seen_in_lane.add(hit.chapter_index)
            fused_scores[hit.chapter_index] = fused_scores.get(hit.chapter_index, 0.0) + 1.0 / (k + rank)
            previous_best_score = best_source_scores.get(hit.chapter_index, float("-inf"))
            previous_best_rank = best_ranks.get(hit.chapter_index, 10**9)
            if hit.score > previous_best_score or (hit.score == previous_best_score and rank < previous_best_rank):
                best_hits[hit.chapter_index] = hit
                best_source_scores[hit.chapter_index] = hit.score
                best_ranks[hit.chapter_index] = rank

    ordered_chapter_indexes = sorted(
        fused_scores,
        key=lambda chapter_index: (-fused_scores[chapter_index], best_ranks[chapter_index], chapter_index),
    )
    return [
        RetrievalHit(
            chapter_index=best_hits[chapter_index].chapter_index,
            title=best_hits[chapter_index].title,
            summary_text=best_hits[chapter_index].summary_text,
            score=fused_scores[chapter_index],
            keyword_list=best_hits[chapter_index].keyword_list,
        )
        for chapter_index in ordered_chapter_indexes[:limit]
    ]
