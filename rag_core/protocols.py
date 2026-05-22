"""Adapter protocols for the reusable RAG core."""

from __future__ import annotations

from typing import Protocol

from .contracts import RetrievalHit, StructuredQueryPlan


class CorpusAdapter(Protocol):
    """Protocol for domain-specific corpus access.

    The core retriever can depend on this protocol instead of novel-specific ORM
    models. Graph is intentionally excluded here.
    """

    def search_evidence(self, scope_id: str, query_plan: StructuredQueryPlan, *, limit: int) -> list[RetrievalHit]:
        """Return domain-scoped evidence hits for a structured query."""


class GraphAdapter(Protocol):
    """Optional graph augmentation protocol.

    Implementations are domain-specific and may be omitted entirely in graph-free
    deployments.
    """

    def search_graph(self, scope_id: str, query_plan: StructuredQueryPlan, *, limit: int) -> list[RetrievalHit]:
        """Return graph-derived evidence hits for a structured query."""
