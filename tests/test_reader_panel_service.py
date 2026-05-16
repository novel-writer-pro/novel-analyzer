"""Reader panel service unit tests.

Cover the parse / verdict / fallback paths without making real LLM calls.
"""

from __future__ import annotations

from unittest.mock import patch

from novel_analyzer.config.settings import Settings
from novel_analyzer.domain.schemas import ChapterImitationDraft
from novel_analyzer.services.reader_panel_service import (
    COMFORT_NEEDS_REWRITE_THRESHOLD,
    COMFORT_PASS_THRESHOLD,
    ReaderPanelService,
)


def _settings() -> Settings:
    return Settings(
        llm_provider_name="deepseek",
        llm_base_url="http://example.test/v1",
        llm_api_key="sk-test",
        llm_model_name="claude-haiku-4.5",
    )


def _draft(text: str, *, idx: int = 1) -> ChapterImitationDraft:
    return ChapterImitationDraft(
        source_chapter_index=idx,
        original_title="测试章",
        draft_title="测试章",
        draft_text=text,
    )


def test_short_draft_returns_fallback() -> None:
    svc = ReaderPanelService(_settings())
    rep = svc.evaluate_draft(_draft("太短了"))
    assert rep.comfort_score == 0
    assert rep.overall_verdict == "needs_rewrite"
    assert "too short" in rep.rejection_reason


def test_empty_draft_returns_fallback() -> None:
    svc = ReaderPanelService(_settings())
    rep = svc.evaluate_draft(_draft(""))
    assert rep.comfort_score == 0
    assert "too short" in rep.rejection_reason


def test_polished_verdict_when_high_comfort() -> None:
    payload = {
        "comfort_score": 82,
        "personas": [
            {"persona": "naive_reader", "score": 80, "feel": "好读", "strengths": [], "weaknesses": []},
            {"persona": "genre_veteran", "score": 75, "feel": "套路稳", "strengths": [], "weaknesses": []},
            {"persona": "editor", "score": 85, "feel": "节奏不错", "strengths": [], "weaknesses": []},
            {"persona": "prose_critic", "score": 78, "feel": "文笔可", "strengths": [], "weaknesses": []},
        ],
        "dimension_scores": [
            {"dimension": "对话生动度", "score": 80, "note": ""},
            {"dimension": "环境描写", "score": 75, "note": ""},
            {"dimension": "阅读舒适度", "score": 85, "note": ""},
            {"dimension": "文笔质感", "score": 78, "note": ""},
            {"dimension": "悬念强度", "score": 80, "note": ""},
            {"dimension": "支线管理", "score": 70, "note": ""},
            {"dimension": "特色（抗平白）", "score": 75, "note": ""},
        ],
        "targeted_revisions": [
            {"dim": "支线管理", "action": "加 1 处支线伏笔", "priority": 3},
        ],
        "verdict": "polished",
    }
    svc = ReaderPanelService(_settings())
    with patch.object(svc, "_call_llm", return_value=payload, create=True):
        with patch("novel_analyzer.services.reader_panel_service.build_chat_model") as mock_build:
            class _Resp:
                content = "{\"comfort_score\":82,\"personas\":[{\"persona\":\"naive_reader\",\"score\":80,\"feel\":\"好读\",\"strengths\":[],\"weaknesses\":[]},{\"persona\":\"genre_veteran\",\"score\":75,\"feel\":\"\",\"strengths\":[],\"weaknesses\":[]},{\"persona\":\"editor\",\"score\":85,\"feel\":\"\",\"strengths\":[],\"weaknesses\":[]},{\"persona\":\"prose_critic\",\"score\":78,\"feel\":\"\",\"strengths\":[],\"weaknesses\":[]}],\"dimension_scores\":[{\"dimension\":\"对话生动度\",\"score\":80,\"note\":\"\"},{\"dimension\":\"环境描写\",\"score\":75,\"note\":\"\"},{\"dimension\":\"阅读舒适度\",\"score\":85,\"note\":\"\"},{\"dimension\":\"文笔质感\",\"score\":78,\"note\":\"\"},{\"dimension\":\"悬念强度\",\"score\":80,\"note\":\"\"},{\"dimension\":\"支线管理\",\"score\":70,\"note\":\"\"},{\"dimension\":\"特色（抗平白）\",\"score\":75,\"note\":\"\"}],\"targeted_revisions\":[{\"dim\":\"支线管理\",\"action\":\"加 1 处支线伏笔\",\"priority\":3}],\"verdict\":\"polished\"}"
            mock_build.return_value.invoke.return_value = _Resp()
            rep = svc.evaluate_draft(_draft("正文" * 200))
    assert rep.comfort_score == 82
    assert rep.overall_verdict == "polished"
    assert len(rep.personas) == 4
    assert len(rep.dimension_scores) == 7


