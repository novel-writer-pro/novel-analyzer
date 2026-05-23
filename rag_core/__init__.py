"""Reusable RAG core contracts and lightweight adapter protocols.

This package intentionally starts small: shared contracts and protocols only.
Novel-specific orchestration, graph semantics, and adapter implementations stay
in ``novel_analyzer`` until later extraction steps.
"""

from .contracts import (
    PlannedEntity,
    QueryConstraints,
    QueryTimeScope,
    RetrievalHit,
    RetrievalPreferences,
    RetrievalRouteDiagnostics,
    RetrievalSearchDiagnostics,
    StructuredQueryPlan,
)
from .fusion import reciprocal_rank_fuse
from .keywords import coerce_keywords
from .protocols import CorpusAdapter, GraphAdapter
from .rerank import apply_rerank_scores
from .text import build_rerank_text
from .vector import coerce_vector_payload, cosine_similarity

__all__ = [
    "CorpusAdapter",
    "GraphAdapter",
    "PlannedEntity",
    "QueryConstraints",
    "QueryTimeScope",
    "RetrievalHit",
    "RetrievalPreferences",
    "RetrievalRouteDiagnostics",
    "RetrievalSearchDiagnostics",
    "StructuredQueryPlan",
    "apply_rerank_scores",
    "build_rerank_text",
    "coerce_keywords",
    "coerce_vector_payload",
    "cosine_similarity",
    "reciprocal_rank_fuse",
]
