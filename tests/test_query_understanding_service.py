from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from novel_analyzer.database.models import GraphNode
from novel_analyzer.database.session import create_schema
from novel_analyzer.services.ingest_service import IngestService
from novel_analyzer.services.query_understanding_service import QueryUnderstandingService
from novel_analyzer.services.run_service import RunService


def _session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    create_schema(engine)
    return Session(engine)


def test_query_understanding_builds_timeline_plan_with_time_scope(tmp_path: Path) -> None:
    novel_path = tmp_path / "novel.txt"
    novel_path.write_text("第1章 一\n正文\n", encoding="utf-8")

    with _session() as session:
        novel, manifest = IngestService(session).ingest_text_file(str(novel_path), "样例")
        _, branch = RunService(session).create_run(novel.id, manifest.id)
        session.add(
            GraphNode(
                branch_id=branch.id,
                node_type="entity",
                label="卫图",
                chapter_first_seen=1,
                chapter_last_seen=20,
                occurrence_count=10,
                metadata_json={},
            )
        )
        session.commit()

        plan = QueryUnderstandingService(session).build_query_plan(
            branch.id,
            "卫图前20章的推进主线是什么？",
        )

        assert plan.question_type == "timeline"
        assert plan.intent == "summarize_arc"
        assert plan.time_scope.chapter_start == 1
        assert plan.time_scope.chapter_end == 20
        assert plan.constraints.anti_spoiler is True
        assert plan.retrieval_plan.prefer_timeline is True
        assert plan.entities[0].canonical == "卫图"


def test_query_understanding_resolves_alias_to_canonical_entity(tmp_path: Path) -> None:
    novel_path = tmp_path / "novel.txt"
    novel_path.write_text("第1章 一\n正文\n", encoding="utf-8")

    with _session() as session:
        novel, manifest = IngestService(session).ingest_text_file(str(novel_path), "样例")
        _, branch = RunService(session).create_run(novel.id, manifest.id)
        session.add_all(
            [
                GraphNode(
                    branch_id=branch.id,
                    node_type="entity",
                    label="卫图",
                    chapter_first_seen=1,
                    chapter_last_seen=12,
                    occurrence_count=12,
                    metadata_json={},
                ),
                GraphNode(
                    branch_id=branch.id,
                    node_type="entity",
                    label="卫图少年",
                    chapter_first_seen=1,
                    chapter_last_seen=6,
                    occurrence_count=3,
                    metadata_json={},
                ),
            ]
        )
        session.commit()

        plan = QueryUnderstandingService(session).build_query_plan(
            branch.id,
            "卫图少年为什么要修养生功？",
        )

        assert plan.question_type == "character_state"
        assert [item.canonical for item in plan.entities] == ["卫图"]
        assert plan.retrieval_plan.prefer_causal is True
