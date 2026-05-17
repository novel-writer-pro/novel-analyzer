from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from novel_analyzer.config.settings import Settings
from novel_analyzer.services.project_plot_service import ProjectPlotService
from novel_analyzer.services.project_shell_service import ProjectShellService


def _setup_project(tmp_path: Path) -> ProjectShellService:
    shell = ProjectShellService(base_dir=tmp_path)
    shell.init("demo", source_branch_id="fake-branch")
    return shell


def _make_svc(tmp_path: Path, rag_dir: Path | None = None) -> ProjectPlotService:
    settings = MagicMock(spec=Settings)
    session = MagicMock()
    svc = ProjectPlotService(settings=settings, session=session, base_dir=tmp_path)
    svc._rag_dir = rag_dir if rag_dir is not None else tmp_path / "rag"
    return svc


def test_generate_plot_creates_files(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    svc = _make_svc(tmp_path)
    arcs, goals, cont = svc.generate_plot("demo", use_llm=False)
    assert arcs.exists()
    assert goals.exists()
    assert cont.exists()


def test_chapter_goals_format(tmp_path: Path) -> None:
    shell = _setup_project(tmp_path)
    svc = _make_svc(tmp_path)
    svc.generate_plot("demo", use_llm=False)
    body = shell.read_artifact("demo", "plot", "chapter_goals")
    lines = [ln for ln in body.splitlines() if ln.strip()]
    assert lines, "chapter_goals.md must have at least one line"
    for line in lines:
        assert re.match(r"^\d+:.{1,50}$", line), (
            f"Line does not match {{idx}}:{{goal≤50}}: {line!r}"
        )


def test_continuity_has_legacy_compat_fields(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    svc = _make_svc(tmp_path)
    _, _, cont_path = svc.generate_plot("demo", use_llm=False)
    content = cont_path.read_text(encoding="utf-8")
    for field in ("## characters", "## rules", "## unresolved_threads", "## previous_chapter_summary"):
        assert field in content, f"Missing legacy_compat field: {field!r}"


def test_arcs_has_3_arcs(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    svc = _make_svc(tmp_path)
    arcs_path, _, _ = svc.generate_plot("demo", use_llm=False)
    content = arcs_path.read_text(encoding="utf-8")
    h2_sections = re.findall(r"^## .+", content, re.MULTILINE)
    assert len(h2_sections) >= 3, f"Expected ≥3 H2 sections, got {len(h2_sections)}"


def test_generate_conflicts_creates_files(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    svc = _make_svc(tmp_path)
    axes, innov, taboo, _ = svc.generate_conflicts("demo", use_llm=False)
    assert axes.exists()
    assert innov.exists()
    assert taboo.exists()


def test_taboo_has_default_items(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    svc = _make_svc(tmp_path)
    _, _, taboo_path, _ = svc.generate_conflicts("demo", use_llm=False)
    content = taboo_path.read_text(encoding="utf-8")
    for item in ("禁止无代价系统外挂", "禁止突兀大团圆收尾", "禁止角色情绪化爆发"):
        assert item in content, f"Default taboo missing: {item!r}"


def test_axes_items_short(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    svc = _make_svc(tmp_path)
    axes_path, _, _, _ = svc.generate_conflicts("demo", use_llm=False)
    content = axes_path.read_text(encoding="utf-8")
    bullet_lines = [
        ln[2:].strip()
        for ln in content.splitlines()
        if ln.startswith("- ")
    ]
    assert bullet_lines, "axes.md must have at least one bullet item"
    for item in bullet_lines:
        assert len(item) <= 20, f"Axis item exceeds 20 chars: {item!r} ({len(item)})"


def test_conflicts_writes_rag_entry(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    rag_dir = tmp_path / "rag"
    rag_dir.mkdir()
    svc = _make_svc(tmp_path, rag_dir=rag_dir)
    _, _, _, rag_path = svc.generate_conflicts("demo", use_llm=False)
    assert rag_path is not None
    assert rag_path.exists()
    assert rag_path.name == "demo-tropes.md"
    assert rag_path.parent.name == "trope-library"
