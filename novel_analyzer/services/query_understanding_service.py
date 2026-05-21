"""Structured query understanding for branch QA.

Stage C1 intentionally starts with a deterministic parser so the new contract can
be introduced without coupling QA correctness to an additional LLM call.
"""

from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from novel_analyzer.database.models import GraphNode
from novel_analyzer.domain.schemas import (
    PlannedEntity,
    QueryConstraints,
    QueryTimeScope,
    RetrievalPreferences,
    StructuredQueryPlan,
)
from novel_analyzer.services.entity_resolution_service import EntityResolutionService


class QueryUnderstandingService:
    """Build a lightweight structured query plan for branch QA."""

    QUESTION_TYPE_KEYWORDS: dict[str, tuple[str, ...]] = {
        "relation": ("关系", "师徒", "敌对", "联盟", "亲近", "疏远", "和谁"),
        "world_rule": ("规则", "设定", "为什么不能", "限制", "门槛", "世界"),
        "foreshadow": ("伏笔", "暗示", "预示", "埋下", "兑现", "回收"),
        "timeline": ("什么时候", "先后", "顺序", "前", "主线", "推进", "经过"),
        "character_state": ("动机", "态度", "想法", "决定", "为什么要", "状态"),
        "causal_why": ("为什么", "原因", "导致", "为何"),
    }

    INTENT_BY_QUESTION_TYPE: dict[str, str] = {
        "relation": "trace_change",
        "world_rule": "identify_rule",
        "foreshadow": "resolve_foreshadow",
        "timeline": "summarize_arc",
        "character_state": "explain_reason",
        "causal_why": "explain_reason",
        "general": "locate_fact",
    }

    ANSWER_EXPECTATION_BY_QUESTION_TYPE: dict[str, str] = {
        "relation": "relation_trace",
        "world_rule": "rule_explanation",
        "foreshadow": "foreshadow_resolution",
        "timeline": "timeline_summary",
        "character_state": "multi_chapter_explanation",
        "causal_why": "multi_chapter_explanation",
        "general": "direct_fact",
    }

    def __init__(self, session: Session) -> None:
        self.session = session
        self.entity_resolution = EntityResolutionService(session)

    def build_query_plan(
        self,
        branch_id: str,
        question: str,
        *,
        max_chapter: int | None = None,
    ) -> StructuredQueryPlan:
        normalized = question.strip()
        question_type = self._classify_question_type(normalized)
        time_scope = self._extract_time_scope(normalized, max_chapter=max_chapter)
        entities = self._extract_entities(branch_id, normalized)
        constraints = QueryConstraints(
            anti_spoiler=time_scope.strict_upper_bound or max_chapter is not None,
            must_cite_evidence=True,
            prefer_multi_hop=question_type in {"relation", "timeline", "foreshadow", "causal_why"},
            allow_conservative_answer=True,
        )
        retrieval_plan = self._build_retrieval_preferences(question_type)
        return StructuredQueryPlan(
            raw_question=question,
            normalized_question=normalized,
            question_type=question_type,
            intent=self.INTENT_BY_QUESTION_TYPE.get(question_type, "locate_fact"),
            answer_expectation=self.ANSWER_EXPECTATION_BY_QUESTION_TYPE.get(question_type, "direct_fact"),
            entities=entities,
            time_scope=time_scope,
            constraints=constraints,
            retrieval_plan=retrieval_plan,
            diagnostic_notes=self._diagnostic_notes(time_scope, entities, max_chapter=max_chapter),
        )

    @classmethod
    def _classify_question_type(cls, question: str) -> str:
        for question_type in ("relation", "world_rule", "foreshadow", "timeline", "character_state", "causal_why"):
            if any(keyword in question for keyword in cls.QUESTION_TYPE_KEYWORDS[question_type]):
                return question_type
        return "general"

    @staticmethod
    def _extract_time_scope(question: str, *, max_chapter: int | None = None) -> QueryTimeScope:
        front_match = re.search(r"前\s*(\d+)\s*章", question)
        if front_match:
            upper = int(front_match.group(1))
            return QueryTimeScope(
                mode="bounded_range",
                chapter_start=1,
                chapter_end=upper,
                strict_upper_bound=True,
            )

        range_match = re.search(r"第\s*(\d+)\s*章\s*(?:到|至|-)\s*第?\s*(\d+)\s*章", question)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2))
            return QueryTimeScope(
                mode="bounded_range",
                chapter_start=min(start, end),
                chapter_end=max(start, end),
                strict_upper_bound=True,
            )

        single_match = re.search(r"第\s*(\d+)\s*章", question)
        if single_match:
            chapter = int(single_match.group(1))
            return QueryTimeScope(
                mode="single_chapter",
                chapter_start=chapter,
                chapter_end=chapter,
                strict_upper_bound=True,
            )

        if max_chapter is not None:
            return QueryTimeScope(
                mode="bounded_range",
                chapter_start=1,
                chapter_end=max_chapter,
                strict_upper_bound=True,
            )

        return QueryTimeScope()

    def _extract_entities(self, branch_id: str, question: str) -> list[PlannedEntity]:
        alias_map = self.entity_resolution.build_alias_map(branch_id)
        node_rows = self.session.scalars(
            select(GraphNode)
            .where(GraphNode.branch_id == branch_id)
            .where(GraphNode.node_type.in_(("entity", "character", "world_rule")))
            .order_by(GraphNode.occurrence_count.desc(), GraphNode.label.asc())
        ).all()

        matches: list[PlannedEntity] = []
        seen: set[tuple[str, str]] = set()
        ordered_labels = sorted(
            {node.label for node in node_rows if node.label and len(node.label) >= 2},
            key=len,
            reverse=True,
        )
        for label in ordered_labels:
            if label not in question:
                continue
            canonical = alias_map.get(label, label)
            key = (label, canonical)
            if key in seen:
                continue
            seen.add(key)
            matches.append(
                PlannedEntity(
                    surface=label,
                    canonical=canonical,
                    entity_type="world_rule" if any(
                        node.label == label and node.node_type == "world_rule" for node in node_rows
                    ) else "entity",
                    confidence=0.9 if canonical == label else 0.95,
                )
            )

        for alias, canonical in alias_map.items():
            if alias not in question:
                continue
            key = (alias, canonical)
            if key in seen:
                continue
            seen.add(key)
            matches.append(
                PlannedEntity(
                    surface=alias,
                    canonical=canonical,
                    entity_type="entity",
                    confidence=0.95,
                )
            )

        deduped: dict[str, PlannedEntity] = {}
        for item in matches:
            deduped.setdefault(item.canonical, item)
        return list(deduped.values())

    @staticmethod
    def _build_retrieval_preferences(question_type: str) -> RetrievalPreferences:
        return RetrievalPreferences(
            prefer_graph=question_type in {"relation", "world_rule", "foreshadow"},
            prefer_timeline=question_type == "timeline",
            prefer_window=question_type in {"timeline", "causal_why", "character_state"},
            prefer_causal=question_type in {"timeline", "causal_why", "character_state"},
            prefer_foreshadow=question_type == "foreshadow",
        )

    @staticmethod
    def _diagnostic_notes(
        time_scope: QueryTimeScope,
        entities: list[PlannedEntity],
        *,
        max_chapter: int | None = None,
    ) -> list[str]:
        notes: list[str] = []
        if entities:
            notes.append(f"matched_entities={','.join(item.canonical for item in entities)}")
        if time_scope.strict_upper_bound and time_scope.chapter_end is not None:
            notes.append(f"time_scope<=chapter_{time_scope.chapter_end}")
        if max_chapter is not None:
            notes.append(f"max_chapter={max_chapter}")
        return notes
