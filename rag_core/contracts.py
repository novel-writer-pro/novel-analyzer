"""Shared RAG contracts for reusable, graph-optional retrieval pipelines."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class RetrievalHit:
    """A normalized retrieval hit independent of domain-specific adapters."""

    chapter_index: int
    title: str
    summary_text: str
    score: float
    keyword_list: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class RetrievalRouteDiagnostics:
    """Per-route diagnostics for latency and contribution checks."""

    route: str
    hit_count: int
    latency_ms: float


@dataclass(frozen=True, slots=True)
class RetrievalSearchDiagnostics:
    """Raw, fused, and reranked retrieval views for inspection/evaluation."""

    query: str
    raw_hits: list[RetrievalHit]
    reranked_hits: list[RetrievalHit]
    rerank_applied: bool
    fusion_applied: bool = False
    route_counts: dict[str, int] | None = None
    route_diagnostics: list[RetrievalRouteDiagnostics] | None = None
    raw_latency_ms: float = 0.0
    rerank_latency_ms: float = 0.0


@dataclass(frozen=True, slots=True)
class RetrievalPreferences:
    """High-level retrieval planning hints for downstream pipelines."""

    lanes: list[str] = field(default_factory=lambda: ["fts", "fact", "graph", "vector", "window"])
    prefer_graph: bool = False
    prefer_timeline: bool = False
    prefer_window: bool = False
    prefer_causal: bool = False
    prefer_foreshadow: bool = False
    candidate_limit: int = 24
    final_limit: int = 6


@dataclass(frozen=True, slots=True)
class StructuredQueryPlan:
    """Minimal reusable query-understanding contract.

    Domain adapters may enrich this with additional fields locally, but the core
    starts with a graph-optional, domain-agnostic baseline.
    """

    raw_question: str
    normalized_question: str
    question_type: str = "general"
    intent: str = "locate_fact"
    answer_expectation: str = "direct_fact"
    retrieval_plan: RetrievalPreferences = field(default_factory=RetrievalPreferences)
