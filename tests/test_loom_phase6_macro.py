from __future__ import annotations

import json
import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from novel_analyzer.config.settings import Settings
from novel_analyzer.services.project_macro_service import (
    ProjectMacroService,
    _SOURCE_NOVEL_BANNED,
)
from novel_analyzer.services.project_shell_service import ProjectShellService


def _setup_project(tmp_path: Path) -> ProjectShellService:
    shell = ProjectShellService(base_dir=tmp_path)
    shell.init("demo", source_branch_id="fake-branch")
    return shell


def _make_svc(tmp_path: Path) -> ProjectMacroService:
    settings = MagicMock(spec=Settings)
    session = MagicMock()
    svc = ProjectMacroService(settings=settings, session=session, base_dir=tmp_path)
    svc._rag_dir = tmp_path / "rag"
    return svc


def test_generate_no_llm_creates_files(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    svc = _make_svc(tmp_path)
    premise_path, world_path, _rag = svc.generate("demo", use_llm=False)
    assert premise_path.exists()
    assert world_path.exists()


def test_generate_premise_has_5_sections(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    svc = _make_svc(tmp_path)
    premise_path, _world, _rag = svc.generate("demo", use_llm=False)
    content = premise_path.read_text(encoding="utf-8")
    h2_sections = re.findall(r"^## .+", content, re.MULTILINE)
    assert len(h2_sections) == 5


def test_generate_world_has_6_sections(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    svc = _make_svc(tmp_path)
    _premise, world_path, _rag = svc.generate("demo", use_llm=False)
    content = world_path.read_text(encoding="utf-8")
    h2_sections = re.findall(r"^## .+", content, re.MULTILINE)
    assert len(h2_sections) == 6


def test_generate_no_zhang_yu_in_template(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    svc = _make_svc(tmp_path)
    premise_path, world_path, _rag = svc.generate("demo", use_llm=False)
    for path in (premise_path, world_path):
        content = path.read_text(encoding="utf-8")
        for noun in _SOURCE_NOVEL_BANNED:
            assert noun not in content, f"Banned noun {noun!r} found in {path.name}"
    assert "[请填写]" in premise_path.read_text(encoding="utf-8")
    assert "[请填写]" in world_path.read_text(encoding="utf-8")


def test_revise_creates_v2(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    svc = _make_svc(tmp_path)
    svc.generate("demo", use_llm=False)

    shell = ProjectShellService(base_dir=tmp_path)
    premise_path, world_path = svc.revise("demo", feedback="调整调性为更轻松", use_llm=False)

    fm_p, _ = shell.read_artifact_with_frontmatter("demo", "macro", "premise")
    fm_w, _ = shell.read_artifact_with_frontmatter("demo", "macro", "world")
    assert int(fm_p.get("version", 0)) == 2  # type: ignore[call-overload]
    assert int(fm_w.get("version", 0)) == 2  # type: ignore[call-overload]

    runs_dir = tmp_path / "demo" / "runs"
    archived = list(runs_dir.rglob("premise.md"))
    assert len(archived) >= 1


def test_generate_with_llm_filters_banned_nouns(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    settings = MagicMock(spec=Settings)
    session = MagicMock()
    svc = ProjectMacroService(settings=settings, session=session, base_dir=tmp_path)
    svc._rag_dir = tmp_path / "rag"

    llm_json = json.dumps(
        {
            "premise": {
                "题材": "箓书世界的故事",
                "主旨": "万民部的权力",
                "调性": "讽刺",
                "核心讽刺引擎": "昆墟体制",
                "与范本的相似/差异轴": "张羽式主角",
            },
            "world": {
                "世界观底座": "白真真的世界",
                "力量体系": "张翩翩体系",
                "经济与权力结构": "玉星寒经济",
                "现代映射": "宋海龙映射",
                "规则": ["周澈尘规则"],
                "名词映射": [{"原": "赵天行", "新": "新名"}],
            },
        },
        ensure_ascii=False,
    )

    mock_message = MagicMock()
    mock_message.content = llm_json
    mock_model = MagicMock()
    mock_model.invoke.return_value = mock_message

    with patch(
        "novel_analyzer.llm.client.build_chat_model",
        return_value=mock_model,
    ):
        premise_path, world_path, _rag = svc.generate("demo", use_llm=True)

    for path in (premise_path, world_path):
        content = path.read_text(encoding="utf-8")
        for noun in _SOURCE_NOVEL_BANNED:
            assert noun not in content, f"Banned noun {noun!r} leaked into {path.name}"


def test_generate_writes_rag_entry(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    svc = _make_svc(tmp_path)
    rag_dir = tmp_path / "rag"
    rag_dir.mkdir()
    svc._rag_dir = rag_dir

    _premise, _world, rag_path = svc.generate("demo", use_llm=False)

    assert rag_path is not None
    assert rag_path.exists()
    assert rag_path.name == "demo-worldview.md"
    assert rag_path.parent.name == "worldview-dossiers"
