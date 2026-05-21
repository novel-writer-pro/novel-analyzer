from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from novel_analyzer.database.models import GraphNode
from novel_analyzer.database.session import create_schema
from novel_analyzer.services.entity_resolution_service import EntityResolutionService
from novel_analyzer.services.ingest_service import IngestService
from novel_analyzer.services.run_service import RunService


def _session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    create_schema(engine)
    return Session(engine)


def test_entity_resolution_supports_entity_nodes_for_alias_lookup(tmp_path: Path) -> None:
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
                    chapter_last_seen=3,
                    occurrence_count=5,
                    metadata_json={},
                ),
                GraphNode(
                    branch_id=branch.id,
                    node_type="entity",
                    label="卫图少年",
                    chapter_first_seen=1,
                    chapter_last_seen=2,
                    occurrence_count=2,
                    metadata_json={},
                ),
            ]
        )
        session.commit()

        service = EntityResolutionService(session)
        alias_map = service.build_alias_map(branch.id)

        assert alias_map["卫图少年"] == "卫图"
        assert service.resolve_canonical(branch.id, "卫图少年") == "卫图"