def test_needs_polish_when_priority1_revision_present() -> None:
    json_text = (
        '{"comfort_score": 75, '
        '"personas": [],'
        '"dimension_scores": [{"dimension": "对话生动度", "score": 60, "note": ""}],'
        '"targeted_revisions": [{"dim": "对话生动度", "action": "改", "priority": 1}],'
        '"verdict": "polished"}'
    )
    svc = ReaderPanelService(_settings())
    with patch("novel_analyzer.services.reader_panel_service.build_chat_model") as mock_build:
        class _Resp:
            content = json_text
        mock_build.return_value.invoke.return_value = _Resp()
        rep = svc.evaluate_draft(_draft("正文" * 200))
    assert rep.overall_verdict == "needs_polish"


def test_needs_rewrite_when_low_comfort() -> None:
    json_text = (
        '{"comfort_score": 45, '
        '"personas": [],'
        '"dimension_scores": [],'
        '"targeted_revisions": [],'
        '"verdict": "polished"}'
    )
    svc = ReaderPanelService(_settings())
    with patch("novel_analyzer.services.reader_panel_service.build_chat_model") as mock_build:
        class _Resp:
            content = json_text
        mock_build.return_value.invoke.return_value = _Resp()
        rep = svc.evaluate_draft(_draft("正文" * 200))
    assert rep.overall_verdict == "needs_rewrite"
    assert rep.comfort_score == 45


def test_needs_rewrite_when_three_dimensions_below_50() -> None:
    json_text = (
        '{"comfort_score": 72, '
        '"personas": [],'
        '"dimension_scores": ['
        '{"dimension": "对话生动度", "score": 40, "note": ""},'
        '{"dimension": "环境描写", "score": 35, "note": ""},'
        '{"dimension": "文笔质感", "score": 45, "note": ""}'
        '],'
        '"targeted_revisions": [],'
        '"verdict": "polished"}'
    )
    svc = ReaderPanelService(_settings())
    with patch("novel_analyzer.services.reader_panel_service.build_chat_model") as mock_build:
        class _Resp:
            content = json_text
        mock_build.return_value.invoke.return_value = _Resp()
        rep = svc.evaluate_draft(_draft("正文" * 200))
    assert rep.overall_verdict == "needs_rewrite"


def test_malformed_json_falls_back_safely() -> None:
    svc = ReaderPanelService(_settings())
    with patch("novel_analyzer.services.reader_panel_service.build_chat_model") as mock_build:
        class _Resp:
            content = "not valid json {"
        mock_build.return_value.invoke.return_value = _Resp()
        rep = svc.evaluate_draft(_draft("正文" * 200))
    assert rep.comfort_score == 60
    assert "parse failed" in rep.rejection_reason
    assert rep.overall_verdict == "needs_polish"


def test_unknown_persona_filtered_out() -> None:
    json_text = (
        '{"comfort_score": 70,'
        '"personas": ['
        '{"persona": "naive_reader", "score": 70, "feel": "", "strengths": [], "weaknesses": []},'
        '{"persona": "fictional_unknown_persona", "score": 99, "feel": "", "strengths": [], "weaknesses": []}'
        '],'
        '"dimension_scores": [],'
        '"targeted_revisions": [],'
        '"verdict": "polished"}'
    )
    svc = ReaderPanelService(_settings())
    with patch("novel_analyzer.services.reader_panel_service.build_chat_model") as mock_build:
        class _Resp:
            content = json_text
        mock_build.return_value.invoke.return_value = _Resp()
        rep = svc.evaluate_draft(_draft("正文" * 200))
    assert len(rep.personas) == 1
    assert rep.personas[0].persona == "naive_reader"


