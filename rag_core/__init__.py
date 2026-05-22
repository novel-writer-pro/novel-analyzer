"""Reusable RAG core contracts and lightweight adapter protocols.

This package intentionally starts small: shared contracts and protocols only.
Novel-specific orchestration, graph semantics, and adapter implementations stay
in ``novel_analyzer`` until later extraction steps.
"""

from .contracts import (
    RetrievalHit,
    RetrievalPreferences,
    RetrievalRouteDiagnostics,
    RetrievalSearchDiagnostics,
    StructuredQueryPlan,
)
from .protocols import CorpusAdapter, GraphAdapter

__all__ = [
    "CorpusAdapter",
    "GraphAdapter",
    "RetrievalHit",
    "RetrievalPreferences",
    "RetrievalRouteDiagnostics",
    "RetrievalSearchDiagnostics",
    "StructuredQueryPlan",
]
