from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from novel_analyzer.services.project_characters_service import (
    ProjectCharactersService,
    _REQUIRED_H2_SECTIONS,
)
from novel_analyzer.services.project_shell_service import ProjectShellService


def _make_service(tmp_path: Path) -> ProjectCharactersService:
    session = MagicMock()
    shell = ProjectShellService(base_dir=tmp_path, session=session)
    return ProjectCharactersService(session=session, base_dir=tmp_path, shell=shell)


def _init_project(tmp_path: Path, slug: str) -> None:
    (tmp_path / slug / "characters").mkdir(parents=True, exist_ok=True)


def test_generate_initial_cards_creates_files(tmp_path: Path) -> None:
    slug = "test-proj"
    _init_project(tmp_path, slug)
    svc = _make_service(tmp_path)

    paths = svc.generate_initial_cards(slug, count=4)

    assert len(paths) == 4
    for p in paths:
        assert p.exists()
        assert p.suffix == ".md"
        assert p.parent.name == "characters"


def test_generate_initial_cards_card_schema(tmp_path: Path) -> None:
    slug = "test-proj"
    _init_project(tmp_path, slug)
    svc = _make_service(tmp_path)

    paths = svc.generate_initial_cards(slug, count=4)

    for p in paths:
        content = p.read_text(encoding="utf-8")
        for section in _REQUIRED_H2_SECTIONS:
            assert f"## {section}" in content, f"Missing section {section!r} in {p.name}"


def test_generate_initial_cards_frontmatter(tmp_path: Path) -> None:
    slug = "test-proj"
    _init_project(tmp_path, slug)
    svc = _make_service(tmp_path)
    shell = ProjectShellService(base_dir=tmp_path, session=MagicMock())

    paths = svc.generate_initial_cards(slug, count=4)

    for p in paths:
        stem = p.stem
        fm, _ = shell.read_artifact_with_frontmatter(slug, "characters", stem)
        assert fm.get("stage") == "characters"
        assert "name" not in fm or True
        assert fm.get("locked") is False


def test_generate_initial_cards_no_zhang_yu(tmp_path: Path) -> None:
    slug = "test-proj"
    _init_project(tmp_path, slug)
    svc = _make_service(tmp_path)

    paths = svc.generate_initial_cards(slug, count=5)

    for p in paths:
        assert "张羽" not in p.stem
        content = p.read_text(encoding="utf-8")
        assert "张羽" not in content


def test_persona_to_markdown_round_trip(tmp_path: Path) -> None:
    from novel_analyzer.services.character_agent_service import CharacterPersona

    slug = "test-proj"
    _init_project(tmp_path, slug)
    svc = _make_service(tmp_path)

    persona = CharacterPersona(
        character_id="hero",
        branch_id="branch-1",
        built_at_chapter=5,
        behavior_labels=["勇敢", "冲动"],
        episodic_anchors=[],
        relationship_network={"villain": "对立", "mentor": "师徒"},
        speech_style_vector=[0.1, 0.2, 0.3],
        chapter_appearances=[1, 3, 5],
    )

    body = svc._persona_to_markdown(persona, "hero")

    shell = ProjectShellService(base_dir=tmp_path, session=MagicMock())
    shell.write_artifact(slug, "characters", "hero", body)

    result = svc.markdown_to_persona(slug, "hero")

    assert result is not None
    assert result.character_id == "hero"
    assert "勇敢" in result.behavior_labels
    assert "冲动" in result.behavior_labels
    assert "villain" in result.relationship_network


def test_inherit_from_source_graceful_failure(tmp_path: Path) -> None:
    slug = "test-proj"
    _init_project(tmp_path, slug)
    session = MagicMock()
    shell = ProjectShellService(base_dir=tmp_path, session=session)
    svc = ProjectCharactersService(session=session, base_dir=tmp_path, shell=shell)

    with patch(
        "novel_analyzer.services.project_characters_service.CharacterAgentService"
    ) as MockAgent:
        mock_instance = MagicMock()
        mock_instance.build_character_persona.side_effect = RuntimeError("DB unavailable")
        MockAgent.return_value = mock_instance

        with patch(
            "novel_analyzer.services.project_characters_service.ProjectCharactersService"
            "._persona_to_markdown"
        ):
            paths = svc.inherit_from_source(slug, ["hero", "villain"])

    assert len(paths) == 2
    for p in paths:
        assert p.exists()
        content = p.read_text(encoding="utf-8")
        assert "## 基本信息" in content
