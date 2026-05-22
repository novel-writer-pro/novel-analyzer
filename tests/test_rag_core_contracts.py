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