def test_thresholds_are_consistent() -> None:
    assert COMFORT_NEEDS_REWRITE_THRESHOLD < COMFORT_PASS_THRESHOLD
    assert 0 < COMFORT_NEEDS_REWRITE_THRESHOLD <= 100
    assert 0 < COMFORT_PASS_THRESHOLD <= 100


def test_revise_with_panel_feedback_returns_unchanged_when_no_revisions() -> None:
    from novel_analyzer.domain.schemas import ReaderPanelReport

    svc = ReaderPanelService(_settings())
    draft = _draft("正文" * 200)
    empty_report = ReaderPanelReport(
        source_chapter_index=1,
        draft_title="t",
        comfort_score=80,
        targeted_revisions=[],
    )
    out = svc.revise_with_panel_feedback(draft, empty_report)
    assert out is draft


def test_revise_with_panel_feedback_applies_when_llm_returns_valid() -> None:
    from novel_analyzer.domain.schemas import (
        ReaderPanelDimensionScore,
        ReaderPanelReport,
        ReaderPanelRevisionAction,
    )

    revised_text = "改后的正文" * 100
    json_text = (
        '{"revised_draft_text": "' + revised_text + '",'
        ' "revision_summary": ["对话生动度: 改完了", "环境描写: 加了感官"]}'
    )
    svc = ReaderPanelService(_settings())
    draft = _draft("原文" * 200)
    report = ReaderPanelReport(
        source_chapter_index=1,
        draft_title="t",
        comfort_score=55,
        dimension_scores=[
            ReaderPanelDimensionScore(dimension="对话生动度", score=40),
            ReaderPanelDimensionScore(dimension="环境描写", score=45),
        ],
        targeted_revisions=[
            ReaderPanelRevisionAction(dimension="对话生动度", action="改对话", priority=1),
        ],
    )
    with patch("novel_analyzer.services.reader_panel_service.build_chat_model") as mock_build:
        class _Resp:
            content = json_text
        mock_build.return_value.invoke.return_value = _Resp()
        out = svc.revise_with_panel_feedback(draft, report)
    assert out.draft_text == revised_text
    assert any("reader_panel revision" in n for n in out.method_notes)
    assert any("对话生动度" in n for n in out.method_notes)


def test_revise_with_panel_feedback_keeps_original_when_llm_returns_short_text() -> None:
    from novel_analyzer.domain.schemas import ReaderPanelReport, ReaderPanelRevisionAction

    json_text = '{"revised_draft_text": "太短", "revision_summary": []}'
    svc = ReaderPanelService(_settings())
    draft = _draft("原文" * 200)
    report = ReaderPanelReport(
        source_chapter_index=1,
        draft_title="t",
        comfort_score=55,
        targeted_revisions=[
            ReaderPanelRevisionAction(dimension="对话生动度", action="改", priority=1),
        ],
    )
    with patch("novel_analyzer.services.reader_panel_service.build_chat_model") as mock_build:
        class _Resp:
            content = json_text
        mock_build.return_value.invoke.return_value = _Resp()
        out = svc.revise_with_panel_feedback(draft, report)
    assert out is draft


def test_revise_with_panel_feedback_swallows_llm_exception() -> None:
    from novel_analyzer.domain.schemas import ReaderPanelReport, ReaderPanelRevisionAction

    svc = ReaderPanelService(_settings())
    draft = _draft("原文" * 200)
    report = ReaderPanelReport(
        source_chapter_index=1,
        draft_title="t",
        comfort_score=55,
        targeted_revisions=[
            ReaderPanelRevisionAction(dimension="对话生动度", action="改", priority=1),
        ],
    )
    with patch("novel_analyzer.services.reader_panel_service.build_chat_model") as mock_build:
        mock_build.return_value.invoke.side_effect = RuntimeError("provider down")
        out = svc.revise_with_panel_feedback(draft, report)
    assert out is draft
