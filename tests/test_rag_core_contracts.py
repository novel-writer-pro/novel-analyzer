from typing import runtime_checkable, Protocol


def test_rag_core_package_exports_shared_contracts() -> None:
    from rag_core import (
        CorpusAdapter,
        GraphAdapter,
        RetrievalHit,
        RetrievalPreferences,
        StructuredQueryPlan,
    )

    hit = RetrievalHit(
        chapter_index=1,
        title="Title",
        summary_text="Summary",
        score=0.5,
        keyword_list=["kw"],
    )
    plan = StructuredQueryPlan(
        raw_question="What happened?",
        normalized_question="What happened?",
    )
    prefs = RetrievalPreferences()

    assert hit.chapter_index == 1
    assert plan.question_type == "general"
    assert prefs.lanes == ["fts", "fact", "graph", "vector", "window"]
    assert CorpusAdapter is not None
    assert GraphAdapter is not None


def test_rag_core_adapter_protocols_make_graph_optional() -> None:
    from rag_core import CorpusAdapter, GraphAdapter

    assert getattr(CorpusAdapter, "__name__", "") == "CorpusAdapter"
    assert getattr(GraphAdapter, "__name__", "") == "GraphAdapter"


def test_existing_novel_schemas_remain_importable() -> None:
    from novel_analyzer.domain.schemas import StructuredQueryPlan as NovelStructuredQueryPlan
    from novel_analyzer.services.retrieval_service import RetrievalHit as NovelRetrievalHit

    plan = NovelStructuredQueryPlan(
        raw_question="卫图前20章如何推进？",
        normalized_question="卫图前20章如何推进？",
    )
    hit = NovelRetrievalHit(
        chapter_index=1,
        title="命格初现",
        summary_text="卫图觉醒命格",
        score=1.0,
        keyword_list=["卫图"],
    )

    assert plan.question_type == "general"
    assert hit.title == "命格初现"


def test_retrieval_service_reuses_rag_core_hit_contract() -> None:
    from rag_core import RetrievalHit as CoreRetrievalHit
    from novel_analyzer.services.retrieval_service import RetrievalHit as ServiceRetrievalHit

    assert ServiceRetrievalHit is CoreRetrievalHit


def test_rag_core_exports_retrieval_diagnostics_contracts() -> None:
    from rag_core import RetrievalHit, RetrievalRouteDiagnostics, RetrievalSearchDiagnostics

    route = RetrievalRouteDiagnostics(route="fts", hit_count=3, latency_ms=12.5)
    report = RetrievalSearchDiagnostics(
        query="卫图",
        raw_hits=[RetrievalHit(chapter_index=1, title="一", summary_text="命格初现", score=1.0, keyword_list=[])],
        reranked_hits=[],
        rerank_applied=False,
    )

    assert route.route == "fts"
    assert report.query == "卫图"
    assert report.raw_hits[0].title == "一"


def test_retrieval_service_reuses_rag_core_diagnostics_contracts() -> None:
    from rag_core import RetrievalRouteDiagnostics as CoreRouteDiagnostics
    from rag_core import RetrievalSearchDiagnostics as CoreSearchDiagnostics
    from novel_analyzer.services.retrieval_service import RetrievalRouteDiagnostics as ServiceRouteDiagnostics
    from novel_analyzer.services.retrieval_service import RetrievalSearchDiagnostics as ServiceSearchDiagnostics

    assert ServiceRouteDiagnostics is CoreRouteDiagnostics
    assert ServiceSearchDiagnostics is CoreSearchDiagnostics


def test_rag_core_exports_query_planning_contracts() -> None:
    from rag_core import RetrievalPreferences, StructuredQueryPlan

    prefs = RetrievalPreferences()
    plan = StructuredQueryPlan(
        raw_question="What happened?",
        normalized_question="What happened?",
        retrieval_plan=prefs,
    )

    assert prefs.lanes == ["fts", "fact", "graph", "vector", "window"]
    assert plan.retrieval_plan is prefs
    assert plan.question_type == "general"


def test_novel_query_planning_contracts_reuse_rag_core_types() -> None:
    from rag_core import RetrievalPreferences as CoreRetrievalPreferences
    from rag_core import StructuredQueryPlan as CoreStructuredQueryPlan
    from novel_analyzer.domain.schemas import RetrievalPreferences as NovelRetrievalPreferences
    from novel_analyzer.domain.schemas import StructuredQueryPlan as NovelStructuredQueryPlan

    assert NovelRetrievalPreferences is CoreRetrievalPreferences
    assert NovelStructuredQueryPlan is CoreStructuredQueryPlan


def test_rag_core_exports_reciprocal_rank_fusion_helper() -> None:
    from rag_core import RetrievalHit, reciprocal_rank_fuse

    route_hits = [
        [
            RetrievalHit(chapter_index=1, title="一", summary_text="命格初现", score=10.0, keyword_list=[]),
            RetrievalHit(chapter_index=2, title="二", summary_text="弱相关", score=9.0, keyword_list=[]),
        ],
        [
            RetrievalHit(chapter_index=2, title="二", summary_text="弱相关", score=1.0, keyword_list=[]),
            RetrievalHit(chapter_index=1, title="一", summary_text="命格初现", score=0.5, keyword_list=[]),
        ],
    ]

    fused = reciprocal_rank_fuse(route_hits, limit=2)

    assert [hit.chapter_index for hit in fused] == [1, 2]


def test_retrieval_service_uses_rag_core_reciprocal_rank_fusion() -> None:
    from rag_core.fusion import reciprocal_rank_fuse as core_rrf
    from novel_analyzer.services.retrieval_service import RetrievalService

    assert RetrievalService._fuse_recall_lists is core_rrf


def test_rag_core_exports_rerank_helper() -> None:
    from rag_core import RetrievalHit, apply_rerank_scores

    hits = [
        RetrievalHit(chapter_index=1, title="一", summary_text="弱相关", score=0.8, keyword_list=["卫图"]),
        RetrievalHit(chapter_index=2, title="二", summary_text="强相关", score=0.1, keyword_list=["命格"]),
    ]

    reranked = apply_rerank_scores(hits, [0.2, 0.9], limit=2)

    assert [hit.chapter_index for hit in reranked] == [2, 1]
    assert reranked[0].score == 0.9


def test_retrieval_service_uses_rag_core_rerank_helper() -> None:
    from rag_core.rerank import apply_rerank_scores as core_rerank
    from novel_analyzer.services.retrieval_service import RetrievalService

    assert RetrievalService._apply_rerank_scores is core_rerank
