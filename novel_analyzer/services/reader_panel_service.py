"""LLM-driven reader-panel evaluation service.

Provides a 4-persona × 7-dimension assessment of a chapter draft, complementing
the existing heuristic ReaderSimulationService. The output is structured so the
imitation harness can use ``comfort_score`` as a soft gate: drafts that pass the
score gate but score low on reader experience get flagged for revision with
concrete dimension-targeted actions.

Persona / dimension definitions live in ``novel_analyzer.llm.prompts`` so the
prompt and the schema are kept in lockstep.
"""

from __future__ import annotations

import json

from novel_analyzer.config.settings import Settings, get_settings
from novel_analyzer.domain.schemas import (
    ChapterImitationDraft,
    ReaderPanelDimensionScore,
    ReaderPanelPersonaScore,
    ReaderPanelReport,
    ReaderPanelRevisionAction,
)
from novel_analyzer.llm.client import build_chat_model
from novel_analyzer.llm.prompts import (
    READER_PANEL_DIMENSIONS,
    READER_PANEL_PERSONAS,
    build_panel_driven_revision_prompt,
    build_reader_panel_prompt,
)


COMFORT_PASS_THRESHOLD = 70
COMFORT_NEEDS_REWRITE_THRESHOLD = 60


class ReaderPanelService:
    """Evaluate a chapter draft via 4-persona × 7-dimension reader panel."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def evaluate_draft(
        self,
        draft: ChapterImitationDraft,
        *,
        target_goal: str = "",
        model_name: str | None = None,
    ) -> ReaderPanelReport:
        """Run the panel on a draft and return a structured report.

        Falls back to a deterministic safety report when the draft is too short
        to evaluate or the LLM returns malformed output - never raises so the
        harness can always read a comfort_score.
        """
        if not draft.draft_text or len(draft.draft_text) < 200:
            return self._build_fallback_report(
                draft,
                comfort_score=0,
                rejection_reason="draft too short to evaluate (< 200 chars)",
            )

        prompt = build_reader_panel_prompt(
            chapter_index=draft.source_chapter_index,
            chapter_title=draft.draft_title or draft.original_title,
            draft_text=draft.draft_text,
            target_goal=target_goal,
        )

        try:
            model = build_chat_model(self.settings, model_name=model_name)
            response = model.invoke(prompt)
            content = response.content if hasattr(response, "content") else response
            payload = self._extract_json_payload(content)
            return self._build_report_from_payload(draft, payload)
        except (json.JSONDecodeError, ValueError, KeyError) as exc:
            return self._build_fallback_report(
                draft,
                comfort_score=60,
                rejection_reason=f"reader panel parse failed: {type(exc).__name__}: {exc}",
            )
        except Exception as exc:  # noqa: BLE001
            return self._build_fallback_report(
                draft,
                comfort_score=60,
                rejection_reason=f"reader panel LLM error: {type(exc).__name__}",
            )

    def revise_with_panel_feedback(
        self,
        draft: ChapterImitationDraft,
        report: ReaderPanelReport,
        *,
        model_name: str | None = None,
    ) -> ChapterImitationDraft:
        """Use panel report's targeted_revisions to drive a one-pass revision.

        Returns the original draft unchanged when the LLM call fails or the
        response is malformed - revision is opportunistic, never blocking.
        Adds revision_summary entries to method_notes for traceability.
        """
        if not report.targeted_revisions:
            return draft

        weak_dims = [
            (d.dimension, d.score)
            for d in sorted(report.dimension_scores, key=lambda x: x.score)[:3]
        ]
        revisions_payload = [
            {"dimension": r.dimension, "action": r.action, "priority": r.priority}
            for r in report.targeted_revisions
        ]
        prompt = build_panel_driven_revision_prompt(
            chapter_title=draft.draft_title or draft.original_title,
            draft_text=draft.draft_text,
            comfort_score=report.comfort_score,
            weak_dimensions=weak_dims,
            targeted_revisions=revisions_payload,
        )

        try:
            model = build_chat_model(self.settings, model_name=model_name)
            response = model.invoke(prompt)
            content = response.content if hasattr(response, "content") else response
            payload = self._extract_json_payload(content)
        except Exception:  # noqa: BLE001
            return draft

        revised_text = payload.get("revised_draft_text") if isinstance(payload, dict) else None
        if not isinstance(revised_text, str) or len(revised_text) < 200:
            return draft

        revision_summary = payload.get("revision_summary") or []
        summary_lines = [str(s) for s in revision_summary if str(s).strip()] if isinstance(revision_summary, list) else []

        return draft.model_copy(
            update={
                "draft_text": revised_text,
                "method_notes": [
                    *draft.method_notes,
                    f"reader_panel revision: comfort={report.comfort_score} -> targeted by {len(report.targeted_revisions)} actions",
                    *[f"revision: {s}" for s in summary_lines[:5]],
                ],
            }
        )

    @staticmethod
    def _extract_json_payload(raw: object) -> dict[str, object]:
        text = str(raw).strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return json.loads(text)

    def _build_report_from_payload(
        self,
        draft: ChapterImitationDraft,
        payload: dict[str, object],
    ) -> ReaderPanelReport:
        comfort_score = self._coerce_score(payload.get("comfort_score"), default=50)

        personas: list[ReaderPanelPersonaScore] = []
        raw_personas = payload.get("personas") or []
        if isinstance(raw_personas, list):
            for item in raw_personas:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("persona") or "").strip()
                if name not in READER_PANEL_PERSONAS:
                    continue
                personas.append(
                    ReaderPanelPersonaScore(
                        persona=name,
                        score=self._coerce_score(item.get("score"), default=50),
                        feel=str(item.get("feel") or ""),
                        strengths=self._coerce_str_list(item.get("strengths")),
                        weaknesses=self._coerce_str_list(item.get("weaknesses")),
                    )
                )

        dimension_scores: list[ReaderPanelDimensionScore] = []
        raw_dims = payload.get("dimension_scores") or []
        if isinstance(raw_dims, list):
            for item in raw_dims:
                if not isinstance(item, dict):
                    continue
                dim = str(item.get("dimension") or "").strip()
                if dim not in READER_PANEL_DIMENSIONS:
                    continue
                dimension_scores.append(
                    ReaderPanelDimensionScore(
                        dimension=dim,
                        score=self._coerce_score(item.get("score"), default=50),
                        note=str(item.get("note") or ""),
                    )
                )

        revisions: list[ReaderPanelRevisionAction] = []
        raw_revs = payload.get("targeted_revisions") or []
        if isinstance(raw_revs, list):
            for item in raw_revs:
                if not isinstance(item, dict):
                    continue
                dim = str(item.get("dim") or "").strip()
                action = str(item.get("action") or "").strip()
                if not dim or not action:
                    continue
                priority = item.get("priority", 2)
                try:
                    priority_int = max(1, min(3, int(priority)))
                except (TypeError, ValueError):
                    priority_int = 2
                revisions.append(
                    ReaderPanelRevisionAction(
                        dimension=dim,
                        action=action,
                        priority=priority_int,
                    )
                )

        verdict = self._derive_verdict(comfort_score, revisions, dimension_scores)

        return ReaderPanelReport(
            source_chapter_index=draft.source_chapter_index,
            draft_title=draft.draft_title or draft.original_title,
            comfort_score=comfort_score,
            personas=personas,
            dimension_scores=dimension_scores,
            targeted_revisions=revisions,
            overall_verdict=verdict,
        )

    @staticmethod
    def _derive_verdict(
        comfort_score: int,
        revisions: list[ReaderPanelRevisionAction],
        dimension_scores: list[ReaderPanelDimensionScore],
    ) -> str:
        weak_dims = sum(1 for d in dimension_scores if d.score < 50)
        has_p1 = any(r.priority == 1 for r in revisions)
        if comfort_score < COMFORT_NEEDS_REWRITE_THRESHOLD or weak_dims >= 3:
            return "needs_rewrite"
        if comfort_score < COMFORT_PASS_THRESHOLD or has_p1:
            return "needs_polish"
        return "polished"

    @staticmethod
    def _coerce_score(value: object, *, default: int) -> int:
        try:
            return max(0, min(100, int(value)))  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _coerce_str_list(value: object) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item).strip() for item in value if str(item).strip()]

    def _build_fallback_report(
        self,
        draft: ChapterImitationDraft,
        *,
        comfort_score: int,
        rejection_reason: str,
    ) -> ReaderPanelReport:
        return ReaderPanelReport(
            source_chapter_index=draft.source_chapter_index,
            draft_title=draft.draft_title or draft.original_title,
            comfort_score=comfort_score,
            personas=[],
            dimension_scores=[],
            targeted_revisions=[],
            overall_verdict="needs_polish" if comfort_score >= COMFORT_NEEDS_REWRITE_THRESHOLD else "needs_rewrite",
            rejection_reason=rejection_reason,
        )
